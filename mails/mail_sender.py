import imaplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
import email
import smtplib
from email.header import decode_header
from email.mime.text import MIMEText
from aiogram.types import ReplyKeyboardRemove

from error_handlers.handlers import mail_error_handler
from bot_instance import bot, event
from mails.lida_instance import login, password
from database.req import get_users_tg_id, create_user_x_row_by_id, update_user_x_row_by_id, get_user, get_one_company, \
    create_company, get_company_by_id, get_all_rows_by_user, update_user, get_user_x_row_by_status, get_all_rows_by_user_w_date, get_all_rows_w_date
from keyboards.keyboards import get_mail_ikb_full
from gpt.gpt_parsers import make_mail, parse_email_data_bin, assystent_questionnary, parse_email_text, client
from handlers.error import safe_send_message


async def mail_start(user_tg_id: int):
    user = await get_user(user_tg_id)
    if user.cnt >= 30:
        await send_stat(user_tg_id)
        return None
    company = await get_one_company(user_tg_id)
    if not company:
        return None
    # company = await get_company_by_id(1)
    await create_user_x_row_by_id(user_tg_id, company.id)
    msg = await safe_send_message(bot, user_tg_id, "Пишем письмо...")
    mail = await make_mail(user, company)
    if not mail:
        await safe_send_message(bot, user_tg_id, text=" У нас какие то проблемы, попробуйте пожалуйста позже")
        await update_user(user_tg_id, {'cnt': 0, 'is_active': True})
        return None
    await update_user_x_row_by_id(user_tg_id, company.id, {'comment': mail})
    await bot.delete_message(chat_id=user_tg_id, message_id=msg.message_id)
    await safe_send_message(bot, user_tg_id, text=f"Для компании {company.company_name} я подготовила письмо:\n"
                                                  f"Кратокое описании компании:\n{mail['prev']}\n\n\n"
                                                  f"Тема письма: {mail['theme']}\n\n"
                                                  f"Письмо:\n\n{mail['text']}",
                            reply_markup=get_mail_ikb_full())


async def test_mail():
    row = await get_user_x_row_by_status(483458201, "requested")
    company = await get_company_by_id(row.company_id)
    theme = row.comment['theme']
    text = row.comment['text']
    await send_mail(theme, text, company.company_mail)


async def start_q2(user_id):
    user = await get_user(user_id)
    thread = client.beta.threads.create()
    thread_id = thread.id
    data = await assystent_questionnary(thread_id, 'поехали', assistant_id='asst_ULM4xN6RyHPEuVNlaPBAxtoI')
    await update_user(user.tg_id, {'is_quested2': 'in_progress', 'thread_q2': thread_id})
    await safe_send_message(bot, user.tg_id, text=f"blalbabla doproydi anketu\n{data}")


async def loop():
    # data = {
    #     'company_name': 'tim_company2',
    #     'okveds': '62.01',
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
    # await update_user(483458201, {'is_active': True})

    user_tg_ids = await get_users_tg_id()
    for user_tg_id in user_tg_ids:
        user = await get_user(user_tg_id)
        if user.is_active:
            await update_user(user_tg_id, {'cnt': 0, 'is_active': False})
            await mail_start(user_tg_id)
    await follow_up()


async def follow_up_stat(user_id):
    flag = False
    user = await get_user(user_id)
    if user.is_quested2 == 'no':
        await start_q2(user_id)
    msg = 'Завтра я отправлю фоллоу аппы для компаний:\n\n'
    for i in [1]:
        date = datetime.utcnow().date() - timedelta(days=i-1)
        rows = await get_all_rows_by_user_w_date(user_id, date)
        if not rows:
            continue
        flag = True
        for row in rows:
            if row.status == 'waiting_rpl_ans':
                company = await get_company_by_id(row.company_id)
                msg += f'{company.company_name}\n'
        if flag:
            if user.is_quested2 == 'no':
                return msg+'\n\n', True
            else:
                return msg+'\n\n', False
        else:
            return '', False


async def follow_up():
    for i in [1]:
        date = datetime.utcnow().date() - timedelta(days=i)
        rows = await get_all_rows_w_date(date)
        if not rows:
            continue
        for row in rows:
            if row.status == 'waiting_rpl_ans':
                company = await get_company_by_id(row.company_id)
                data = await assystent_questionnary(row.thread, mes='следующее письмо', assistant_id='asst_Ag8SRhkXXleq6kgdW0zWtkAP')  # TODO: rewrite mes
                mail = await parse_email_text(data)
                await send_mail(mail['theme'], mail['text'], company.company_mail)
                await update_user_x_row_by_id(row.user_id, row.company_id, {'follow_up_cnt': row.follow_up_cnt+1})


async def send_stat(user_tg_id: int):
    cnt = 0
    cnt1 = 0
    await update_user(user_tg_id, {'cnt': 0, 'is_active': True})
    user = await get_user(user_tg_id)
    follow_up_st, flag = await follow_up_stat(user_tg_id)
    msg = ('Все подходящие компании на сегодня закончились, убежала искать новые 30 компаний и пришлю вам их '
           f'завтра.\n\n📊 А вот пока ваша статистика:\n\n{follow_up_st}📨 Сегодня отправлено писем:')
    stat = '🥳 Новые успешные контакты:\n'
    rows = await get_all_rows_by_user_w_date(user_tg_id, datetime.utcnow().date())
    msg += f'{len(rows)}\n\n📬 Ожидаем ответы: '
    rows = await get_all_rows_by_user(user_tg_id)
    for row in rows:
        if row.status == 'waiting_rpl_ans':
            cnt1 += 1
            company = await get_company_by_id(row.company_id)
            mail = await get_latest_email_by_sender(company.company_mail)
            if mail['theme'] != 'not found':
                data = await parse_email_data_bin(mail['text'])
                if data.get('no', 0) == 0:
                    await send_mail(mail['theme'], mail['text'], user.email)
                    await update_user_x_row_by_id(user_tg_id, row.company_id,
                                                  {'status': 'lead', 'comment': mail})
                    cnt += 1
                    stat += f' - 🟢 {company.company_name} — Клиент проявил интерес.\n   👉 Я переслала вам это письмо на ваш e-mail. Рекомендую ответить как можно скорее!\n\n'
                else:
                    await update_user_x_row_by_id(user_tg_id, row.company_id, {'status': 'rejected_by_rpl'})

    msg += f'{cnt1-cnt} компаний\n\n'
    msg += stat
    await safe_send_message(bot, user_tg_id, text=msg, reply_markup=ReplyKeyboardRemove())
    if flag and user.is_quested2 == 'no':
        await start_q2(user.tg_id)


# async def send_stat_nu(user_tg_id: int):
#     await update_user(user_tg_id, {'cnt': 0, 'is_active': True})
#     user = await get_user(user_tg_id)
#     msg = 'Текущая статистика отправленных писем\n'
#     rows = await get_all_rows_by_user(user_tg_id)
#     for row in rows:
#         company = await get_company_by_id(row.company_id)
#         # if row['status'] == 'waiting_rpl_contact':
#         #     mail = await get_latest_email_by_sender(row['company_mail'])
#         #     if mail != 'not found':
#         #         data = await parse_email_data(mail)
#         #         if data.get('no', 0) == 0:
#         #             await update_company_by_id(row['company_id'], data) # need to test
#         #             mail_to_sand = await make_mail_lpr(user, company)
#         #             if company['lpr_mail'] != '':
#         #                 await send_mail(mail_to_sand, company['lpr_mail'])
#         #             await update_user_x_row_by_id({'status': 'waiting_rpl_ans', 'comment': mail})
#         #             msg += f"Ожидаем ответ от рпла компании {row['lpr_mail']}, вот его почта {row['lpr_mail']}\n"
#         #         else:
#         #             await update_user_x_row_by_id({'status': 'rejected_by_company'})
#         #             msg += f"Компания {row['name']} к сожалению отклонила наше письмо\n"
#         #     else:
#         #         msg += f"Ожидаем контакты рпла от компании {row['lpr_mail']}\n"
#         if row.status == 'waiting_rpl_ans':
#             mail = await get_latest_email_by_sender(company.company_mail)
#             if mail['theme'] != 'not found':
#                 data = await parse_email_data_bin(mail['text'])
#                 if data.get('no', 0) == 0:
#                     theme = mail['theme']
#                     text = mail['text']
#                     await send_mail(theme, text, user.email)
#                     await update_user_x_row_by_id(user_tg_id, row.company_id,
#                                                   {'status': 'lead', 'comment': mail})
#                     msg += f"Лпр комании {company.company_name} подтвердил контакт, направила его письмо вам на почту"
#                 else:
#                     await update_user_x_row_by_id(user_tg_id, row.company_id, {'status': 'rejected_by_rpl'})
#                     msg += f"Лпр компании {company.company_name} к сожалению отклонил наше письмо\n"
#             else:
#                 msg += f"Ожидаем ответ от рпла компании {company.company_name}, вот его почта {company.company_mail}\n"
#             pass
#         # elif row.status == 'company_rejected_by_user':
#             # msg += f"Вы отклонили компанию {company.company_name}\n"
#         # elif row['status'] == 'rejected_by_company':
#         #     msg += f"Компания {row['name']} к сожалению отклонила наше письмо\n"
#         elif row.status == 'rejected_by_rpl':
#             msg += f"Лпр компании {company.company_name} к сожалению отклонил наше письмо\n"
#         elif row.status == 'lead':
#             msg += f"Лпр комании {company.company_name} подтвердил контакт"
#     await safe_send_message(bot, user_tg_id, text=msg, reply_markup=ReplyKeyboardRemove(),)


@mail_error_handler
async def send_mail(theme, mail, to_email):
    theme = theme
    body = mail
    smtp_server = "smtp.timeweb.ru"
    smtp_port = 2525
    msg = MIMEMultipart()
    msg['From'] = 'lida.ai@claricont.ru'
    msg['To'] = to_email
    msg['Subject'] = theme
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(login, password)
    print('kk')
    server.sendmail(login, to_email, msg.as_string())
    print('aa')
    server.quit()


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
