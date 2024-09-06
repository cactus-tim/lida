from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from gpt.gpt_parsers import parse_user_data, parse_product_data, parse_edits_data, parse_company_data, \
    parse_target_company_scope, parse_target_company_employe, parse_target_company_age, parse_target_company_money, \
    parse_target_company_jobtitle
from database.req import create_user, update_user
from keyboards.keyboards import get_data_ikb, get_mail_ikb
from lida.mail_sender import mail_start

# from database import requests as rq

router = Router()


@router.callback_query(F.data == "send")
async def cmd_send(message: Message, state: FSMContext):
    if cnt == 10:
        # TODO: check_old_mails,
        #  update (TODO: if take lpr contact, save to db ans sand new mail) status and comments)
        # TODO: send statistics
        pass
    else:
        # TODO: mail = await get_mail() # check status
        # TODO: await send_mail(mail)
        # TODO: update db (status in user_x_company, cnt in user)
        await mail_start(message.from_user.id)


@router.callback_query(F.data == "company_reject_by_user")
async def cmd_company_reject_by_user(message: Message, state: FSMContext):
    # TODO: update db (status in user_x_company, cnt in user)
    await mail_start(message.from_user.id)


@router.callback_query(F.data == "mail_reject_by_user")
async def cmd_mail_reject_by_user(message: Message, state: FSMContext):
    # TODO: mail = make_mail(company)
    # TODO: save mail to db(comment)
    await message.answer(text=f"Хотите отправить компании {company['name']} письмо:\n"
                              f"{mail}",
                         reply_markup=get_mail_ikb())
