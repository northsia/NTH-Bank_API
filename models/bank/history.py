from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.bank.account import Account
from models.bank.transaction import Transaction
from models.security.deps import get_current_user
from models.security.ratelimiter import limiter
from models.bank.transfer import get_db

router = APIRouter(prefix="/api/v1/nth/account")


@router.get("/history")
@limiter.limit("50/minute")
def get_history(
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    nth_uid = current_user["nth_uid"]

    # get transactions by nth_uid
    txs = (
        db.query(Transaction)
        .filter(
            or_(
                Transaction.from_nth_uid == nth_uid,
                Transaction.to_nth_uid == nth_uid
            )
        )
        .order_by(Transaction.created_at.desc())
        .all()
    )

    return [
        {
            "id": tx.id,
            "direction": (
                "outgoing"
                if tx.from_nth_uid == nth_uid
                else "incoming"
            ),
            "amount": float(tx.amount),
            "status": tx.status,
            "created_at": tx.created_at,
            "from": tx.from_nth_uid,
            "to": tx.to_nth_uid
        }
        for tx in txs
    ]