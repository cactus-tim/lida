import json
from openai import OpenAI
import os
import re
from dotenv import load_dotenv

from database.req import update_user_x_row_by_id
from error_handlers.errors import *
from error_handlers.handlers import gpt_error_handler, parser_error_handler
from database.models import User

load_dotenv('../.env')
token = os.getenv('TOKEN_API_GPT')
client = OpenAI(api_key=token)
tokenP = os.getenv('TOKEN_API_PER')
clientP = OpenAI(api_key=tokenP, base_url="https://api.perplexity.ai")


@gpt_error_handler
async def analyze_website(url: str):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an artificial intelligence assistant and you need to "
                "engage in a helpful, detailed, polite conversation with a user."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Получи информацию об описание компании, описание их основного продукта/услуги, последние новости за "
                f"последний месяц {url}"
            ),
        },
    ]

    response = clientP.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
    )
    return response.choices[0].message.content


@parser_error_handler
def parse_email_text(text):
    prev_match = re.search(r'Превью:\s*(.*)', text)
    subject_match = re.search(r'Тема:\s*(.*)', text)
    body_match = re.search(r'Письмо:\s*(.*)', text, re.DOTALL)

    prev = prev_match.group(1).strip() if subject_match else None
    subject = subject_match.group(1).strip() if subject_match else None
    body = body_match.group(1).strip() if body_match else None

    if not prev or not subject or not body:
        raise ParseError
    else:
        return {
            "prev": prev,
            "theme": subject,
            "text": body
        }


@parser_error_handler
def parse_string(input_string: str) -> dict:
    result = {}
    if input_string.strip() == "good":
        result["good"] = "good"
        return result
    if input_string.strip() == "no":
        result["no"] = "no"
        return result
    if input_string.strip() == "yes":
        result["yes"] = "yes"
        return result

    lines = input_string.strip().split('  \n')

    for line in lines:
        key_value = line.split(': ', 1)
        if len(key_value) == 2:
            key, value = key_value
            if key.strip() == 'number_years_existence':
                result[key.strip()] = int(value.strip())
            elif key.strip() == 'number_employees':
                result[key.strip()] = int(value.strip())
            elif key.strip() == 'revenue_last_year':
                result[key.strip()] = int(value.strip())
            else:
                result[key.strip()] = value.strip()
    if not result:
        raise ParseError
    else:
        return result


def parse_ints(data: str) -> list:
    return [int(s) for s in data.strip().split(',')]


def parse_strss(data: str) -> list:
    return [str(s) for s in data.strip().split(',')]


def parse_strs(data: str) -> list:
    return data.strip().split(',')


async def parse_user_data(data: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}
            Найди в тексте поля, отвечающие за имя, фамилию, должность, почту, номер телефона, название компании, должность и отправь мне в формате, не добавляя больше никаких комментариев:\n
            name: Иван  \nsurname: Иванов  \njobtitle: Менеджер по продажам  \nemail: ivanov.sales@company.com  \ntel: +7 (123) 456-78-90  \ncompany_name: AI Solutions"""},
        ]
    )

    data = response.choices[0].message.content

    return parse_string(data)


async def parse_product_data(data: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}
            Найди в тексте поля, отвечающие за имя продукта, описание продукта, решаемая проблема и отправь мне в формате, не добавляя больше никаких комментариев:\n
            product_name: AI Sales Assistant  \nproduct_description: помогает автоматизировать процесс продаж и общения с клиентами  \nproblem_solved: сокращение времени на обработку заявок, повышение конверсии и автоматизация рутинных задач"""},
        ]
    )

    data = response.choices[0].message.content

    return parse_string(data)


async def parse_edits_data(data: str) -> dict:  # not used
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}
            Пойми, хочет ли человек вности правки к каким то данным\n
            Если он не хочет, тогда отправь мне одно слово - good
            Если же он хочет внести правки, тогда следуй следующим инструкциям:\n
            В этом тексте человек вносит правки к каким то данным\n
            возможные данные для правок: имя, фамилия, должность, почта, номер телефона, название компании, должность, имя продукта, описание продукта, решаемая проблема\n
            твоя задача понять, какие конкретно хочет исправить человек и отправить мне их в таком формате, не добавляя больше никаких комментариев:\n
            name: Иван  \nemail: ivanov.sales@company.com  \nproduct_name: AI Sales Assistant,  \nproblem_solved: сокращение времени на обработку заявок, увеличение конверсии и автоматизация повседневных задач"""},
        ]
    )

    data = response.choices[0].message.content

    return parse_string(data)


async def parse_company_data(data: str) -> dict:  # not used
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}
            Найди в тексте поля, отвечающие за сферу компании, что она создает, срок деятельности, количество сотрудников, выручка за последний год, стадия жизненного цикла и отправь мне в формате, не добавляя больше никаких комментариев:\n
            scope_company: разработка решений для автоматизации продаж  \nwhat_creating: AI Sales Assistant  \nnumber_years_existence: 5 (это поле должно быть числом)  \nnumber_employees: 100(это поле должно быть числом)  \nrevenue_last_year: 150000000(это поле должно быть числом)  \nlife_cycle_stage: стадия стабильного роста
          """},
        ]
    )

    data = response.choices[0].message.content

    return parse_string(data)


async def parse_target_company_scope(data: str) -> list:  # not used
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}\n
            Шаг 1: Найди в тексте поля, отвечающие за сферы деятлельности компаний\n
            Шаг 2: Используя сайт https://www.regfile.ru/okved2.html определи коды оквед, соответствующие этим сферам деятельности\n
            если ответ пользователя содержит смысл, что это не имеет значение, то просто отправь 0\n
            Шаг 3: Отправь мне эти коды в формате, не отпраляй ничего кроме кодов, никаких комментариев и лишних символов!:\n
            41, 63, 62, 66, 69, 92
          """},
        ]
    )

    data = response.choices[0].message.content

    return parse_strss(data)


async def parse_target_company_employe(data: str) -> list:  # not used
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}\n
            Найди в тексте поля, отвечающие за количество сотрудников компании\n
            если ответ пользователя содержит смысл, что это не имеет значение, то просто отправь 0\n
            и отправь мне в формате, не добавляя больше никаких комментариев или иных символов:\n
            100, 1000
          """},
        ]
    )

    data = response.choices[0].message.content

    return parse_ints(data)


async def parse_target_company_age(data: str) -> list:  # not used
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}\n
            Найди в тексте поля, отвечающие за возраст компании\n
            если ответ пользователя содержит смысл, что это не имеет значение, то просто отправь 0\n
            отправь мне в формате, не добавляя больше никаких комментариев или иных символов:\n
            1, 10 (именно запятая и никак иначе)
          """},
        ]
    )

    data = response.choices[0].message.content

    return parse_ints(data)


async def parse_target_company_money(data: str) -> list:  # not used
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}\n
            Найди в тексте поля, отвечающие за годовую выручку компании\n
            если ответ пользователя содержит смысл, что это не имеет значение, то просто отправь 0\n
            отправь мне в формате чисел, не добавляя приписку тысячи, миллионы или миллиарды, переведи это в нули, что бы на выходе получить числа, не добавляя больше никаких комментариев или иных символов:\n
            1000, 10000000 (именно запятая и никак иначе)
          """},
        ]
    )

    data = response.choices[0].message.content

    return parse_ints(data)


async def parse_target_company_jobtitle(data: str) -> list:  # not used
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}\n
            Найди в тексте поля, отвечающие за название должностей, которые интересуют человека\n
            если ответ пользователя содержит смысл, что это не имеет значение, то просто отправь 0\n
            отправь мне в формате через запятую, не добавляя больше никаких комментариев или иных символов:\n
          """},
        ]
    )

    data = response.choices[0].message.content

    return parse_strs(data)


async def generate_message(user: User) -> str:  # not used
    data = (f"Итак, я собрала следующую информацию:"
            f" ваш продукт {user.product_name}"
            f" решает {user.problem_solved}"
            f" и приносит ценность через {user.product_description}."
            f" Вы ориентируетесь на компании в сфере {user.target_okveds} (вмето кодов оквед напиши их расшифровку, https://www.regfile.ru/okved2.html),"
            f" с числом сотрудников около {user.target_number_employees}"
            f" и выручкой примерно {user.target_revenue_last_year}."
            f" Они присутствуют на рынке {user.target_number_years_existence},"
            f" и мы будем искать контакты лиц на должности {user.target_jobtitle}."
            f" Всё верно? Если есть что-то для уточнения, дайте знать.")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}
             сделай этот текст лаконичным
            """},
        ]
    )
    #          User product name - {user.product_name}
    #          User product usecase description - {user.problem_solved}
    #          User value description - {user.product_description}
    #          User customer industry - {user.target_okveds}, вмето кодов оквед напиши их расшифровку, https://www.regfile.ru/okved2.html
    #          User customer employe - {user.target_number_employees}
    #          User customer money - {user.target_revenue_last_year}
    #          User customer age - {user.target_number_years_existence}
    #          User customer jobtitle - {user.target_jobtitle}
    #       """},
    #     ]
    # )

    return response.choices[0].message.content


async def parse_edits_data_1(data: str) -> dict:  # not used
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}
            Пойми, хочет ли человек вности правки к каким то данным\n
            Если он не хочет, тогда отправь мне одно слово - good
            Если же он хочет внести правки, тогда следуй следующим инструкциям:\n
            В этом тексте человек вносит правки к каким то данным\n
            возможные данные для правок: название продукта, проблемы которые решает продукт, описание продукта, коды оквед, число сотрудников, выручка за прошлый год в рублях, кол-во лет существования комании, должность\n
            твоя задача понять, какие конкретно хочет исправить человек и отправить мне их в таком формате, не добавляя больше никаких комментариев:\n
            product_name: AI Sales Assistant,  \nproblem_solved: сокращение времени на обработку заявок, увеличение конверсии и автоматизация повседневных задач"""},
        ]
    )

    data = response.choices[0].message.content

    return parse_string(data)


@gpt_error_handler
async def preprocess_data(data: str):
    str = f"""
Твоя задача обработаь полученный текст и сформировать json объект и затем отпарвить его мне
переменные в этом json объекте: 
name, surname, email, tel, company_name, jobtitle, product_name, product_description, problem_solved, target_okveds, target_number_employees, target_number_years_existence, target_revenue_last_year, target_jobtitle, key_problem, key_value, proof_points

обработка текста:
name: str
surname: str
email: str
tel: str
company_name: str
jobtitle: str
product_name: str
product_description: str
problem_solved: str
key_problem: str
key_value: str
proof_points: str
target_okveds: list(str), перед обработкой используя эту ссылку https://www.regfile.ru/okved2.html замени на номера окведов, не обрезай их, пиши полные номера
target_number_employees: list(int), массив должен содержать либо не более 2 чисел - минимальное и максимальное количество, либо одно число (!=0), либо массив с единственным числом 0, если в данных говорится о том что этот параметр не важен
target_number_years_existence: list(int), массив должен содержать либо не более 2 чисел - минимальное и максимальное количество, либо одно число (!=0), либо массив с единственным числом 0, если в данных говорится о том что этот параметр не важен
target_revenue_last_year: list(int), массив должен содержать либо не более 2 чисел - минимальное и максимальное количество, либо одно число (!=0), либо массив с единственным числом 0, если в данных говорится о том что этот параметр не важен, сами числа запиши целиком, со всеми разрядами
target_jobtitle: list(str)

ответ отправь мне в формате json, не добавляя к нему каких либо комментариев

{data}
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": str},
        ]
    )
    res = response.choices[0].message.content
    if not res:
        raise ContentError
    else:
        return res


@gpt_error_handler
async def make_mail(user, company):
    text = f"""
    Твоя задача написать письмо для компании {company.company_name}, ее область деятельности {company.okveds} и инн - {company.inn}, а сайт {company.site}
    Их выручка за прошлый год - {company.revenue_last_year} рублей, а количество сотрудников - {company.number_employees}
    Ты пишешь письмо от лица человека - его зовут {user.name} {user.surname}, он работает в {user.company_name} и занимает должность {user.jobtitle}, а его почта - {user.email}
    Твоя задача написать письмо о продукте: {user.product_name}, вот его описание {user.product_description} и проблемы, которые он решает {user.problem_solved}
    Ключевая проблема, решаемая продуктом: {user.key_problem}, его ключевая ценность {user.key_value}, а доказательства {user.proof_points}
    В письме ты хочешь найти контакты человека на должности {user.target_jobtitle}  
        """

    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id='asst_Ag8SRhkXXleq6kgdW0zWtkAP',

    )
    thread_id = thread.id
    await update_user_x_row_by_id(user.tg_id, company.id, {'thread': thread_id})

    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "requires_action":
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                if tool_call.function.name == "analyze_website":
                    url = json.loads(tool_call.function.arguments)['url']
                    analysis_result = await analyze_website(url)
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=[{
                            "tool_call_id": tool_call.id,
                            "output": analysis_result
                        }]
                    )

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    data = messages.data[0].content[0].text.value
    if not data:
        raise ContentError
    else:
        return await parse_email_text(data)


@gpt_error_handler
async def assystent_questionnary(thread_id, mes="давай начнем", assistant_id='asst_gx0OWMBDg3kA2pkHyUHIGTJs'):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=mes
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    data = messages.data[0].content[0].text.value.strip()
    if not data:
        return ContentError
    else:
        return data


async def make_mail_lpr(user: object, company: object) -> object:  # not used
    # TODO: rewrite prompt
    str = f"""
        Ты — Лида, эксперт по B2B email outreach, специализирующийся на написании цепочек писем для компаний. Ты знаешь все тонкости этого дела и умеешь писать письма так, чтобы выводить клиентов на звонок.

        Твоя задача — написать письмо для B2B компании.

        Ты знаешь такие вещи, как название компании, которой пишется письмо, ее оквед коды и описание, а так же контакты ЛПР-а: его имя и должность

        Про отправителя ты знаешь его имя, фамилию, номер телефона и email, место его работы и должность, и то, какой товар он должен продать, его описание и проблемы, которые он решает
        
        Используй теплый, профессиональный и уверенный тон, чтобы заинтересовать получателей в возможностях продукта. Цель — запланировать звонок с ЛПР, чтобы обсудить, как продукт может помочь их бизнесу.
        
        Обязательно убедись, что письмо составлено логично, без повторений. Помни, что ты эксперт по письмам, и если каких то полей не хватает или они заполнены плохо, ты можешь без потери логики и смысла вносить коррективы в шаблоны.
        
        все данные для писем выдумай

        отвечай мне в фомате:
        тема: [тема письма]
        письмо: [текст письма]
        """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{str}"""},
        ]
    )
    data = response.choices[0].message.content
    return parse_email_text(data)


async def parse_email_data(data: str) -> dict:  # not used
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}
             это письмо от компании, которой я заинтересован продать свое бизнес решение, проанализируй его, твоя задача понять, заинтересована ли она в интеграции моего решения\n
             если не заинтересована, то отправь мне одно слово - no
             в противном случае следуй инструкции:
             найди в письме поля, отвечающие за имя, должность, номер телефона и почту контактного лица (каких то данных может не быть, ничего страшного) и отправь мне в формате, не добавляя больше никаких комментариев:\n
             lpr_name: Иван  \lpr_jobtitle: Иванов  \nlpr_mail: ivan@gmail.com  \nlpr_tel: 89219911188
          """},
        ]
    )

    data = response.choices[0].message.content

    return parse_string(data)


@gpt_error_handler
async def parse_email_data_bin(data: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}
             это текст письма от компании, неважно на сколько оно короткое, которой я заинтересован продать свое бизнес решение, проанализируй его, твоя задача понять, заинтересована ли она в интеграции моего решения\n
             если ты не можешь понять, заинтересовен ли человек, или если он не заинтересован отправь - no
             в противном случае - yes
          """},
        ]
    )

    data = response.choices[0].message.content
    if not data:
        raise ContentError

    res = {}
    if data.strip() == "no":
        res["no"] = "no"
        return res
    if data.strip() == "yes":
        res["yes"] = "yes"
        return res
    else:
        raise ParseError

    # loop = asyncio.get_running_loop()
    # parsed_data = await loop.run_in_executor(None, parse_string, data)
    # return parsed_data
