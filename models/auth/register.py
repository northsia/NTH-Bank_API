import hashlib
import base64

from pydantic import BaseModel, Field, field_validator
from fastapi import APIRouter, HTTPException, Request
from passlib.context import CryptContext

from models.databases.database import SessionLocal
from models.auth.user import User
from models.bank.account import Account
from models.security.jwt import create_token
from models.auth.nthid import genth
from models.security.ratelimiter import limiter

router = APIRouter(prefix="/api/v1/nth/auth")

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """Hash password via SHA-256 first to avoid bcrypt's 72-byte limit."""
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    safe = base64.b64encode(digest).decode("utf-8")  # always 44 chars
    return pwd_context.hash(safe)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify password using the same SHA-256 + bcrypt pipeline."""
    digest = hashlib.sha256(plain.encode("utf-8")).digest()
    safe = base64.b64encode(digest).decode("utf-8")
    return pwd_context.verify(safe, hashed)


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=4, max_length=128)

    @field_validator("password")
    @classmethod
    def password_byte_limit(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 500:
            raise ValueError("Password is too long")
        return v


@router.post("/register")
@limiter.limit("10/minute")
async def register(request: Request, data: RegisterRequest):

    db = SessionLocal()

    try:
        first_name = data.first_name.strip()
        last_name = data.last_name.strip()
        email = data.email.strip().lower()
        password = data.password

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Email already exists"
            )

        hashed_password = hash_password(password)

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

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )

    finally:
        db.close()
