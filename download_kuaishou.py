from pathlib import Path
import re

from aiohttp import ClientSession
from aiolimiter import AsyncLimiter
import aiofiles

from consts import *


LIMITER = AsyncLimiter(1, 1)

PATTERN = re.compile(r'https?:\/\/[^\s"]+?\.mp4')

FORBIDDEN_DOMAINS: list[str] = [
    'v4.oskwai.com',
    'v23-3.kwaicdn.com',
]


async def download_kuaishou_video(
    session: ClientSession,
    url: str,
    video_path: Path | str | None = None,
    chunk_size: int = 1024 * 1024,
    force: bool = False,
    download_html: bool = False,
) -> Path | None:
    if not 'v.kuaishou.com' in url:
        LOGGER.error(f"Unsupported url: {url}")
        return None
    if video_path is None:
        video_path = Path(url.split('/')[-1] + '.mp4')
    if isinstance(video_path, str):
        video_path = Path(video_path)
    video_path = Path() / 'videos' / video_path.name
    (video_path.parent / f'{video_path.stem}.yaml').touch(exist_ok=True)
    exists = video_path.exists()
    if exists:
        if not force:
            LOGGER.warning(f"Video already downloaded to: {video_path}, skip downloading")
            return video_path
        LOGGER.warning(f"Video already downloaded to: {video_path}, overwrite it")
    async with (
        LIMITER,
        session.get(url) as resp,
        # aiofiles.open(video_path, 'wb') as f,
    ):
        if resp.status != 200:
            LOGGER.error(f"Failed to download video from {url}, status code: {resp.status}")
            return None
        html_content = await resp.text()
        # for debug
        if download_html:
            async with aiofiles.open(video_path.with_suffix('.html'), 'w', encoding='utf-8') as f:
                await f.write(html_content)
        video_urls: list[str] = PATTERN.findall(html_content)
    video_urls = [
        video_url
        for video_url in video_urls
        if 'bs2/photo-video-mz' not in video_url
    ]
    LOGGER.info(f'all video urls: {video_urls}')
    flag = False
    for video_url in video_urls:
        if any(
            forbidden_domain in video_url
            for forbidden_domain
            in FORBIDDEN_DOMAINS
        ):
            continue
        async with (
            LIMITER,
            aiofiles.open(video_path, 'wb') as f,
            session.get(video_url) as resp,
        ):
            if resp.status == 403:
                LOGGER.error(f"Failed to download video from {video_url}, status code: {resp.status}")
                FORBIDDEN_DOMAINS.append(video_url.split('/')[2])
                continue
            if resp.status != 200:
                LOGGER.error(f"Failed to download video from {video_url}, status code: {resp.status}")
                continue
            if resp.content_type != 'video/mp4':
                LOGGER.error(f"Failed to download video from {video_url}, content type: {resp.content_type}")
                continue
            LOGGER.info(f"Downloading video from {video_url} to {video_path}")
            while True:
                chunk = await resp.content.read(chunk_size)
                if not chunk:
                    break
                await f.write(chunk)
            flag = True
            break
    if not flag:
        LOGGER.error(f"Failed to download video from {url}")
        if not exists:  # avoid deleting the file if it was already downloaded
            video_path.unlink(missing_ok=True)
        return None
    # LOGGER.info(f"Video downloaded to {video_path}")
    LOGGER.success(f'成功下载视频: {video_path}')
    return video_path
    

async def kuaishou_downloader():
    async with ClientSession() as session:
        while True:
            url = await URL_QUEUE.get()
            if url is None:
                break
            video_path = await download_kuaishou_video(session, url, force=True)
            URL_QUEUE.task_done()
            if video_path is None:
                LOGGER.error(f"Failed to download video: {url}")
                continue
            LOGGER.info(f"Downloaded video: {video_path}")


# async def main():
#     async with ClientSession() as session:
#         url = 'https://v.kuaishou.com/Jq4FVpUc'
#         video_path = await download_kuaishou_video(session, url, force=True)
        
        
# if __name__ == '__main__':
#     asyncio.run(main())


TASK = kuaishou_downloader()
