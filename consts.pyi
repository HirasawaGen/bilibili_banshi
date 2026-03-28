from typing import Final
from types import CoroutineType
from asyncio import Queue

from bilibili_api import Credential
from bilibili_api.session import Session
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

class BiliLogger(Logger):
    """
    注：该class并未继承loguru.Logger，
    只是把所有访问接口都委托给了loguru，因此在存根文件中写了继承。
    
    虽然此举会造成实际执行逻辑与存根文件不匹配，
    但是可以把类型注解委托给loguru.Logger的同时不显式继承。
    """
    def bili(self, message: str) -> None: ...

CREDENTIAL: Final[Credential]
SESSION: Final[Session]
URL_QUEUE: Final[Queue[str]]
MESSAGE_QUEUE: Final[Queue[str]]
LOGGER: Final[BiliLogger]
TARGET_UID: Final[int]
SELF_UID: Final[int]
DONE: Final[CoroutineType[None, None, None]]
SEND_MSG_TASK: Final[CoroutineType[None, None, None]]
