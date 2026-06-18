from sqlalchemy import Column, DateTime, Integer, Numeric, String, func
from models.databases.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)

    from_nth_uid = Column(String(30), nullable=False)
    to_nth_uid = Column(String(30), nullable=False)

    amount = Column(Numeric(12, 2), nullable=False)

    type = Column(String(20))  # transfer / deposit / withdraw

    status = Column(String(20), default="success")

    created_at = Column(DateTime, server_default=func.now())