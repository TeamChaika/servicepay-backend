from sqlalchemy.orm import Session
from app.models.balance import Balance, BalanceTransaction, TransactionType
from app.models.user import User
from fastapi import HTTPException, status
from typing import Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class BillingService:
    @staticmethod
    def get_balance(db: Session, user_id: UUID) -> Balance:
        balance = db.query(Balance).filter(Balance.user_id == user_id).first()
        if not balance:
            # Создаем баланс если его нет
            balance = Balance(user_id=user_id)
            db.add(balance)
            db.commit()
            db.refresh(balance)
        return balance
    
    @staticmethod
    def add_funds(
        db: Session,
        user_id: UUID,
        amount: int,
        transaction_type: TransactionType = TransactionType.TOPUP,
        description: Optional[str] = None,
        reference_id: Optional[UUID] = None
    ) -> Balance:
        balance = BillingService.get_balance(db, user_id)
        
        balance_before = balance.amount
        balance.amount += amount
        balance_after = balance.amount
        
        # Создаем транзакцию
        transaction = BalanceTransaction(
            balance_id=balance.id,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            reference_id=reference_id
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(balance)
        
        logger.info(f"Added {amount} to user {user_id} balance")
        return balance
    
    @staticmethod
    def deduct_funds(
        db: Session,
        user_id: UUID,
        amount: int,
        transaction_type: TransactionType = TransactionType.PAYMENT,
        description: Optional[str] = None,
        reference_id: Optional[UUID] = None
    ) -> Balance:
        balance = BillingService.get_balance(db, user_id)
        
        if balance.amount < amount:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Insufficient balance"
            )
        
        balance_before = balance.amount
        balance.amount -= amount
        balance_after = balance.amount
        
        # Создаем транзакцию
        transaction = BalanceTransaction(
            balance_id=balance.id,
            transaction_type=transaction_type,
            amount=-amount,  # Отрицательное значение для списания
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            reference_id=reference_id
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(balance)
        
        logger.info(f"Deducted {amount} from user {user_id} balance")
        return balance
    
    @staticmethod
    def check_low_balance(db: Session, user_id: UUID) -> bool:
        from app.config import settings
        balance = BillingService.get_balance(db, user_id)
        return balance.amount < settings.LOW_BALANCE_THRESHOLD

