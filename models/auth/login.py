from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from passlib.context import CryptContext

from models.databases.database import SessionLocal
from models.security.ratelimiter import limiter

from models.auth.user import User
from models.security.jwt import create_token
from models.bank.account import Account


router = APIRouter(prefix="/api/v1/nth/auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    email: str = Field(min_length=4)
    password: str = Field(min_length=4)


@router.post("/login")
async def login(data: LoginRequest):

    db = SessionLocal()

    try:
        email = data.email.strip().lower()
        password = data.password

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(401, "Invalid email or password")

        if not pwd_context.verify(password, user.password):
            raise HTTPException(401, "Invalid email or password")
        

        token = create_token(
            nth_uid=user.nth_uid,
            email=user.email,
            username=user.username
        )

        account = db.query(Account).filter(
            Account.nth_uid == user.nth_uid
        ).first()

        if not account:
            account = Account(
                nth_uid=user.nth_uid,
                balance=0,
                currency="USD",
                status="active"
            )
            db.add(account)
            db.commit()
            db.refresh(account)

        return {
            "success": True,
            "token": token,
            "user": {
                "email": user.email,
                "nth_uid": user.nth_uid
            },
            "account": {
                "balance": float(account.balance),
                "currency": account.currency,
                "status": account.status
            }
        }

    finally:
        db.close()