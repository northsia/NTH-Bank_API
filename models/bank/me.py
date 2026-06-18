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
@router.get("/me")
@limiter.limit("50/minute")
async def me(
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    nth_uid = current_user["nth_uid"]

    db_user = db.query(User).filter(
        User.nth_uid == nth_uid
    ).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    account = db.query(Account).filter(
        Account.nth_uid == nth_uid
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "user": {
            "nth_uid": db_user.nth_uid,
            "username": db_user.username,
            "email": db_user.email 
        },
        "account": {
            "balance": float(account.balance),
            "currency": account.currency,
            "status": account.status
        }
    }