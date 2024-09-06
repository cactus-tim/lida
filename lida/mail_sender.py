from bot_instance import bot
from database.models import User, Company, User_x_Company
from database.req import get_users_tg_id
from keyboards.keyboards import get_mail_ikb_full


async def mail_start(user_tg_id: int):
    # TODO: company = await get_one_company(user_tg_id)
    # TODO: mail = make_mail(company)
    # TODO: save mail to db(comment)
    # TODO: update status in db
    await bot.send_message(user_tg_id, text=f"Хотите отправить компании {company['name']} письмо:\n"
                                            f"{mail}",
                           reply_markup=get_mail_ikb_full())


async def loop():
    user_tg_ids = await get_users_tg_id()
    for user_tg_id in user_tg_ids:
        await mail_start(user_tg_id)
