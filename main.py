import asyncio

import message_reader
import download_kuaishou
import upload_bilibili

from consts import *


async def main():
    await asyncio.gather(
        message_reader.TASK,
        download_kuaishou.TASK,
        upload_bilibili.TASK,
        SEND_MSG_TASK,
    )


if __name__ == '__main__':
    try:
        LOGGER.bili('程序启动')
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.warning('KeyboardInterrupt')
    except Exception as e:
        LOGGER.error(e)
        LOGGER.bili(f'异常失败，错误信息：\n{e}')
    finally:
        asyncio.run(DONE)
        LOGGER.bili('程序结束')