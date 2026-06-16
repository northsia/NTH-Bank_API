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

router = APIRouter(prefix="/api/v1/nth/transfer")


# ---------------------------
# CONFIG
# ---------------------------
MAX_TRANSFER_AMOUNT = Decimal("1000000.00")


# ---------------------------
# REQUEST MODEL
# ---------------------------
class TransferRequest(BaseModel):
    to_user_id: int = Field(gt=0)
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
@router.post("/", status_code=status.HTTP_200_OK)
async def transfer(
    data: TransferRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    from_user_id = user["user_id"]

    # ---------------------------
    # 1. prevent self transfer
    # ---------------------------
    if from_user_id == data.to_user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot transfer to yourself"
        )

    # ---------------------------
    # 2. lock accounts (deadlock safe)
    # ---------------------------
    ids_in_order = sorted([from_user_id, data.to_user_id])

    accounts = (
        db.query(Account)
        .filter(Account.user_id.in_(ids_in_order))
        .order_by(Account.user_id)
        .with_for_update()
        .all()
    )

    account_map = {acc.user_id: acc for acc in accounts}

    sender = account_map.get(from_user_id)
    receiver = account_map.get(data.to_user_id)

    # ---------------------------
    # 3. validations
    # ---------------------------
    if not sender or not receiver:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    if sender.status != "active":
        raise HTTPException(
            status_code=403,
            detail="Sender account is not active"
        )

    if receiver.status != "active":
        raise HTTPException(
            status_code=403,
            detail="Receiver account is not active"
        )

    if sender.balance < data.amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    # ---------------------------
    # 4. atomic transfer
    # ---------------------------
    try:
        sender.balance -= data.amount
        receiver.balance += data.amount

        tx = Transaction(
            from_account=sender.id,
            to_account=receiver.id,
            amount=data.amount,
            type="transfer"
        )

        db.add(tx)
        db.commit()
        db.refresh(tx)

        logger.info(
            "Transfer success: from_user=%s to_user=%s amount=%s tx_id=%s",
            from_user_id,
            data.to_user_id,
            data.amount,
            tx.id,
        )

        return {
            "success": True,
            "transaction_id": tx.id,
            "amount": str(data.amount),
            "new_balance": str(sender.balance)
        }

    except Exception:
        db.rollback()

        logger.exception(
            "Transfer failed: from_user=%s to_user=%s amount=%s",
            from_user_id,
            data.to_user_id,
            data.amount,
        )

        raise HTTPException(
            status_code=500,
            detail="Transfer failed. Please try again later."
        )