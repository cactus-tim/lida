from aiogram import Router, F, types
import asyncio
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from handlers.error import safe_send_message
import json
import io

from bot_instance import bot, logger
from gpt.gpt_parsers import client, parse_user_data, parse_product_data, parse_edits_data, parse_company_data, \
    parse_target_company_scope, parse_target_company_employe, parse_target_company_age, parse_target_company_money, \
    parse_target_company_jobtitle, generate_message, parse_edits_data_1
from database.req import create_user, update_user, get_thread
from keyboards.keyboards import get_data_ikb
from error_handlers.handlers import gpt_error_handler

from database.req import get_user
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramUnauthorizedError, TelegramNetworkError

# from database import requests as rq

router = Router()


def clean_json_string(json_string):
    start_index = json_string.find("{")
    end_index = json_string.rfind("}") + 1
    if start_index != -1 and end_index != -1:
        return json_string[start_index:end_index]
    else:
        return "JSON object not found"


@router.callback_query(F.data == "data")
async def cmd_data(callback: F.CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback,
                            text="Чтобы я смогла это сделать, я проведу вас по 5 шагам:\n"
                                 "Шаг 1: Я попрошу вас рассказать о себе и о вашем бизнесе/продукте.\n"
                                 "Шаг 2: Я уточню, каким компаниям и кому внутри них вы хотите продавать.\n"
                                 "Шаг 3: Я отправлюсь на поиск максимально подходящих контактов для вас."
                                 "Шаг 4: Я напишу каждому найденному персонализированное письмо с целью вывести на созвон с вами.\n"
                                 "Шаг 5: Все контакты, кто проявит интерес, передам вам.\n",
                            reply_markup=get_data_ikb(),
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
    await safe_send_message(bot, callback, text=data, reply_markup=ReplyKeyboardRemove())


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
    if user == "not created":
        await safe_send_message(bot, message, text="Приве, мы пока не знакомы. Нажми /start")
        return
    if user.is_active:
        await safe_send_message(bot, message, text="Я уже убежала искать подходящие компании, как только найду и "
                                                   "проверю их,"
                                                   "сразу вам напишу.\n"
                                                   "Если вы хотите заново заполнить информацию о своей компании и "
                                                   "продукте,"
                                                   "просто введите команду /start.")
        return
    else:
        thread_id = await get_thread(user_id)

    # mb make error handler here

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
    if data.count('{') > 0 and data.count('}') > 0:
        cleaned_text = clean_json_string(data)
        data_to_db = json.loads(cleaned_text)
        data_to_db['is_active'] = True
        # if you need you can here cut okveds
        await update_user(user_id, data_to_db)
        await safe_send_message(bot, message, text="Отлично! Я заполнила всю информацию и приступила к поиску "
                                                   "подходящих компаний."
                                                   "Ежедневно я буду находить 10 таких компаний и составлять для них "
                                                   "персонализированные письма от вашего имени."
                                                   "Каждое письмо и компанию я согласую с вами. "
                                                   "У вас будет возможность отменить отправку письма, отправить его или"
                                                   "отредактировать любую часть."
                                                   "Как только компания ответит, я немедленно перешлю вам их ответ.\n\n"
                                                   "Если вы хотите заново заполнить информацию о своей компании и "
                                                   "продукте,"
                                                   "просто введите команду /start.")
    else:
        await safe_send_message(bot, message, text=data)
