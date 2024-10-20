from datetime import datetime
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from database.req import update_user, update_user_x_row_by_status, get_user, get_user_x_row_by_status, update_acc, \
    get_acc
from keyboards.keyboards import get_mail_ikb
from mails.mail_sender import mail_start, send_mail
from gpt.gpt_parsers import make_mail
from bot_instance import bot
from handlers.error import safe_send_message
from database.req import get_company_by_id


router = Router()


@router.callback_query(F.data == "send")
async def cmd_send(callback: F.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    row = await get_user_x_row_by_status(callback.from_user.id, "requested")
    company = await get_company_by_id(row.company_id)
    theme = row.comment['theme']
    text = row.comment['text']
    await send_mail(theme, text, company.company_mail, row.acc_id)
    user = await get_user(callback.from_user.id)
    await update_user(callback.from_user.id, {'cnt': user.cnt + 1})
    await update_user_x_row_by_status(callback.from_user.id, 'requested', {'status': "waiting_rpl_ans", 'date': datetime.utcnow().date})
    acc = await get_acc(row.acc_id)
    await update_acc(row.acc_id, {'in_use': acc.in_use+1, 'all_use': acc.all_use+1})
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
    msg = await safe_send_message(bot, callback, "Пишем письмо...")
    row = await get_user_x_row_by_status(callback.from_user.id, 'requested')
    company = await get_company_by_id(row.company_id)
    user = await get_user(callback.from_user.id)
    mail = await make_mail(user, company)
    await update_user_x_row_by_status(callback.from_user.id, 'requested', {'comment': mail})
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    await safe_send_message(bot, callback, text=f"Для компании {company.company_name} я подготовила письмою\n"
                                                f"Кратокое описании компании:\n{mail['prev']}\n\n\n"
                                                f"Тема письма: {mail['theme']}\n\n"
                                                f"Письмо:\n\n{mail['text']}",
                            reply_markup=get_mail_ikb())
