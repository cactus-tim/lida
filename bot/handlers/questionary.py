from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove

# from keyboards.simple_kb import make_colum_keyboard
from keyboards.keyboards import get_data_ikb

# from database import requests as rq

router = Router()


class AiSallerBotState(StatesGroup):
    waiting_user_info = State()
    waiting_product_info = State()
    waiting_edits_info = State()
    waiting_price_info = State()
    waiting_company_info = State()


@router.callback_query(F.data == "data")
async def cmd_quest(message: Message, state: FSMContext):
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
    # TODO: parse_user_data, return name, surname, tel, email, company_name, role_in_company
    data = parse_user_data(message.text)
    # TODO: save to db

    await message.answer(
        text=f"Рада познакомиться, {data[0]}! "
             "Давайте теперь поговорим о вашем продукте. "
             "Расскажите, пожалуйста, Как он называется и какие бизнес-задачи решает для ваших клиентов? "
             "Какие ключевые преимущества и ценность он предлагает? ",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_product_info)


@router.message(AiSallerBotState.waiting_product_info)
async def get_user_info(message: Message, state: FSMContext):
    # TODO: parse_product_data, return product_name, product_description, problem_solved
    data = parse_product_data(message.text)
    # TODO: save to db

    await message.answer(
        text=f"Здорово!  Если я правильно уловила суть, ваш продукт {data[0]} "
             f"направлен на решение {data[1]} "
             f"и приносит вашим клиентам ценность через {data[2]}? "
             f"Если есть нюансы, которые я упустила, пожалуйста, сообщите.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_edits_info)


@router.message(AiSallerBotState.waiting_edits_info)
async def get_user_info(message: Message, state: FSMContext):
    # TODO: parse_edits_data, return edits, or all good
    data = parse_edits_data(message.text)
    if data[0] != 'good':
        # TODO: save to db

    await message.answer(
        text="Отлично! Это действительно важно. "
             "А какова стоимость вашего продукта? "
             "Или может все гибко под каждого клиента?",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_price_info)


@router.message(AiSallerBotState.waiting_price_info)
async def get_user_info(message: Message, state: FSMContext):
    # TODO: parse_price_data, return price, or cond
    # TODO: wtf is cond, wait kirill ans
    data = parse_price_data(message.text)
    # TODO: save to db

    await message.answer(
        text="Расскажи о своей компании", # TODO: rewrite this message
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_company_info)


@router.message(AiSallerBotState.waiting_company_info)
async def get_user_info(message: Message, state: FSMContext):
    # TODO: parse_company_data, return scope_company, what_creating, number_years_existence, number_employees, revenue_last_year, life_cycle_stage, contact_company_for_sale
    data = parse_price_data(message.text)
    # TODO: save to db

    await message.answer(
        text="",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AiSallerBotState.waiting_company_info)
