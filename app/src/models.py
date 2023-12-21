from sqlalchemy import Integer, String, Float
from sqlalchemy.sql.schema import Column
from src.database import Base


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, index=True)
    member_name = Column(String(20), unique=True)
    portfolio_value = Column(Float)
    age = Column(Integer)

    