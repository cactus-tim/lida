from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from gpt.gpt_parsers import client, parse_user_data, parse_product_data, parse_edits_data, parse_company_data, parse_target_company_scope, parse_target_company_employe, parse_target_company_age, parse_target_company_money, parse_target_company_jobtitle, generate_message, parse_edits_data_1
from database.req import create_user, update_user, get_con, get_thread
from keyboards.keyboards import get_data_ikb

from database.req import get_user, create_con

# from database import requests as rq

router = Router()


@router.callback_query(F.data == "data")
async def cmd_data(callback: F.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Чтобы я смогла это сделать, я проведу вас по 5 шагам:\n"
             "Шаг 1: Я попрошу вас рассказать о себе и о вашем бизнесе/продукте.\n"
             "Шаг 2: Я уточню, каким компаниям и кому внутри них вы хотите продавать.\n"
             "Шаг 3: Я отправлюсь на поиск максимально подходящих контактов для вас."
             "Шаг 4: Я напишу каждому найденному персонализированное письмо с целью вывести на созвон с вами.\n"
             "Шаг 5: Все контакты, кто проявит интерес, передам вам.\n",
        reply_markup=get_data_ikb()
    )


@router.callback_query(F.data == "quest")
async def cmd_quest(callback: F.CallbackQuery):
    data = "Давайте начнем с первого шага на пути к заинтересованным лидам! "\
           "Напишите пожалуйста ваше имя и фамилию, почту и номер телефона. "\
           "В какой компании и на какой должности вы работаете?"
    await callback.message.answer(
        text=data,
        reply_markup=ReplyKeyboardRemove()
    )
    await create_con(callback.from_user.id, 'assistant', data)


@router.message()
async def gpt_handler(message: Message):
    user_id = message.from_user.id
    user_message = message.text
    user = await get_user(user_id)
    if user == "not created":
        thread = client.beta.threads.create()
        thread_id = thread.id
        await create_user(user_id, {'thread': thread.id})
    elif user.is_active:
        await message.answer("лимит сообщений исчерпан")
        return
    else:
        thread_id = await get_thread(user_id)

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id='asst_gx0OWMBDg3kA2pkHyUHIGTJs',
    )

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    data = messages.data[0].content[0].text.value.strip()
    await message.answer(data)
