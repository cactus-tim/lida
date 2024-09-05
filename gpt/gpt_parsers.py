from openai import OpenAI
client = OpenAI(api_key='')


def parse_string(input_string: str) -> dict:
    result = {}
    if input_string.strip() == "good":
        result["good"] = "good"
        return result

    lines = input_string.strip().split('  \n')

    for line in lines:
        key_value = line.split(': ', 1)
        if len(key_value) == 2:
            key, value = key_value
            result[key.strip()] = value.strip()

    return result


def parse_ints(data: str) -> list:
    return [int(s) for s in data.strip().split(',')]


def parse_strs(data: str) -> list:
    return data.strip().split(',')


async def parse_user_data(data: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{data}
            Найди в тексте поля, отвечающие за имя, фамилию, должность, почту, номер телефона, название компании, должность и отправь мне в формате, не добавляя больше никаких комментариев:\n
            name: Иван  \nsurname: Иванов  \nrole_in_company: Менеджер по продажам  \nemail: ivanov.sales@company.com  \ntel: +7 (123) 456-78-90  \ncompany_name: AI Solutions"""},
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

    return parse_ints(data)


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
