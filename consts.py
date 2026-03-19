import json
from typing import TYPE_CHECKING, Final
from asyncio import Queue
from pathlib import Path

from bilibili_api import Credential, sync
from bilibili_api.session import Session, EventType, send_msg
from loguru import logger as LOGGER


if TYPE_CHECKING:
    from loguru import Message


__all__ = [
    'CREDENTIAL',
    'URL_QUEUE',
    'LOGGER',
    'TARGET_UID',
    'SELF_UID'
]


_TARGET_PATH: Final[Path] = Path('target.txt')
_COOKIES_PATH: Final[Path] = Path('cookies.json')

assert _TARGET_PATH.exists(), '请先配置target.txt文件'
assert _COOKIES_PATH.exists(), '请先配置cookies.json文件'


with open(_TARGET_PATH, 'r') as f:
    TARGET_UID: Final[int] = int(f.read().strip())
    

with open(_COOKIES_PATH, 'r') as f:
    _cookies = json.load(f)
_cookies['sessdata'] = _cookies['SESSDATA']

CREDENTIAL: Final[Credential] = Credential(**_cookies)

SESSION: Final[Session] = Session(CREDENTIAL)

URL_QUEUE: Final[Queue[str]] = Queue(maxsize=0x10)
'''
快手分享链接的队列

生产者：读取私信中的快手视频分享链接

消费者：下载视频到本地
'''

SELF_UID = int(getattr(CREDENTIAL, 'DedeUserID', 0))

assert SELF_UID, '请先登录账号'


def _success_sink(msg: 'Message'):
    coro = send_msg(
        CREDENTIAL,
        TARGET_UID,
        EventType.TEXT,
        msg.record['message']
    )
    sync(coro)
    
LOGGER.add(_success_sink, level='SUCCESS')

