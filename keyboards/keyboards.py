from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


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


def get_mail_ikb_full() -> InlineKeyboardMarkup:
    ikb = [
        [InlineKeyboardButton(text="ДА", callback_data="send")],
        [InlineKeyboardButton(text="Нет, мне не нравится компания", callback_data="company_reject_by_user")],
        [InlineKeyboardButton(text="Нет, мне не нравится письмо", callback_data="mail_reject_by_user")],
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def get_mail_ikb() -> InlineKeyboardMarkup:
    ikb = [
        [InlineKeyboardButton(text="Да", callback_data="send")],
        [InlineKeyboardButton(text="Нет, мне не нравится компания", callback_data="company_reject_by_user")],
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard
