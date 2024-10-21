from sqlalchemy import select, desc, distinct, and_

from database.models import User, Company, User_x_Company, async_session, Acc
from error_handlers.errors import *
from error_handlers.handlers import db_error_handler

@db_error_handler
async def get_user(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return user
        else:
            return "not created"


@db_error_handler
async def get_thread(tg_id: int) -> str:
    async with async_session() as session:
        user = await get_user(tg_id)
        if user:
            return user.thread
        else:
            raise Error404


@db_error_handler
async def create_user(tg_id: int, data: dict):
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == 'not created':
            data['tg_id'] = tg_id
            user_data = User(**data)
            session.add(user_data)
            await session.commit()
        else:
            raise Error409


@db_error_handler
async def update_user(tg_id: int, data: dict):
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == 'not created':
            raise Error404
        else:
            for key, value in data.items():
                setattr(user, key, value)
            session.add(user)
            await session.commit()


@db_error_handler
async def get_users_tg_id():
    async with async_session() as session:
        users_tg_id = await session.execute(select(distinct(User.tg_id)))
        users_tg_ids = users_tg_id.scalars().all()
        if len(users_tg_ids) == 0:
            raise Error404
        return users_tg_ids


@db_error_handler
async def get_company_by_name(company_name: str):
    async with async_session() as session:
        company = await session.scalar(select(Company).where(Company.company_name == company_name))
        if company:
            return company
        else:
            return 'not created'


@db_error_handler
async def get_company_by_id(company_id: int):
    async with async_session() as session:
        company = await session.scalar(select(Company).where(Company.id == company_id))
        if company:
            return company
        else:
            return 'not created'


@db_error_handler
async def create_company(data: dict):   # in data must be company_name
    async with async_session() as session:
        if data.get('company_name', 0) == 0:
            raise CompanyNameError
        company = await get_company_by_name(data['company_name'])
        if company == 'not created':
            company_data = Company(**data)
            session.add(company_data)
            await session.commit()
        else:
            raise Error409


@db_error_handler
async def update_company_by_name(company_name: str, data: dict):
    async with async_session() as session:
        company = await get_company_by_name(company_name)
        if company == 'not created':
            raise Error404
        else:
            for key, value in data.items():
                setattr(company, key, value)
            session.add(company)
            await session.commit()


@db_error_handler
async def update_company_by_id(company_id: int, data: dict):
    async with async_session() as session:
        company = await get_company_by_id(company_id)
        if not company:
            raise Error404
        else:
            for key, value in data.items():
                setattr(company, key, value)
            session.add(company)
            await session.commit()


@db_error_handler
async def get_one_company(tg_id: int):
    async with async_session() as session:
        user = await get_user(tg_id)
        if not user:
            raise Error404

        #  TODO: check invariant(company + user clearly defines row id)
        #  TODO: check invariant(company clearly defines row id)

        subquery = select(User_x_Company.company_id).where(User_x_Company.user_id == tg_id).subquery()
        query = select(Company).outerjoin(subquery, Company.id == subquery.c.company_id).where(subquery.c.company_id.is_(None))

        # if len(user.target_okveds) > 0 and user.target_okveds[0] != '0':
        #     query = query.where(Company.okveds.in_(user.target_okveds))

        if len(user.target_number_employees) > 0 and user.target_number_employees[0] != 0:
            if len(user.target_number_employees) == 1:
                query = query.where(
                    and_(Company.number_employees >= user.target_number_employees[0]/4,
                         Company.number_employees <= user.target_number_employees[0]*4)
                )
            elif len(user.target_number_employees) >= 2:
                query = query.where(
                    and_(Company.number_employees >= user.target_number_employees[0]/2,
                         Company.number_employees <= user.target_number_employees[-1]*2)
                )

        if len(user.target_number_years_existence) > 0 and user.target_number_years_existence[0] != 0:
            if len(user.target_number_years_existence) == 1:
                query = query.where(
                    and_(Company.number_years_existence >= user.target_number_years_existence[0]/4,
                         Company.number_employees <= user.target_number_years_existence[0]*4)
                )
            elif len(user.target_number_years_existence) >= 2:
                query = query.where(
                    and_(Company.number_years_existence >= user.target_number_years_existence[0]/2,
                         Company.number_years_existence <= user.target_number_years_existence[-1]*2)
                )

        if len(user.target_revenue_last_year) > 0 and user.target_revenue_last_year[0] != 0:  # need to check
            if len(user.target_revenue_last_year) == 1:
                query = query.where(
                    and_(Company.revenue_last_year >= user.target_revenue_last_year[0]/4,
                         Company.revenue_last_year <= user.target_revenue_last_year[0]*4)
                )
            elif len(user.target_revenue_last_year) >= 2:
                query = query.where(
                    and_(Company.revenue_last_year >= user.target_revenue_last_year[0]/2,
                         Company.revenue_last_year <= user.target_revenue_last_year[-1]*2)
                )

        result = await session.execute(query)
        data = result.scalars().first()
        if data:
            return data
        else:
            await update_user(tg_id, {'cnt': 0, 'is_active': True})
            raise FilterError(tg_id)


@db_error_handler
async def get_user_x_company_row_by_name(tg_id: int, company_name: str):
    async with async_session() as session:
        company = await get_company_by_name(company_name)
        if company == 'not created':
            raise Error404
        company_id = company['id']
        row = await session.scalar(select(User_x_Company)
                                   .where(and_(User_x_Company.tg_id == tg_id, User_x_Company.id == company_id)))
        if row:
            return row
        else:
            raise Error404


@db_error_handler
async def get_user_x_company_row_by_id(tg_id: int, company_id: int):
    async with async_session() as session:
        row = await session.scalar(select(User_x_Company).where(and_(User_x_Company.user_id == tg_id, User_x_Company.company_id == company_id)))
        if row:
            return row
        else:
            raise Error404


@db_error_handler
async def create_user_x_row_by_id(tg_id: int, company_id: int):
    async with async_session() as session:
        row = await get_user_x_company_row_by_id(tg_id, company_id)
        if not row:
            acc_id = await get_best_acc_id()
            row = User_x_Company(user_id=tg_id, company_id=company_id, acc_id=acc_id)
            session.add(row)
            await session.commit()
        else:
            raise Error409


@db_error_handler
async def update_user_x_row_by_id(tg_id: int, company_id: int, data):
    async with async_session() as session:
        row = await get_user_x_company_row_by_id(tg_id, company_id)
        if not row:
            raise Error404
        else:
            for key, value in data.items():
                setattr(row, key, value)
            session.add(row)
            await session.commit()


@db_error_handler
async def get_user_x_row_by_status(tg_id: int, status: str):
    async with async_session() as session:
        row = await session.scalar(select(User_x_Company)
                                   .where(and_(User_x_Company.user_id == tg_id, User_x_Company.status == status))
                                   .order_by(desc(User_x_Company.id)))
        if row:
            return row
        else:
            raise Error404


@db_error_handler
async def update_user_x_row_by_status(tg_id: int, status: str, data: dict):
    async with async_session() as session:
        row = await get_user_x_row_by_status(tg_id, status)
        if not row:
            raise Error404
        else:
            for key, value in data.items():
                setattr(row, key, value)
            session.add(row)
            await session.commit()


@db_error_handler
async def get_all_rows_by_user(tg_id: int):
    async with async_session() as session:
        subquery = select(User_x_Company).where(User_x_Company.user_id == tg_id).subquery()
        query = select(Company, subquery).join(subquery, Company.id == subquery.c.company_id)
        result = await session.execute(query)
        res = result.all()
        if len(res) == 0:
            raise Error404
        return res


@db_error_handler
async def get_all_rows_w_date(date):
    async with async_session() as session:
        subquery = select(User_x_Company).where(User_x_Company.date == date).subquery()
        query = select(Company, subquery).join(subquery, Company.id == subquery.c.company_id)
        result = await session.execute(query)
        res = result.all()
        if len(res) == 0:
            return []
        return res


@db_error_handler
async def get_all_rows_by_user_w_date(tg_id: int, date):
    async with async_session() as session:
        subquery = select(User_x_Company).where(
            and_(
                User_x_Company.user_id == tg_id,
                User_x_Company.date == date
            )).subquery()
        query = select(Company, subquery).join(subquery, Company.id == subquery.c.company_id)
        result = await session.execute(query)
        res = result.all()
        if len(res) == 0:
            raise Error404
        return res


@db_error_handler
async def get_acc(id: int):
    async with async_session() as session:
        acc = await session.scalar(select(Acc).where(Acc.id == id))
        if acc:
            return acc
        else:
            raise Error404


@db_error_handler
async def get_acc_by_email(email: str):
    async with async_session() as session:
        acc = await session.scalar(select(Acc).where(Acc.email == email))
        if acc:
            return acc
        else:
            return 'not created'


@db_error_handler
async def get_best_acc_id():
    async with async_session() as session:
        best_acc = await session.scalar(select(Acc).order_by(Acc.in_use))
        if best_acc:
            return best_acc.id
        else:
            raise Error404


@db_error_handler
async def create_acc(data: dict):
    async with async_session() as session:
        if data.get('email', 0) == 0:
            raise ZeroEmailError
        if data.get('password', 0) == 0:
            raise ZeroPassError
        acc = await get_acc_by_email(data['email'])
        if acc == 'not created':
            acc_data = Acc(**data)
            session.add(acc_data)
            await session.commit()
        else:
            raise Error409


@db_error_handler
async def update_acc(id: int, data: dict):
    async with async_session() as session:
        acc = await get_acc(id)
        for key, value in data.items():
            setattr(acc, key, value)
        session.add(acc)
        await session.commit()

