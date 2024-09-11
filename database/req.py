from database.models import User, Company, User_x_Company, async_session
from sqlalchemy import select, desc, distinct, and_


async def get_user(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return user
        else:
            print("Пользователь с таким id не найден")


async def create_user(tg_id: int, data: dict):
    async with async_session() as session:
        user = await get_user(tg_id)
        if not user:
            data['tg_id'] = tg_id
            user_data = User(**data)
            session.add(user_data)
            await session.commit()
        else:
            print("Пользователь с таким id уже существует")


async def update_user(tg_id: int, data: dict):
    async with async_session() as session:
        user = await get_user(tg_id)
        if not user:
            print("Пользователь с таким id не найден")
        else:
            for key, value in data.items():
                setattr(user, key, value)
            session.add(user)
            await session.commit()


async def get_users_tg_id():
    async with async_session() as session:
        users_tg_id = await session.execute(select(distinct(User.tg_id)))
        return users_tg_id.scalars().all()


async def get_company_by_name(company_name: str):
    async with async_session() as session:
        company = await session.scalar(select(Company).where(Company.company_name == company_name))
        return company


async def get_company_by_id(company_id: int):
    async with async_session() as session:
        company = await session.scalar(select(Company).where(Company.id == company_id))
        return company


async def create_company(data: dict):   # in data must be company_name
    async with async_session() as session:
        company = await get_company_by_name(data['company_name'])
        if not company:
            company_data = Company(**data)
            session.add(company_data)
            await session.commit()
        else:
            print("Компания с таким именем уже существует")


async def update_company_by_name(company_name: str, data: dict):
    async with async_session() as session:
        company = await get_company_by_name(company_name)
        if not company:
            print("Компания с таким именем не найдена")
        else:
            for key, value in data.items():
                setattr(company, key, value)
            session.add(company)
            await session.commit()


async def update_company_by_id(company_id: int, data: dict):
    async with async_session() as session:
        company = await get_company_by_id(company_id)
        if not company:
            print("Компания с таким id не найдена")
        else:
            for key, value in data.items():
                setattr(company, key, value)
            session.add(company)
            await session.commit()


async def get_one_company(tg_id: int):
    async with async_session() as session:
        user = await get_user(tg_id)

        subquery = select(User_x_Company.company_id).where(User_x_Company.user_id == tg_id).subquery()
        query = select(Company).outerjoin(subquery, Company.id == subquery.c.company_id).where(subquery.c.company_id.is_(None))

        if len(user.target_okveds) > 0:
            query = query.where(Company.okveds.any(user.target_okveds))

        if len(user.target_number_employees) > 0:
            if len(user.target_number_employees) == 1:
                query = query.where(Company.number_employees == user.target_number_employees[0])
            elif len(user.target_number_employees) == 2:
                query = query.where(
                    and_(Company.number_employees >= user.target_number_employees[0],
                         Company.number_employees <= user.target_number_employees[1])
                )

        if len(user.target_number_years_existence) > 0:
            if len(user.target_number_years_existence) == 1:
                query = query.where(Company.number_years_existence == user.target_number_years_existence[0])
            elif len(user.target_number_years_existence) == 2:
                query = query.where(
                    and_(Company.number_years_existence >= user.target_number_years_existence[0],
                         Company.number_years_existence <= user.target_number_years_existence[1])
                )

        if len(user.target_revenue_last_year) > 0:
            if len(user.target_revenue_last_year) == 1:
                query = query.where(Company.revenue_last_year == user.target_revenue_last_year[0])
            elif len(user.target_revenue_last_year) == 2:
                query = query.where(
                    and_(Company.revenue_last_year >= user.target_revenue_last_year[0],
                         Company.revenue_last_year <= user.target_revenue_last_year[1])
                )

        # if len(user.target_jobtitle) > 0:
        #     if len(user.target_jobtitle) == 1:
        #         query = query.where(Company.target_jobtitle == user.target_jobtitle)

        result = await session.execute(query)
        return result.scalars().first()


async def get_user_x_company_row_by_name(tg_id: int, company_name: str):
    async with async_session() as session:
        company = await get_company_by_name(company_name)
        if not company:
            print("Компания с таким именем не найдена")
        company_id = company['id']
        row = await session.scalar(select(User_x_Company)
                                   .where(and_(User_x_Company.tg_id == tg_id, User_x_Company.id == company_id)))
        if row:
            return row
        else:
            print("Запись с такими параметрами не найдена")


async def get_user_x_company_row_by_id(tg_id: int, company_id: int):
    async with async_session() as session:
        row = await session.scalar(select(User_x_Company)
                                   .where(and_(User_x_Company.user_id == tg_id, User_x_Company.company_id == company_id)))
        if row:
            return row
        else:
            print("Запись с такими параметрами не найдена")


async def create_user_x_row_by_id(tg_id: int, company_id: int):
    async with async_session() as session:
        row = await get_user_x_company_row_by_id(tg_id, company_id)
        if not row:
            row = User_x_Company(user_id=tg_id, company_id=company_id)
            session.add(row)
            await session.commit()
        else:
            print("already exist")


async def update_user_x_row_by_id(tg_id: int, company_id: int, data):
    async with async_session() as session:
        row = await get_user_x_company_row_by_id(tg_id, company_id)
        if not row:
            print("Запись с таким id не найдена")
        else:
            for key, value in data.items():
                setattr(row, key, value)
            session.add(row)
            await session.commit()


async def get_user_x_row_by_status(tg_id: int, status: str):
    async with async_session() as session:
        row = await session.scalar(select(User_x_Company)
                                   .where(and_(User_x_Company.user_id == tg_id, User_x_Company.status == status)))
        if row:
            return row
        else:
            print("Запись с такими параметрами не найдена")


async def update_user_x_row_by_status(tg_id: int, status: str, data: dict):
    async with async_session() as session:
        row = await get_user_x_row_by_status(tg_id, status)
        if not row:
            print("Запись с таким статусом не найдена")
        else:
            for key, value in data.items():
                setattr(row, key, value)
            session.add(row)
            await session.commit()


async def get_all_rows_by_user(tg_id: int):
    async with async_session() as session:
        subquery = select(User_x_Company).where(User_x_Company.user_id == tg_id).subquery()
        query = select(Company, subquery).join(subquery, Company.id == subquery.c.company_id)
        result = await session.execute(query)
        return result.all()
