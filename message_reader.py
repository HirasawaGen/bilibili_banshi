from math import e
from pathlib import Path
from typing import Final
import re

from bilibili_api.session import Event, EventType, Session
import aiofiles
import yaml

from consts import *


SESSION: Final[Session] = Session(CREDENTIAL)


PATTERNS: Final[dict[str, re.Pattern]] = {
    '快手': re.compile(r'https://v\.kuaishou\.com/[a-zA-Z0-9]+'),
}

last_url: str = ''


async def set_title(title: str):
    name = last_url.split('/')[-1]
    config_path = Path(f'./videos/{name}.yaml')
    if config_path.exists():
        async with aiofiles.open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(await f.read())
    else:
        config = {}
    if not config:
        config = {}
    config['title'] = title
    async with aiofiles.open(config_path, 'w', encoding='utf-8') as f:
        await f.write(yaml.dump(config))


@SESSION.on(EventType.TEXT)
async def _on_text(event: Event):
    if not event.sender_uid == TARGET_UID:
        return
    if not isinstance(event.content, str):
        return
    content = event.content.strip()
    if content == 'test':
        LOGGER.success('test')
    name = ''
    url = ''
    for name_, pattern in PATTERNS.items():
        match = pattern.search(content)
        if not match:
            continue
        name = name_
        url = match.group(0)
        break
    if url:
        global last_url
        last_url = url
        LOGGER.info(f"Received a url from `{name}`: {url}")
        await URL_QUEUE.put(url)
    elif ':' in content:  # yaml
        try:
            config = yaml.safe_load(content)
        except yaml.YAMLError:
            return
        name = last_url.split('/')[-1]
        config_path = Path(f'./videos/{name}.yaml')
        async with aiofiles.open(config_path, 'w', encoding='utf-8') as f:
            await f.write(yaml.dump(config))
        LOGGER.info(f"Received a config from `{name}`: {config}")


TASK: Final = SESSION.start()
