import json
import asyncio
from typing import TYPE_CHECKING, Final
from asyncio import Queue
from pathlib import Path

from bilibili_api import Credential
from bilibili_api.session import Session, EventType, send_msg
from loguru import logger


if TYPE_CHECKING:
    from loguru import Logger


__all__ = [
    'CREDENTIAL',
    'URL_QUEUE',
    'LOGGER',
    'TARGET_UID',
    'SELF_UID',
    'SESSION',
    'MESSAGE_QUEUE',
    'URL_QUEUE',
    'DONE',
    'SEND_MSG_TASK',
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

SELF_UID = int(getattr(CREDENTIAL, 'DedeUserID', 0))

assert SELF_UID, '请先登录账号'

URL_QUEUE: Final[Queue[str]] = Queue(maxsize=0x10)
'''
快手分享链接的队列

生产者：读取私信中的快手视频分享链接

消费者：下载视频到本地
'''

MESSAGE_QUEUE: Final[Queue[str]] = Queue()


async def _send_msg_task():
    while True:
        message = await MESSAGE_QUEUE.get()
        await send_msg(
            CREDENTIAL,
            TARGET_UID,
            EventType.TEXT,
            message
        )
        MESSAGE_QUEUE.task_done()

async def _done():
    await asyncio.gather(
        URL_QUEUE.join(),
        MESSAGE_QUEUE.join()
    )

DONE = _done()

class _BiliLogger:
    """
    注：该class并未继承loguru.Logger，
    只是把所有访问接口都委托给了loguru，因此在存根文件中写了继承。
    
    虽然此举会造成实际执行逻辑与存根文件不匹配，
    但是可以把类型注解委托给loguru.Logger的同时不显式继承。
    """
    
    __slots__ = ('_logger',)
    
    def __init__(self, logger: 'Logger'):
        self._logger = logger
        self._logger.level(
            'BILI',
            no=25,
            color='<light-magenta>',
        )
    
    def bili(self, message: str):
        """将logger内容发送到b站私信"""
        self._logger.log('BILI', message)
        MESSAGE_QUEUE.put_nowait(message)
    
    def __getattr__(self, name):
        # 委托所有其他属性到原 logger
        return getattr(self._logger, name)

type BiliLogger = _BiliLogger

SEND_MSG_TASK = _send_msg_task()

LOGGER: Final[BiliLogger] = _BiliLogger(logger)
