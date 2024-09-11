import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import email
from email.header import decode_header

from bot_instance import bot
from mails.lida_instance import login, password
from database.req import get_users_tg_id, create_user_x_row_by_id, update_user_x_row_by_id, get_user, get_one_company
from keyboards.keyboards import get_mail_ikb_full
from gpt.gpt_parsers import make_mail


async def mail_start(user_tg_id: int):
    company = await get_one_company(user_tg_id)
    await create_user_x_row_by_id(user_tg_id, company['id'])
    user = await get_user(user_tg_id)
    mail = await make_mail(user, company)
    await update_user_x_row_by_id(user_tg_id, company['id'], {'comment': mail})
    await bot.send_message(user_tg_id, text=f"Хотите отправить компании {company['name']} письмо:\n"
                                            f"{mail}",
                           reply_markup=get_mail_ikb_full())


async def loop():
    user_tg_ids = await get_users_tg_id()
    for user_tg_id in user_tg_ids:
        await mail_start(user_tg_id)


async def send_mail(mail, to_email):
    theme = mail[0]
    body = mail[1]

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = login
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


def decode_mime_words(s):
    return ''.join(
        word.decode(encoding or 'utf-8') if isinstance(word, bytes) else word
        for word, encoding in decode_header(s)
    )


def get_latest_email_by_sender(sender_email):
    imap_server = "imap.gmail.com"
    mail = imaplib.IMAP4_SSL(imap_server)
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
                # subject = decode_mime_words(msg["Subject"])
                # from_ = decode_mime_words(msg.get("From"))

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode('utf-8')
                else:
                    body = msg.get_payload(decode=True).decode('utf-8')
        mail.logout()
        return body

    else:
        mail.logout()
        return 'not found'
