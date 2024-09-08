from sqlalchemy import Column, DateTime, Integer, String, Boolean, ARRAY, Text, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from datetime import datetime

from bot.bot_instance import SQL_URL_RC

engine = create_async_engine(url=SQL_URL_RC,
                             echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    tg_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="")
    surname = Column(String, default="")
    tel = Column(String, nullable=False, unique=True)
    email = Column(String, default="")
    company_name = Column(String,  default="")
    jobtitle = Column(String, default="")
    product_name = Column(String, default="")
    product_description = Column(String, default="")
    problem_solved = Column(String, default="")
    scope_company = Column(String, default="")
    what_creating = Column(String, default="")
    number_years_existence = Column(Integer, default=0)
    number_employees = Column(Integer, default=0)
    revenue_last_year = Column(Integer, default=0)
    life_cycle_stage = Column(String, default="")
    target_okveds = Column(ARRAY, default=[])
    target_number_employees = Column(ARRAY, default=[])
    target_number_years_existence = Column(ARRAY, default=[])
    target_revenue_last_year = Column(ARRAY, default=[])
    target_jobtitle = Column(String, default="")
    is_active = Column(Boolean, default=False)
    cnt = Column(Integer, default=0)
    # past_using_time = Column(DateTime, default=datetime.utcnow)


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, default="")
    okveds = Column(ARRAY)
    inn = Column(Integer, default=0)
    number_employees = Column(Integer, default=0)
    number_years_existence = Column(Integer, default=0)
    revenue_last_year = Column(Integer, default=0)
    registration_form = Column(Integer, default=0)
    description = Column(String, default="")
    company_mail = Column(String, default="")
    company_tel = Column(String, default="")
    site = Column(String, default="")
    lpr_name = Column(String, default="")
    lpr_jobtitle = Column(String, default="")
    lpr_mail = Column(String, default="")
    lpr_tel = Column(String, default="")


class User_x_Company(Base):
    __tablename__ = "user_x_company"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    company_id = Column(Integer, nullable=False)
    status = Column(String, default="requested")
    comment = Column(String, default="")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
