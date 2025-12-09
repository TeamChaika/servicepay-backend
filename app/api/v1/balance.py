from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.balance import BalanceResponse, BalanceTopUp, BalanceTransactionResponse
from app.models.user import User
from app.models.balance import BalanceTransaction
from app.dependencies import get_current_user, get_current_active_owner
from app.services.billing_service import BillingService
from app.services.payment_service import PaymentService

router = APIRouter()


@router.get("/", response_model=BalanceResponse)
def get_balance(
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Получить баланс текущего пользователя"""
    balance = BillingService.get_balance(db, current_user.id)
    return balance


@router.post("/topup", response_model=dict, status_code=status.HTTP_201_CREATED)
async def topup_balance(
    topup_data: BalanceTopUp,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Пополнить баланс"""
    from app.schemas.payment import PaymentCreate
    
    # Создаем платеж для пополнения
    payment_data = PaymentCreate(
        payment_type="balance_topup",
        amount=topup_data.amount,
        description="Balance top-up",
        payer_email=current_user.email
    )
    
    payment = PaymentService.create_payment(
        db=db,
        payment_data=payment_data,
        user_id=str(current_user.id)
    )
    
    return {
        "payment_id": str(payment.id),
        "amount": payment.amount,
        "qr_url": payment.qr_url,
        "status": payment.status
    }


@router.get("/transactions", response_model=List[BalanceTransactionResponse])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Получить список транзакций"""
    balance = BillingService.get_balance(db, current_user.id)
    
    transactions = db.query(BalanceTransaction)\
        .filter(BalanceTransaction.balance_id == balance.id)\
        .order_by(BalanceTransaction.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return transactions

