from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove

from database.req import get_user
from keyboards.keyboards import get_main_ikb
from bot_instance import bot
from handlers.error import safe_send_message
from mails.mail_sender import update, start_q2

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await safe_send_message(bot, message, text="Привет! Я Лида, твой виртуальный ассистент по продажам. Я помогу вам "
                                               "находить контакты ЛПРов."
                                               "Автоматизируя общение с контактами, я организую встречи с вашими "
                                               "продавцами, чтобы они могли"
                                               "сосредоточиться на продажах, а не на поиске клиентов!",
                            reply_markup=get_main_ikb())
    await state.clear()


@router.message(Command("info"))
async def cmd_info(message: Message):
    await safe_send_message(bot, message, text="Я учусь и уже кое-что могу: ежедневно буду для вас находить 10 "
                                               "подходящих компаний."
                                               "В некоторых я найду контакты ЛПРов и составлю персонализированные "
                                               "письма для организации созвонов с вами."
                                               "Если контакт не найден, я напишу на общую почту для связи с нужным "
                                               "человеком. Отклики передам вам.",
                            reply_markup=get_main_ikb())


@router.message(Command("stat"))
async def send_stat_to_user(message: Message):
    user_tg_id = message.from_user.id
    msg, flag = await update(user_tg_id)
    user = await get_user(user_tg_id)
    msg += "\nЕсли у вас еще не закончились письма, пожалуйста, ознакомтесь с письмом в прошлом сообщении!"
    await safe_send_message(bot, user_tg_id, text=msg, reply_markup=ReplyKeyboardRemove())
    if flag and user.is_quested2 == 'no':
        await start_q2(user_tg_id)
