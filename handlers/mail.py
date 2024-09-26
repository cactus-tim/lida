from aiogram import Router, F, types
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramUnauthorizedError, TelegramNetworkError
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from gpt.gpt_parsers import parse_user_data, parse_product_data, parse_edits_data, parse_company_data, \
    parse_target_company_scope, parse_target_company_employe, parse_target_company_age, parse_target_company_money, \
    parse_target_company_jobtitle
from database.req import create_user, update_user, update_user_x_row_by_id, update_user_x_row_by_status, get_user, \
    get_user_x_row_by_status, get_all_rows_by_user
from keyboards.keyboards import get_data_ikb, get_mail_ikb
from mails.mail_sender import mail_start, send_mail, get_latest_email_by_sender
from gpt.gpt_parsers import make_mail, make_mail_lpr, parse_email_data, parse_email_data_bin
from bot_instance import logger, bot
from handlers.error import safe_send_message

from database.req import get_company_by_id, update_company_by_id
import asyncio

# from database import requests as rq

router = Router()


@router.callback_query(F.data == "send")
async def cmd_send(callback: F.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = await get_user_x_row_by_status(callback.from_user.id, "requested")
    company = await get_company_by_id(row.company_id)
    theme = row.comment['theme']
    text = row.comment['text']
    await send_mail(theme, text, company.company_mail)
    user = await get_user(callback.from_user.id)
    await update_user(callback.from_user.id, {'cnt': user.cnt + 1})
    await update_user_x_row_by_status(callback.from_user.id, 'requested', {'status': "waiting_rpl_ans"})
    # await update_user_x_row_by_status(callback.from_user.id, 'requested', {'status': "waiting_rpl_contact"})
    await mail_start(callback.from_user.id)


@router.callback_query(F.data == "company_reject_by_user")
async def cmd_company_reject_by_user(callback: F.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user = await get_user(callback.from_user.id)
    await update_user(callback.from_user.id, {'cnt': user.cnt + 1})
    await update_user_x_row_by_status(callback.from_user.id, 'requested', {'status': "company_rejected_by_user"})
    await mail_start(callback.from_user.id)


@router.callback_query(F.data == "mail_reject_by_user")
async def cmd_mail_reject_by_user(callback: F.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = await get_user_x_row_by_status(callback.from_user.id, 'requested')
    company = await get_company_by_id(row.company_id)
    user = await get_user(callback.from_user.id)
    mail = await make_mail(user, company)
    await update_user_x_row_by_status(callback.from_user.id, 'requested', {'comment': mail})
    await safe_send_message(bot, callback, text=f"Для компании {company.company_name} я подготовила письмою\n"
                                                f"Кратокое описании компании:\n{mail['prev']}\n\n\n"
                                                f"Письмо:\n\n{mail['text']}",
                            reply_markup=get_mail_ikb())
