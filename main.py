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
    )


if __name__ == '__main__':
    try:
        LOGGER.success('初始化成功')
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.warning('KeyboardInterrupt')
        LOGGER.success('退出成功')
    except Exception as e:
        LOGGER.error(e)
        LOGGER.success(f'异常失败，错误信息：\n{e}')
        
