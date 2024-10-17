from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
import json
import io

from handlers.error import safe_send_message
from bot_instance import bot, event
from gpt.gpt_parsers import client, preprocess_data, assystent_questionnary, preprocess_extra_data
from database.req import create_user, update_user, get_thread
from keyboards.keyboards import get_data_ikb
from database.req import get_user


router = Router()


async def clean_json_string(json_string):
    start_index = json_string.find("{")
    end_index = json_string.rfind("}") + 1
    if start_index != -1 and end_index != -1:
        return json_string[start_index:end_index]
    else:
        return "JSON object not found"


@router.callback_query(F.data == "data")
async def cmd_data(callback: F.CallbackQuery):
    await callback.message.delete()
    await safe_send_message(bot, callback,
                            text="Чтобы я смогла это сделать, я проведу вас по 5 шагам:\n"
                                 "Шаг 1: Я попрошу вас рассказать о себе и о вашем бизнесе/продукте.\n"
                                 "Шаг 2: Я уточню, каким компаниям и кому внутри них вы хотите продавать.\n"
                                 "Шаг 3: Я отправлюсь на поиск максимально подходящих контактов для вас."
                                 "Шаг 4: Я напишу каждому найденному персонализированное письмо с целью вывести на "
                                 "созвон с вами.\n"
                                 "Шаг 5: Все контакты, кто проявит интерес, передам вам.\n",
                            reply_markup=get_data_ikb(),
                            )


@router.callback_query(F.data == "quest")
async def cmd_quest(callback: F.CallbackQuery):
    await callback.message.delete()
    user = await get_user(callback.from_user.id)
    thread = client.beta.threads.create()
    thread_id = thread.id
    if user == "not created":
        await create_user(callback.from_user.id, {'thread': thread.id})
    else:
        await update_user(callback.from_user.id, {'thread': thread.id, 'is_active': False, 'is_quested': False})

    data = await assystent_questionnary(thread_id)
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
        await safe_send_message(bot, message, text="Привет, мы пока не знакомы. Нажми /start")
        return
    elif user.is_quested2 == 'in_progress':
        thread_id = user.thread_q2
        data = await assystent_questionnary(thread_id, user_message, assistant_id='asst_ULM4xN6RyHPEuVNlaPBAxtoI')
        if data[0:6] == 'Готово':
            data_json = await preprocess_extra_data(data)
            cleaned_text = await clean_json_string(data_json)
            data_to_db = json.loads(cleaned_text)
            data_to_db['is_quested2'] = 'done'
            await update_user(user_id, data_to_db)
            await safe_send_message(bot, message, text="молодец молодец")
            event.set()
        else:
            await safe_send_message(bot, message, text=data)
        return
    elif user.is_quested or user.is_quested2 == 'done':
        await safe_send_message(bot, message, text="Я уже убежала искать подходящие компании, как только найду и "
                                                   "проверю их,"
                                                   "сразу вам напишу.\n"
                                                   "Если вы хотите заново заполнить информацию о своей компании и "
                                                   "продукте,"
                                                   "просто введите команду /start.")
        return
    else:
        thread_id = await get_thread(user_id)

    data = await assystent_questionnary(thread_id, user_message)
    if data[0:6] == 'Готово':
        data_json = await preprocess_data(data)
        cleaned_text = await clean_json_string(data_json)
        data_to_db = json.loads(cleaned_text)
        data_to_db['is_active'] = True
        data_to_db['is_quested'] = True
        # if you need you can here cut okveds
        await update_user(user_id, data_to_db)
        await safe_send_message(bot, message, text="Отлично! Я заполнила всю информацию и приступила к поиску "
                                                   "подходящих компаний. "
                                                   "Ежедневно я буду находить 30 таких компаний и составлять для них "
                                                   "персонализированные письма от вашего имени. "
                                                   "Каждое письмо и компанию я согласую с вами. "
                                                   "У вас будет возможность отменить отправку письма, отправить его "
                                                   "или отредактировать любую часть. "
                                                   "Каждый день, после отправки всех писем, я буду отправлять вам а"
                                                   "ктуальную информацию касаемо каждого письма.\n\n"
                                                   "Если вы хотите заново заполнить информацию о своей компании и "
                                                   "продукте, "
                                                   "просто введите команду /start.")
    else:
        await safe_send_message(bot, message, text=data)
