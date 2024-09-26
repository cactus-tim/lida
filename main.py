import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot_instance import bot
from confige import BotConfig
from database.parse_company import csv_to_db
from handlers import user, questionary_ai, mail, error
from mails.mail_sender import loop

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta


from database.models import async_main


def register_routers(dp: Dispatcher) -> None:
    """Registers routers"""
    dp.include_routers(user.router, questionary_ai.router, mail.router, error.router)


async def main() -> None:
    """Entry point of the program."""

    await async_main()

    config = BotConfig(
        admin_ids=[52786051],
        welcome_message="Привет! Я AI Saler, помогаю B2B-компаниям увеличивать продажи с помощью искусственного интеллекта. \n\n <b>Давай начнем!</b>"
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp["config"] = config

    register_routers(dp)

    # await csv_to_db()

    scheduler = AsyncIOScheduler()

    scheduler.add_job(loop, 'interval', hours=24, start_date=datetime.now() + timedelta(seconds=5),
                      id='loop')

    try:
        # scheduler.start()
        await loop()
        await dp.start_polling(bot, skip_updates=True)
    except Exception as _ex:
        print(f'Exception: {_ex}')


if __name__ == '__main__':
    asyncio.run(main())
