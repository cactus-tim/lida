import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot_instance import bot
from confige import BotConfig
# from handlers import user_handlers, questionnaire_handlers, rc_handlers

from database.models import async_main
from datetime import datetime, timedelta


def register_routers(dp: Dispatcher) -> None:
    """Registers routers"""
    dp.include_routers(user_handlers.router, questionnaire_handlers.router, rc_handlers.router)


async def main() -> None:
    """Entry point of the program."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    await async_main()

    config = BotConfig(
        admin_ids=[52786051],
        welcome_message="Привет! Я AI Saler, помогаю B2B-компаниям увеличивать продажи с помощью искусственного интеллекта. \n\n <b>Давай начнем!</b>"
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp["config"] = config

    register_routers(dp)

    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as _ex:
        print(f'Exception: {_ex}')


if __name__ == '__main__':
    asyncio.run(main())
