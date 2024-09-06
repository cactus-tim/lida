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
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            data['tg_id'] = tg_id
            user_data = User(**data)
            session.add(user_data)
            await session.commit()
        else:
            print("Пользователь с таким id уже существует")


async def update_user(tg_id: int, data: dict):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            print("Пользователь с таким id не найден")
        else:
            for key, value in data.items():
                setattr(user, key, value)
            await session.commit()


async def get_users_tg_id():
    async with async_session() as session:
        users_tg_id = await session.execute(select(distinct(User.tg_id)))
        return users_tg_id.scalars().all()


async def get_company_by_name(company_name: str):
    async with async_session() as session:
        company = await session.scalar(select(Company).where(Company.name == company_name))
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
            await session.commit()


async def update_company_by_id(company_id: int, data: dict):
    async with async_session() as session:
        company = await get_company_by_id(company_id)
        if not company:
            print("Компания с таким id не найдена")
        else:
            for key, value in data.items():
                setattr(company, key, value)
            await session.commit()


async def get_user_x_company_row(tg_id: int, company_name: str):
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
