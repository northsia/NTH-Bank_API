from unittest.mock import Base
from sqlalchemy import Column, DateTime, Integer, Numeric, String, func
from models.databases.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)

    from_account = Column(Integer, nullable=True)
    to_account = Column(Integer, nullable=True)

    amount = Column(Numeric(12, 2), nullable=False)

    type = Column(String(20))  # transfer / deposit / withdraw

    created_at = Column(DateTime, server_default=func.now())