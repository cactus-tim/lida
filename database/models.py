from sqlalchemy import Column, Integer, String, Boolean, ARRAY, BigInteger, ForeignKey, Float, Numeric, JSON, Text
from sqlalchemy.dialects.mysql import FLOAT
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from bot_instance import SQL_URL_RC

engine = create_async_engine(url=SQL_URL_RC, echo=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    tg_id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, default="")
    surname = Column(String, default="")
    tel = Column(String, unique=True)
    email = Column(String, default="")
    company_name = Column(String,  default="")
    jobtitle = Column(String, default="")
    product_name = Column(String, default="")
    product_description = Column(String, default="")
    problem_solved = Column(String, default="")
    # scope_company = Column(String, default="")
    # what_creating = Column(String, default="")
    # number_years_existence = Column(Integer, default=0)
    # number_employees = Column(Integer, default=0)
    # revenue_last_year = Column(Numeric, default=0)
    # life_cycle_stage = Column(String, default="")
    target_okveds = Column(ARRAY(String), default=list)
    target_number_employees = Column(ARRAY(Integer), default=list)
    target_number_years_existence = Column(ARRAY(Integer), default=list)
    target_revenue_last_year = Column(ARRAY(Numeric), default=list)
    target_jobtitle = Column(ARRAY(String), default="")
    is_active = Column(Boolean, default=False)
    cnt = Column(Integer, default=0)
    thread = Column(String, default='')
    # past_using_time = Column(DateTime, default=datetime.utcnow)

    companies = relationship("User_x_Company", back_populates="user")


class Company(Base):
    __tablename__ = "сompany"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String, default="")
    okveds = Column(ARRAY(String), default=list)
    inn = Column(BigInteger, default=0)
    number_employees = Column(Integer, default=0)
    number_years_existence = Column(Integer, default=0)
    revenue_last_year = Column(Numeric, default=0)
    registration_form = Column(Integer, default=0)
    description = Column(String, default="")
    company_mail = Column(String, default="")
    company_tel = Column(String, default="")
    site = Column(String, default="")
    lpr_name = Column(String, default="")
    lpr_jobtitle = Column(String, default="")
    lpr_mail = Column(String, default="")
    lpr_tel = Column(String, default="")

    users = relationship("User_x_Company", back_populates="сompany")


class User_x_Company(Base):
    __tablename__ = "user_x_сompany"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.tg_id"), nullable=False)
    company_id = Column(Integer, ForeignKey("сompany.id"), nullable=False)
    status = Column(String, default="requested")
    comment = Column(JSON, default="")

    user = relationship("User", back_populates="сompanies")
    company = relationship("Company", back_populates="users")


async def async_main():
    async with engine.begin() as conn:
        await сonn.run_sync(Base.metadata.create_all)