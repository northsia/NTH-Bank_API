from sqlalchemy import Column, Integer, String, Numeric
from models.databases.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)

    balance = Column(Numeric(12, 2), default=0)

    currency = Column(String(3), default="USD")
    status = Column(String(20), default="active")