from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    nth_uid = Column(String(30), unique=True, nullable=False)

    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    email = Column(String(120), unique=True, nullable=True)

    created_at = Column(DateTime, server_default=func.now())