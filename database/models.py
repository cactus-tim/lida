from sqlalchemy import Column, DateTime, Integer, String, Text, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from datetime import datetime

from bot.bot_instance import SQL_URL_RC

engine = create_async_engine(url=SQL_URL_RC,
                             echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserOrm(Base):
    __tablename__ = "users"

    telegram_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="")
    surname = Column(String, default="")
    tel = Column(String(20), nullable=False, unique=True)
    email = Column(String, default="")
    company_name = Column(String,  default="")
    role_in_company = Column(String, default="")
    # count_answer_past_day = Column(Integer, default=0)
    # past_using_time = Column(DateTime, default=datetime.utcnow)


class ProductOrm(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False, unique=True)
    product_name = Column(String, default="")
    product_description = Column(String, default="")
    problem_solved = Column(String, default="")
    price = Column(Integer, default=0)

    def to_dict(self):
        return {
            "telegram_id": self.telegram_id,
            "product_name": self.product_name,
            "product_description": self.product_description,
            "problem_solved": self.problem_solved,
            "price": self.price,
        }


class CompanyOrm(Base):
    __tablename__ = "user_company"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False, unique=True)
    scope_company = Column(String, default="")
    what_creating = Column(String, default="")
    number_years_existence = Column(Integer, default=0)
    number_employees = Column(Integer, default=0)
    revenue_last_year = Column(Integer, default=0)
    life_cycle_stage = Column(String, default="")
    contact_company_for_sale = Column(String, default="")

    def to_dict(self):
        return {
            "telegram_id": self.telegram_id,
            "scope_company": self.scope_company,
            "what_creating": self.what_creating,
            "number_years_existence": self.number_years_existence,
            "number_employees": self.number_employees,
            "revenue_last_year": self.revenue_last_year,
            "life_cycle_stage": self.life_cycle_stage,
            "contact_company_for_sale": self.contact_company_for_sale,
        }


class TargetCompanyOrm(Base):
    __tablename__ = "target_company"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False, unique=True)
    scope_company = Column(String, default="")
    what_creating = Column(String, default="")
    number_years_existence = Column(Integer, default=0)
    number_employees = Column(Integer, default=0)
    revenue_last_year = Column(Integer, default=0)
    life_cycle_stage = Column(String, default="")
    contact_company_for_sale = Column(String, default="")

    def to_dict(self):
        return {
            "telegram_id": self.telegram_id,
            "scope_company": self.scope_company,
            "what_creating": self.what_creating,
            "number_years_existence": self.number_years_existence,
            "number_employees": self.number_employees,
            "revenue_last_year": self.revenue_last_year,
            "life_cycle_stage": self.life_cycle_stage,
            "contact_company_for_sale": self.contact_company_for_sale,
        }


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
