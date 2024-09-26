import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import email
from email.header import decode_header

from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardRemove

from error_handlers.handlers import mail_error_handler

from bot_instance import bot
from mails.lida_instance import login, password
from database.req import get_users_tg_id, create_user_x_row_by_id, update_user_x_row_by_id, get_user, get_one_company, \
    create_company, get_company_by_id, get_all_rows_by_user, update_user
from keyboards.keyboards import get_mail_ikb_full
from gpt.gpt_parsers import make_mail, parse_email_data_bin
from error_handlers.errors import *
from handlers.error import safe_send_message


async def mail_start(user_tg_id: int):
    user = await get_user(user_tg_id)
    if user.cnt >= 10:
        await send_stat(user_tg_id)
    company = await get_one_company(user_tg_id)
    if not company:
        return None
    # company = await get_company_by_id(1)
    await create_user_x_row_by_id(user_tg_id, company.id)
    mail = await make_mail(user, company)
    print(mail)
    if not mail:
        await safe_send_message(bot, user_tg_id, text=" У нас какие то проблемы, попробуйте пожалуйста позже")
        await update_user(user_tg_id, {'cnt': 0, 'is_active': True})
        return None
    await update_user_x_row_by_id(user_tg_id, company.id, {'comment': mail})
    await safe_send_message(bot, user_tg_id, text=f"Для компании {company.company_name} я подготовила письмо:\n"
                                                  f"Кратокое описании компании:\n{mail['prev']}\n\n\n"
                                                  f"Письмо:\n\n{mail['text']}",
                            reply_markup=get_mail_ikb_full())


async def loop():
    # data = {
    #     'company_name': 'tim_company',
    #     'okveds': ['1', '2'],
    #     'inn': 22222,
    #     'number_employees': 111,
    #     'number_years_existence': 11,
    #     'revenue_last_year': 111111,
    #     'registration_form': 11,
    #     'description': 'qegroubven',
    #     'company_mail': 'tim.sosnin@gmail.com',
    #     'company_tel': '89219988111',
    #     'site': '33333',
    #     'lpr_name': '33333',
    #     'lpr_jobtitle': '33333',
    #     'lpr_mail': '33333',
    #     'lpr_tel': '33333',
    # }
    # await create_company(data)
    # await update_user(483458201,{'is_active': True})

    user_tg_ids = await get_users_tg_id()
    for user_tg_id in user_tg_ids:
        user = await get_user(user_tg_id)
        if user.is_active:
            # await update_user(user_tg_id, {'cnt': 0, 'is_active': False})
            await mail_start(user_tg_id)


async def send_stat(user_tg_id: int):
    await update_user(user_tg_id, {'cnt': 0, 'is_active': True})
    user = await get_user(user_tg_id)
    msg = 'Лимит сообщений на сегодня исчерпан\n'
    rows = await get_all_rows_by_user(user_tg_id)
    for row in rows:
        company = await get_company_by_id(row.company_id)
        # if row['status'] == 'waiting_rpl_contact':
        #     mail = await get_latest_email_by_sender(row['company_mail'])
        #     if mail != 'not found':
        #         data = await parse_email_data(mail)
        #         if data.get('no', 0) == 0:
        #             await update_company_by_id(row['company_id'], data) # need to test
        #             mail_to_sand = await make_mail_lpr(user, company)
        #             if company['lpr_mail'] != '':
        #                 await send_mail(mail_to_sand, company['lpr_mail'])
        #             await update_user_x_row_by_id({'status': 'waiting_rpl_ans', 'comment': mail})
        #             msg += f"Ожидаем ответ от рпла компании {row['lpr_mail']}, вот его почта {row['lpr_mail']}\n"
        #         else:
        #             await update_user_x_row_by_id({'status': 'rejected_by_company'})
        #             msg += f"Компания {row['name']} к сожалению отклонила наше письмо\n"
        #     else:
        #         msg += f"Ожидаем контакты рпла от компании {row['lpr_mail']}\n"
        if row.status == 'waiting_rpl_ans':
            mail = await get_latest_email_by_sender(company.company_mail)
            if mail['theme'] != 'not found':
                data = await parse_email_data_bin(mail['text'])
                if data.get('no', 0) == 0:
                    theme = mail['theme']
                    text = mail['text']
                    await send_mail(theme, text, user.email)
                    await update_user_x_row_by_id(user_tg_id, row.company_id,
                                                  {'status': 'lead', 'comment': mail})
                    msg += f"Лпр комании {company.company_name} подтвердил контакт, направила его письмо вам на почту"
                else:
                    await update_user_x_row_by_id(user_tg_id, row.company_id, {'status': 'rejected_by_rpl'})
                    msg += f"Рпл компании {company.company_name} к сожалению отклонил наше письмо\n"
            else:
                msg += f"Ожидаем ответ от рпла компании {company.company_name}, вот его почта {company.lpr_mail}\n"
            pass
        elif row.status == 'company_rejected_by_user':
            msg += f"Вы отклонили компанию {company.company_name}\n"
        # elif row['status'] == 'rejected_by_company':
        #     msg += f"Компания {row['name']} к сожалению отклонила наше письмо\n"
        elif row['status'] == 'rejected_by_rpl':
            msg += f"Рпл компании {company.name} к сожалению отклонил наше письмо\n"
        elif row['status'] == 'lead':
            msg += f"Лпр комании {company.name} подтвердил контакт, вот его номер для связи {company.lpr_tel}"
    await safe_send_message(bot, user_tg_id, text=msg, reply_markup=ReplyKeyboardRemove(),)


@mail_error_handler
async def send_mail(theme, mail, to_email):
    theme = theme
    body = mail
    smtp_server = "smtp.timeweb.ru"
    smtp_port = 587
    msg = MIMEMultipart()
    msg['From'] = 'lida.ai@test50funnels.ru'
    msg['To'] = to_email
    msg['Subject'] = theme
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(login, password)
        server.sendmail(login, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


async def decode_mime_words(s):
    return ''.join(
        word.decode(encoding or 'utf-8') if isinstance(word, bytes) else word
        for word, encoding in decode_header(s)
    )


@mail_error_handler
async def get_latest_email_by_sender(sender_email):
    imap_server = "imap.timeweb.ru"
    mail = imaplib.IMAP4_SSL(imap_server, 993)
    mail.login(login, password)

    mail.select("inbox")
    status, messages = mail.search(None, f'FROM "{sender_email}"')
    email_ids = messages[0].split()

    if email_ids:
        latest_email_id = email_ids[-1]
        status, msg_data = mail.fetch(latest_email_id, '(RFC822)')

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = await decode_mime_words(msg["Subject"])
                # from_ = decode_mime_words(msg.get("From"))

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode('utf-8')
                else:
                    body = msg.get_payload(decode=True).decode('utf-8')
        mail.logout()
        return {'theme': subject, 'text': body}

    else:
        mail.logout()
        return {'theme': 'not found'}
