from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from passlib.context import CryptContext

from models.databases.database import SessionLocal
from models.security.ratelimiter import limiter

from models.auth.user import User
from models.security.jwt import create_token



router = APIRouter(prefix="/api/v1/nth/auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    username: str = Field(min_length=4)
    password: str = Field(min_length=4)


@router.post("/login")
@limiter.limit("20/minute")
async def login(request: Request, data: LoginRequest):

    username = data.username.strip()
    password = data.password

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        if not pwd_context.verify(password, user.password):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        token = create_token(
            user_id=user.id,
            username=user.username
        )

        return {
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username
            },
            "balance": user.balance
        }

    finally:
        db.close()