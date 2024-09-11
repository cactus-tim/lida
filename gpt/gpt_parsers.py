from openai import OpenAI
import os
import re
from dotenv import load_dotenv

from database.models import User


load_dotenv('../.env')
token = os.getenv('TOKEN_API_GPT')
client = OpenAI(api_key=token)


def parse_email_text(text):
    subject_match = re.search(r'Тема:\s*(.*)', text)
    body_match = re.search(r'Письмо:\s*(.*)', text, re.DOTALL)

    subject = subject_match.group(1).strip() if subject_match else None
    body = body_match.group(1).strip() if body_match else None

    return {
        "theme": subject,
        "text": body
    }



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


async def parse_edits_data(data: str) -> dict:
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


async def parse_company_data(data: str) -> dict:
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


async def parse_target_company_scope(data: str) -> list:
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


async def parse_target_company_employe(data: str) -> list:
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


async def parse_target_company_age(data: str) -> list:
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


async def parse_target_company_money(data: str) -> list:
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


async def parse_target_company_jobtitle(data: str) -> list:
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


async def generate_message(user: User) -> str:
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


async def parse_edits_data_1(data: str) -> dict:
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


async def make_mail(user, company):
    # TODO: rewrite prompt
    str = f"""
        Ты — Лида, эксперт по B2B email outreach, специализирующийся на написании цепочек писем для компаний. Ты знаешь все тонкости этого дела и умеешь писать письма так, чтобы выводить клиентов на звонок.

        Твоя задача — написать письмо для B2B компании.

        Ты знаешь такие вещи, как название компании, которой пишется письмо, ее оквед коды и описание, твоя задача сделать так, что бы в обратном письме тебе дали контакты ЛПР-а, тебе они не известны

        Про отправителя ты знаешь его имя, фамилию, номер телефона и email, место его работы и должность, и то, какой товар он должен продать, его описание и проблемы, которые он решает
        
        Используй теплый, профессиональный и уверенный тон, чтобы заинтересовать получателей в возможностях продукта. Цель — запланировать звонок с ЛПР, чтобы обсудить, как продукт может помочь их бизнесу.
        
        Обязательно убедись, что письмо составлено логично, без повторений. Помни, что ты эксперт по письмам, и если каких то полей не хватает или они заполнены плохо, ты можешь без потери логики и смысла вносить коррективы в шаблоны.
        
       вот данные о пользоветеле: \n{user}\nа вот о компании: \n{company}\n

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


async def make_mail_lpr(user: object, company: object) -> object:
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


async def parse_email_data(data: str) -> dict:
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


async def parse_email_data_bin(data: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}
             это письмо от компании, которой я заинтересован продать свое бизнес решение, проанализируй его, твоя задача понять, заинтересована ли она в интеграции моего решения\n
             если не заинтересована, то отправь мне одно слово - no
             в противном случае - yes
          """},
        ]
    )

    data = response.choices[0].message.content

    return parse_string(data)
