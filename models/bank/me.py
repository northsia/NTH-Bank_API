from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from models.databases.database import SessionLocal
from models.auth.user import User
from models.bank.account import Account
from models.security.deps import get_current_user
from models.security.ratelimiter import limiter

router = APIRouter(prefix="/api/v1/nth/account")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/me")
@limiter.limit("50/minute")
async def me(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
    ):

    user_id = user["user_id"]

    # get user
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(404, "User not found")

    # get account
    account = db.query(Account).filter(Account.user_id == user_id).first()

    if not account:
        raise HTTPException(404, "Account not found")

    return {
        "user": {
            "id": db_user.id,
            "username": db_user.username
        },
        "account": {
            "balance": float(account.balance),
            "currency": account.currency,
            "status": account.status
        }
    }