from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.refund import RefundCreate, RefundUpdate, RefundResponse
from app.models.refund import Refund
from app.models.payment import Payment
from app.models.user import User
from app.dependencies import get_current_user, get_current_active_owner

router = APIRouter()


@router.post("/", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
def create_refund(
    refund_data: RefundCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать запрос на возврат"""
    # Проверяем платеж
    payment = db.query(Payment).filter(Payment.id == refund_data.payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Проверяем, нет ли уже возврата
    existing_refund = db.query(Refund).filter(Refund.payment_id == refund_data.payment_id).first()
    
    if existing_refund:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund already exists for this payment"
        )
    
    # Создаем возврат
    refund = Refund(
        payment_id=refund_data.payment_id,
        amount=refund_data.amount,
        reason=refund_data.reason
    )
    
    db.add(refund)
    db.commit()
    db.refresh(refund)
    
    return refund


@router.get("/", response_model=List[RefundResponse])
def list_refunds(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список возвратов"""
    refunds = db.query(Refund).join(Payment).filter(
        Payment.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return refunds


@router.get("/{refund_id}", response_model=RefundResponse)
def get_refund(
    refund_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить информацию о возврате"""
    refund = db.query(Refund).join(Payment).filter(
        Refund.id == refund_id
    ).first()
    
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund not found"
        )
    
    if refund.payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return refund


@router.put("/{refund_id}", response_model=RefundResponse)
def update_refund(
    refund_id: UUID,
    refund_data: RefundUpdate,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Обновить статус возврата (только для владельца)"""
    refund = db.query(Refund).filter(Refund.id == refund_id).first()
    
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund not found"
        )
    
    refund.status = refund_data.status
    if refund_data.admin_notes:
        refund.admin_notes = refund_data.admin_notes
    
    from datetime import datetime
    from app.models.refund import RefundStatus
    
    if refund_data.status in [RefundStatus.APPROVED, RefundStatus.PROCESSING]:
        refund.processed_at = datetime.utcnow()
    
    if refund_data.status == RefundStatus.COMPLETED:
        refund.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(refund)
    
    return refund

