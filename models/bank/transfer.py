import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from decimal import Decimal

from models.security.deps import get_current_user
from models.databases.database import SessionLocal
from models.bank.account import Account
from models.bank.transaction import Transaction


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/nth/bank/transfer")


# ---------------------------
# CONFIG
# ---------------------------
MAX_TRANSFER_AMOUNT = Decimal("100000.00")


# ---------------------------
# REQUEST MODEL
# ---------------------------
class TransferRequest(BaseModel):
    to_nth_uid: str
    amount: Decimal = Field(gt=0, le=MAX_TRANSFER_AMOUNT)


# ---------------------------
# DB SESSION
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# TRANSFER ENDPOINT
# ---------------------------
@router.post("/", status_code=200)
async def transfer(
    data: TransferRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from_nth_uid = current_user["nth_uid"]

    if from_nth_uid == data.to_nth_uid:
        raise HTTPException(400, "Cannot transfer to yourself")

    # Lock both accounts in one query
    accounts = (
        db.query(Account)
        .filter(Account.nth_uid.in_([from_nth_uid, data.to_nth_uid]))
        .with_for_update()
        .all()
    )

    account_map = {a.nth_uid: a for a in accounts}
    sender   = account_map.get(from_nth_uid)
    receiver = account_map.get(data.to_nth_uid)

    if not sender or not receiver:
        raise HTTPException(404, "Account not found")

    if sender.balance < data.amount:
        raise HTTPException(400, "Insufficient balance")

    try:
        sender.balance   -= data.amount
        receiver.balance += data.amount

        tx = Transaction(
            from_nth_uid=from_nth_uid,
            to_nth_uid=data.to_nth_uid,
            amount=data.amount,
            type="transfer"
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)

    except Exception as e:
        db.rollback()
        logger.exception("Transfer failed")
        raise HTTPException(500, "Transfer failed, please try again")

    return {
        "success": True,
        "transaction_id": tx.id,
        "sender_balance": str(sender.balance)
    }