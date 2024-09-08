from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv('../.env')
token = os.getenv('TOKEN_GPT')
client = OpenAI(api_key=token)


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


async def make_mail(user, company):
    str = f"""Ты — Лида, эксперт по B2B email outreach, специализирующийся на написании цепочек писем для компаний. Ты знаешь все тонкости этого дела и умеешь писать письма так, чтобы выводить клиентов на звонок.

            Твоя задача — написать цепочку писем для B2B компании.
            ---
            **Первое письмо:**

            **Тема письма**: **Возможности для роста {company['name']} с {user['product_name']}**

            **Текст письма**:

            Здравствуйте,

            Меня зовут {user['name']}, и я {user['jobtitle']} в {user['company_name']}. Меня искренне впечатляет, как {company['name']} успешно развивает {company['description']}, особенно ваши достижения с {{User customer product}}.

            Наша команда разработала продукт {user['product_name']}, который решает важные задачи, такие как {{User product usecase description}}. Это позволяет добиться таких преимуществ, как {{User value description}}

            Уверен, что {user['product_name']} может помочь {company['name']} быстрее достигать своих бизнес целей.

            Пожалуйста, поделитесь со мной контактами или передайте это письмо лицу, с которым я могу обсудить как добиться ваших целей в бизнесе.

            Заранее благодарю за помощь и надеюсь на дальнейшее сотрудничество!

            С уважением,
            {{User name}}
            {{User job title}}
            {{User company}}
            ---
            Используй следующий шаблон для follow-up письма:
            
            **Второе письмо:**

            Добрый день!

            Хотел напомнить о моем предыдущем письме и предложении обсудить возможности {{User product name}} для вашей компании. Мы помогаем улучшать {{User value description}}.

            Буду признателен, если вы сможете поделиться со мной контактами человека, с которым я могу обсудить, как добиться ваших целей в бизнесе. Возможно, это {{User customer job title}}.

            Заранее спасибо за ваше внимание и надеюсь на ответ!

            С уважением,
            {{User name}}
            {{User job title}}
            {{User company}}
            ---
            Используй теплый, профессиональный и уверенный тон, чтобы заинтересовать получателей в возможностях продукта. Цель — запланировать звонок с ЛПР, чтобы обсудить, как продукт может помочь их бизнесу.
            Пиши только письма. Ничего больше не пиши.
            Обязательно убедись, что письмо составлено логично, без повторений. Помни, что ты эксперт по письмам, и если каких то полей не хватает или они заполнены плохо, ты можешь без потери логики и смысла вносить коррективы в шаблоны.
          """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{str}"""},
        ]
    )


async def make_mail_lpr(company):
    str = f"""Ты — Лида, эксперт по B2B email outreach, специализирующийся на написании цепочек писем для компаний. Ты знаешь все тонкости этого дела и умеешь писать письма так, чтобы выводить клиентов на звонок.

                Твоя задача — написать цепочку писем для B2B компании.
                ---
                **Первое письмо:**

                **Тема письма**: **[LPR Name], откроем новые возможности для {{Company name}} вместе?**

                **Текст письма**:

                Добрый день, [LPR Name]!

                Меня зовут {{User name}}, и я {{User job title}} в {{User company}}. Меня искренне впечатляет, как {{Company name}} успешно развивает {{Описание компании}}, особенно ваши достижения с {{User customer product}}.

                Наша команда разработала продукт {{User product name}}, который решает важные задачи, такие как {{User product usecase description}}. Это позволяет добиться таких преимуществ, как {{User value description}}

                Уверен, что {{User product name}} может помочь {{Company name}} добиться быстрее своих бизнес целей.

                Возможно, у вас найдется время на короткий звонок, чтобы обсудить, как наш продукт может помочь вам достичь новых высот?

                С уважением,
                {{User name}}
                {{User job title}}
                {{User company}}
                ---
                Используй следующий шаблон для второго письма:

                **Второе письмо:**

                Добрый день, [LPR Name]!

                Недавно я отправлял вам письмо о том, как {{User product name}} может помочь {{Company name}} развиваться ещё быстрее. Надеюсь, у вас была возможность его просмотреть.

                Напомню, что {{User product name}} решает задачи, такие как {{User product usecase description}}, и приносит следующие преимущества {{User value description}}

                Будет здорово, если мы сможем обсудить это подробнее. Как насчет короткого созвона? Если у вас есть удобное время, пожалуйста, дайте знать.

                Всего наилучшего,
                {{User name}}
                {{User job title}}
                {{User company}}

                Используй теплый, профессиональный и уверенный тон, чтобы заинтересовать получателей в возможностях продукта. Цель — запланировать звонок с ЛПР, чтобы обсудить, как продукт может помочь их бизнесу.
                Пиши только письма. Ничего больше не пиши.
                Обязательно убедись, что письмо составлено логично, без повторений. Помни, что ты эксперт по письмам, и если каких то полей не хватает или они заполнены плохо, ты можешь без потери логики и смысла вносить коррективы в шаблоны.
              """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"""{str}"""},
        ]
    )
