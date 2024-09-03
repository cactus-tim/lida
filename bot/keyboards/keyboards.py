from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_ikb() -> InlineKeyboardMarkup:
    ikb = [
        [InlineKeyboardButton(text="Начать заполнять данные", callback_data="data")],
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def get_data_ikb() -> InlineKeyboardMarkup:
    ikb = [
        [InlineKeyboardButton(text="Поехали", callback_data="quest")],
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard