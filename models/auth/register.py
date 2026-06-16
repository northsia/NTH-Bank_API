from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request
from passlib.context import CryptContext

from models.databases.database import SessionLocal
from models.auth.user import User
from models.bank.account import Account
from models.security.jwt import create_token

from models.security.ratelimiter import limiter


router = APIRouter(prefix="/api/v1/nth/auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)


@router.post("/register")
@limiter.limit("10/minute")
async def register(request: Request, data: RegisterRequest):

    db = SessionLocal()

    try:
        username = data.username.strip().lower()

        # check exists
        existing = db.query(User).filter(
            User.username == username
        ).first()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Username already exists"
            )

        # hash password
        hashed_password = pwd_context.hash(data.password)

        # create user
        user = User(
            username=username,
            password=hashed_password
        )

        db.add(user)
        db.flush()

        # create account
        account = Account(
            user_id=user.id,
            balance=0,
            currency="USD",
            status="active"
        )

        db.add(account)
        db.commit()

        token = create_token(user.id, user.username)

        return {
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username
            }
        }

    except HTTPException as e:
        db.rollback()
        raise e

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )

    finally:
        db.close()