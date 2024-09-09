from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from gpt.gpt_parsers import parse_user_data, parse_product_data, parse_edits_data, parse_company_data, \
    parse_target_company_scope, parse_target_company_employe, parse_target_company_age, parse_target_company_money, \
    parse_target_company_jobtitle
from database.req import create_user, update_user, update_user_x_row_by_id, update_user_x_row_by_status, get_user, get_user_x_row_by_status, get_all_rows_by_user
from keyboards.keyboards import get_data_ikb, get_mail_ikb
from lida.mail_sender import mail_start, send_mail, get_latest_email_by_sender
from gpt.gpt_parsers import make_mail, make_mail_lpr, parse_email_data, parse_email_data_bin

from lida.database.req import get_company_by_id, update_company_by_id

# from database import requests as rq

router = Router()


@router.callback_query(F.data == "send")
async def cmd_send(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user['cnt'] == 10:
        msg = ''
        rows = await get_all_rows_by_user(message.from_user.id)
        for row in rows:
            company = await get_company_by_id(row['company_id'])
            if row['status'] == 'waiting_rpl_contact':
                mail = await get_latest_email_by_sender(row['company_mail'])
                if mail != 'not found':
                    data = await parse_email_data(mail)
                    if data.get('no', 0) == 0:
                        await update_company_by_id(row['company_id'], data) # need to test
                        mail_to_sand = await make_mail_lpr(user, company)
                        if company['lpr_mail'] != '':
                            await send_mail(mail_to_sand, company['lpr_mail'])
                        await update_user_x_row_by_id({'status': 'waiting_rpl_ans', 'comment': mail})
                        msg += f"Ожидаем ответ от рпла компании {row['lpr_mail']}, вот его почта {row['lpr_mail']}\n"
                    else:
                        await update_user_x_row_by_id({'status': 'rejected_by_company'})
                        msg += f"Компания {row['name']} к сожалению отклонила наше письмо\n"
                else:
                    msg += f"Ожидаем контакты рпла от компании {row['lpr_mail']}\n"
                pass
            elif row['status'] == 'waiting_rpl_ans':
                mail = await get_latest_email_by_sender(row['company_mail'])
                if mail != 'not found':
                    data = await parse_email_data_bin(mail)
                    if data.get('no', 0) == 0:
                        await send_mail(mail, user['email'])
                        await update_user_x_row_by_id({'status': 'lead', 'comment': mail})
                        msg += f"Лпр комании {row['name']} подтвердил контакт, направила его письмо вам на почту"
                    else:
                        await update_user_x_row_by_id({'status': 'rejected_by_rpl'})
                        msg += f"Рпл компании {row['name']} к сожалению отклонил наше письмо\n"
                else:
                    msg += f"Ожидаем ответ от рпла компании {row['lpr_mail']}, вот его почта {row['lpr_mail']}\n"
                pass
            elif row['status'] == 'company_rejected_by_user':
                msg += f"Вы отклонили компанию {row['name']}\n"
            elif row['status'] == 'rejected_by_company':
                msg += f"Компания {row['name']} к сожалению отклонила наше письмо\n"
            elif row['status'] == 'rejected_by_rpl':
                msg += f"Рпл компании {row['name']} к сожалению отклонил наше письмо\n"
            elif row['status'] == 'lead':
                msg += f"Лпр комании {row['name']} подтвердил контакт, вот его номер для связи {row['lpr_tel']}"
        await message.answer(text=f"{msg}",
                             reply_markup=ReplyKeyboardRemove())
    else:
        row = await get_user_x_row_by_status(message.from_user.id, "requested")
        company = await get_company_by_id(row['company_id'])
        await send_mail(row['comment'], company['company_mail'])
        user = await get_user(message.from_user.id)
        await update_user(message.from_user.id, {'cnt': user['cnt'] + 1})
        await update_user_x_row_by_status(message.from_user.id, 'requested', {'status': "waiting_rpl_contact"})
        await mail_start(message.from_user.id)


@router.callback_query(F.data == "company_reject_by_user")
async def cmd_company_reject_by_user(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    await update_user(message.from_user.id, {'cnt': user['cnt']+1})
    await update_user_x_row_by_status(message.from_user.id, 'requested', {'status': "company_rejected_by_user"})
    await mail_start(message.from_user.id)


@router.callback_query(F.data == "mail_reject_by_user")
async def cmd_mail_reject_by_user(message: Message, state: FSMContext):
    company = await get_user_x_row_by_status(message.from_user.id, 'requested')
    user = await get_user(message.from_user.id)
    mail = make_mail(user, company)
    await update_user_x_row_by_status(message.from_user.id, 'requested', {'comment': mail})
    await message.answer(text=f"Хотите отправить компании {company['name']} письмо:\n"
                              f"{mail}",
                         reply_markup=get_mail_ikb())
