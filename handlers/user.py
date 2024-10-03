from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message

from keyboards.keyboards import get_main_ikb
from bot_instance import bot
from handlers.error import safe_send_message


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
