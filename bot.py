
import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import router


load_dotenv(dotenv_path=".env", override=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Не найден BOT_TOKEN в файле .env")


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
