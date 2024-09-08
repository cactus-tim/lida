import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bot_instance import bot
from database.models import User, Company, User_x_Company
from database.req import get_users_tg_id, create_user_x_row_row, update_user_x_row_by_id, get_user, get_one_company
from keyboards.keyboards import get_mail_ikb_full
from gpt.gpt_parsers import make_mail


async def mail_start(user_tg_id: int):
    company = await get_one_company(user_tg_id)
    await create_user_x_row_row(user_tg_id, company['id'])
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


async def send_mail(mail, company, status):
    theme = mail[0]
    body = mail[1]
    if status == 'requested':
        to_email = company['company_mail']
    else:
        to_email = company['lpr_mail']

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    gmail_user = "your-email@gmail.com"
    gmail_password = "your-app-password"

    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = theme

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
