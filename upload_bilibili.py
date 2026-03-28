from pathlib import Path
import asyncio

import aiofiles
import yaml
import cv2
from bilibili_api.video_uploader import (
    VideoUploader,
    VideoMeta,
    VideoUploaderPage,
)

from consts import *


def extract_cover(video_path: Path) -> Path:
    cover_path = video_path.parent / f"{video_path.stem}.jpg"
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"无法打开视频文件: {video_path}")
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise RuntimeError(f"无法读取视频帧: {video_path}")
    
    cv2.imwrite('cover.jpg', frame)
    return cover_path


def config2meta(raw_config: dict) -> VideoMeta:
    assert 'title' in raw_config, "Title not found in config."
    tags_txt: str = str(raw_config.get('tags', '抽象'))
    tags = tags_txt.split('，')
    return VideoMeta(
        tid=int(raw_config.get('tid', 138)),
        title=raw_config['title'],
        desc=raw_config.get('desc', ''),
        tags=tags,
        cover=raw_config.get('cover', 'cover.jpg'),
    )


async def upload_video(
    video_path: Path | str,
) -> bool:
    if not isinstance(video_path, Path):
        video_path = Path(video_path)
    video_path = Path() / 'videos' / video_path.name
    config_path = video_path.parent / f"{video_path.stem}.yaml"
    flag_path = video_path.parent / f"{video_path.stem}.flag"
    if flag_path.exists():
        return False
    if not config_path.exists():
        return False
    if not video_path.exists():
        return False
    extract_cover(video_path)
    async with aiofiles.open(config_path, "r", encoding="utf-8") as f:
        config: dict = yaml.safe_load(await f.read())
    if not config:
        return False
    vu_meta = config2meta(config)
    
    try:
        await vu_meta.verify(credential=CREDENTIAL)
    except Exception as e:
        LOGGER.error(f"Verify video meta failed: {e}")
        return False
    page = VideoUploaderPage(
        path=str(video_path),
        title=config['title'],
        description=config.get('desc', ''),
    )
    uploader = VideoUploader(
        [page], vu_meta, CREDENTIAL
    )
    @uploader.on("__ALL__")
    async def ev(data):
        LOGGER.info("上传事件详情：", data)  # 会输出具体错误描述
        
    await uploader.start()
    flag_path.touch()
    LOGGER.bili(f'成功上传视频: {video_path}')
    return True


async def video_uploader():
    while True:
        # LOGGER.info('轮循检测所有视频')
        for video_path in Path().glob('videos/*.mp4'):
            success = await upload_video(video_path)
            if success:
                LOGGER.info(f"Upload video {video_path} success.")
        await asyncio.sleep(5)


TASK = video_uploader()

# video_path = "Jq4FVpUc.mp4"
video_path = 'KiD2EAuL.mp4'

async def main():
    await upload_video(video_path)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
    # sync(upload_video(video_path))
