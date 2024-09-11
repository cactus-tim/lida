from aiogram import Bot
from aiogram.enums import ParseMode
import os
from dotenv import load_dotenv
import sys
from aiogram.client.bot import DefaultBotProperties

sys.path.append(os.path.join(sys.path[0], 'lida'))

load_dotenv('.env')
token = os.getenv('TOKEN_API_TG')
SQL_URL_RC = (f'postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}'
              f'@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}')

bot = Bot(
    token=token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)
