# main.py

import asyncio
from logger import setup_logger
from bot import connect_to_bot

setup_logger()


async def main():
    while True:
        try:
            await connect_to_bot()
        except Exception as e:
            print(f"连接失败，正在重试: {e}")
            await asyncio.sleep(1)  # 每秒重试一次


if __name__ == "__main__":
    asyncio.run(main())
