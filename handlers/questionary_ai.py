from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums import ParseMode
import json
import io

from bot_instance import bot
from gpt.gpt_parsers import client, parse_user_data, parse_product_data, parse_edits_data, parse_company_data, \
    parse_target_company_scope, parse_target_company_employe, parse_target_company_age, parse_target_company_money, \
    parse_target_company_jobtitle, generate_message, parse_edits_data_1
from database.req import create_user, update_user, get_thread
from keyboards.keyboards import get_data_ikb

from database.req import get_user

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
        reply_markup=get_data_ikb(),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data == "quest")
async def cmd_quest(callback: F.CallbackQuery):
    user = await get_user(callback.from_user.id)
    thread = client.beta.threads.create()
    thread_id = thread.id
    if user == "not created":
        await create_user(callback.from_user.id, {'thread': thread.id})
    else:
        await update_user(callback.from_user.id, {'thread': thread.id, 'is_active': False})

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content="давай начнем\nне приветствуй меня, просто начни диалог"
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id='asst_gx0OWMBDg3kA2pkHyUHIGTJs',
    )

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    data = messages.data[0].content[0].text.value.strip()
    await callback.message.answer(text=data, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)


@router.message()
async def gpt_handler(message: Message):
    user_id = message.from_user.id
    if message.voice:
        voice_file = io.BytesIO()
        voice_file_id = message.voice.file_id
        file = await bot.get_file(voice_file_id)
        await bot.download_file(file.file_path, voice_file)
        voice_file.seek(0)
        voice_file.name = "voice_message.ogg"

        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=voice_file,
            response_format="text"
        )
        user_message = transcription
    elif message.text:
        user_message = message.text
    else:
        return
    user = await get_user(user_id)
    if user.is_active:
        await message.answer(text="Я уже убежала искать подходящие компании, как только найду и проверю их, "
                                  "сразу вам напишу.\n"
                                  "Если вы хотите заново заполнить информацию о своей компании и продукте, "
                                  "просто введите команду /start.",
                             parse_mode=ParseMode.HTML)
        return
    else:
        thread_id = await get_thread(user_id)

    resp = client.beta.threads.messages.create(
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
    if (data[0] == '{' and data[-1] == '}') or (data[8] == '{' and data[-5] == '}'):
        data_to_db = json.loads(messages.data[0].content[0].text.value)
        data_to_db['is_active'] = True
        # if you need you can here cut okveds
        await update_user(user_id, data_to_db)
        await message.answer(text="Отлично! Я заполнила всю информацию и приступила к поиску подходящих компаний. "
                                  "Ежедневно я буду находить 10 таких компаний и составлять для них "
                                  "персонализированные письма от вашего имени."
                                  "Каждое письмо и компанию я согласую с вами. "
                                  "У вас будет возможность отменить отправку письма, отправить его или "
                                  "отредактировать любую часть."
                                  "Как только компания ответит, я немедленно перешлю вам их ответ.\n\n"
                                  "Если вы хотите заново заполнить информацию о своей компании и продукте, "
                                  "просто введите команду /start.",
                             parse_mode=ParseMode.HTML)
    else:
        await message.answer(text=data, parse_mode=ParseMode.HTML)
