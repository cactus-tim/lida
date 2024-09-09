from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

from gpt.gpt_parsers import parse_user_data, parse_product_data, parse_edits_data, parse_company_data, parse_target_company_scope, parse_target_company_employe, parse_target_company_age, parse_target_company_money, parse_target_company_jobtitle, generate_message, parse_edits_data_1
from database.req import create_user, update_user
from keyboards.keyboards import get_data_ikb

from lida.database.req import get_user

# from database import requests as rq

router = Router()


class AiSallerBotState(StatesGroup):
    waiting_user_info = State()
    waiting_product_info = State()
    waiting_edits_info = State()
    waiting_price_info = State()
    waiting_company_info = State()
    waiting_target_company_scope = State()
    waiting_target_company_employe = State()
    waiting_target_company_age = State()
    waiting_target_company_money = State()
    waiting_target_company_jobtitle = State()
    waiting_target_company_edits = State()



@router.callback_query(F.data == "data")
async def cmd_data(message: Message, state: FSMContext):
    await message.answer(
        text="Чтобы я смогла это сделать, я проведу вас по 5 шагам:\n"
             "Шаг 1: Я попрошу вас рассказать о себе и о вашем бизнесе/продукте.\n"
             "Шаг 2: Я уточню, каким компаниям и кому внутри них вы хотите продавать.\n"
             "Шаг 3: Я отправлюсь на поиск максимально подходящих контактов для вас."
             "Шаг 4: Я напишу каждому найденному персонализированное письмо с целью вывести на созвон с вами.\n"
             "Шаг 5: Все контакты, кто проявит интерес, передам вам.\n",
        reply_markup=get_data_ikb()
    )


@router.callback_query(F.data == "quest")
async def cmd_quest(message: Message, state: FSMContext):
    await message.answer(
        text="Давайте начнем с первого шага на пути к заинтересованным лидам! "
             "Напишите пожалуйста ваше имя и фамилию, почту и номер телефона. "
             "В какой компании и на какой должности вы работаете?",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_user_info)


@router.message(AiSallerBotState.waiting_user_info)
async def get_user_info(message: Message, state: FSMContext):
    data = parse_user_data(message.text)
    create_user(message.from_user.id, data)

    await message.answer(
        text=f"Рада познакомиться, {data['name']}! "
             "Давайте теперь поговорим о вашем продукте. "
             "Расскажите, пожалуйста, Как он называется и какие бизнес-задачи решает для ваших клиентов? "
             "Какие ключевые преимущества и ценность он предлагает?",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_product_info)


@router.message(AiSallerBotState.waiting_product_info)
async def get_user_info(message: Message, state: FSMContext):
    data = parse_product_data(message.text)
    update_user(message.from_user.id, data)

    await message.answer(
        text=f"Здорово!  Если я правильно уловила суть, ваш продукт {data['product_name']} "
             f"направлен на решение {data['problem_solved']} "
             f"и приносит вашим клиентам ценность через {data['product_description']}? "
             f"Если есть нюансы, которые я упустила, пожалуйста, сообщите.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_edits_info)


@router.message(AiSallerBotState.waiting_edits_info)
async def get_user_info(message: Message, state: FSMContext):
    data = parse_edits_data(message.text)
    if data.get('good', 0) != 0:
        update_user(message.from_user.id, data)

    await message.answer(
        text="Отлично! Это действительно важно. "
             "Расскажи о своей компании"
             "Ваша сфера деятельности, что вы создаете и как давно существуете (в годах) и на какой вы стадии жизненного цикла"
             "не забудь рассказать про количетсво ваших сотрудников и выручку за последний год в рублях",  # TODO: rewrite this message
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_company_info)


@router.message(AiSallerBotState.waiting_company_info)
async def get_user_info(message: Message, state: FSMContext):
    data = parse_company_data(message.text)
    update_user(message.from_user.id, data)

    await message.answer(
        text="Отлично, спасибо!"
             "Теперь давайте определим, кто ваши идеальные клиенты. "
             "В каких отраслях или сферах деятельности работают компании, для которых ваш продукт приносит наибольшую пользу? "
             "Это поможет нам более точно ориентироваться при поиске потенциальных клиентов.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_target_company_scope)


@router.message(AiSallerBotState.waiting_target_company_scope)
async def get_user_info(message: Message, state: FSMContext):
    data = parse_target_company_scope(message.text)
    update_user(message.from_user.id, data)

    await message.answer(
        text="А как давно эти компании на рынке? ",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_target_company_employe)


@router.message(AiSallerBotState.waiting_target_company_employe)
async def get_user_info(message: Message, state: FSMContext):
    data = parse_target_company_employe(message.text)
    update_user(message.from_user.id, data)

    await message.answer(
        text="Отлично. "
             "Можете рассказать, насколько крупные компании среди ваших клиентов и какое количество сотрудников у них обычно?",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_target_company_age)


@router.message(AiSallerBotState.waiting_target_company_age)
async def get_user_info(message: Message, state: FSMContext):
    data = parse_target_company_age(message.text)
    update_user(message.from_user.id, data)

    await message.answer(
        text="Ага. Какую приблизительно выручку эти компании заработали за последний год? ",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_target_company_money)


@router.message(AiSallerBotState.waiting_target_company_money)
async def get_user_info(message: Message, state: FSMContext):
    data = parse_target_company_money(message.text)
    update_user(message.from_user.id, data)

    await message.answer(
        text="Теперь давайте обсудим, кому именно внутри этих компаний вы хотите продавать свой продукт. "
             "Какая должность или роли вас интересуют?",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_target_company_jobtitle)


@router.message(AiSallerBotState.waiting_target_company_jobtitle)
async def get_user_info(message: Message, state: FSMContext):
    data = parse_target_company_jobtitle(message.text)
    update_user(message.from_user.id, data)
    user = get_user(message.from_user.id)

    await message.answer(
        text=generate_message(user),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_target_company_edits)


@router.message(AiSallerBotState.waiting_target_company_edits)
async def get_user_info(message: Message, state: FSMContext):
    data = parse_edits_data_1(message.text)
    data['is_active'] = True
    update_user(message.from_user.id, data)

    await message.answer(
        text="Отлично! Каждый день я буду отправлять 10 персонализированных писем в подходящие компании."
             " Как только получу ответ с интересом к вашему продукту, "
             "я незамедлительно передам вам всю информацию о компании, "
             "контакте и других важных деталях, которые помогут вам успешно завершить сделки.",
        reply_markup=ReplyKeyboardRemove()
    )
