from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Request
from passlib.context import CryptContext

from models.databases.database import SessionLocal
from models.auth.user import User
from models.bank.account import Account
from models.security.jwt import create_token
from models.auth.nthid import genth
from models.security.ratelimiter import limiter


router = APIRouter(prefix="/api/v1/nth/auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str = Field(min_length=4)


@router.post("/register")
@limiter.limit("10/minute")
async def register(request: Request, data: RegisterRequest):

    db = SessionLocal()

    try:
        first_name = data.first_name.strip().lower()
        last_name = data.last_name.strip().lower()
        email = data.email.strip().lower()
        password = data.password

        # check email exists
        existing = db.query(User).filter(
            User.email == email
        ).first()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Email already exists"
            )

        hashed_password = pwd_context.hash(password)

        user = User(
            nth_uid=genth(),
            username=f"{first_name} {last_name}",
            email=email,
            password=hashed_password
        )

        db.add(user)
        db.flush()

        account = Account(
            nth_uid=user.nth_uid,
            balance=0,
            currency="USD",
            status="active"
        )

        db.add(account)
        db.commit()

        token = create_token(
            nth_uid=user.nth_uid,
            username=user.username,
            email=user.email
        )

        return {
            "success": True,
            "token": token,
            "user": {
                "username": user.username,
                "nth_uid": user.nth_uid,
                "email": user.email
            },
            "account": {
                "balance": float(account.balance),
                "currency": account.currency,
                "status": account.status
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()