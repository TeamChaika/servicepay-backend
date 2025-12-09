from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentStatusUpdate
from app.models.user import User
from app.dependencies import get_current_user
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новый платеж"""
    payment = PaymentService.create_payment(
        db=db,
        payment_data=payment_data,
        user_id=str(current_user.id)
    )
    
    return payment


@router.get("/", response_model=List[PaymentResponse])
def list_payments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список платежей текущего пользователя"""
    from app.models.payment import Payment
    
    query = db.query(Payment).filter(Payment.user_id == current_user.id)
    
    if status:
        query = query.filter(Payment.status == status)
    
    payments = query.offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить информацию о платеже"""
    payment = PaymentService.get_payment(db, str(payment_id))
    
    # Проверка доступа
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return payment


@router.put("/{payment_id}/status", response_model=PaymentResponse)
def update_payment_status(
    payment_id: UUID,
    status_data: PaymentStatusUpdate,
    db: Session = Depends(get_db)
):
    """Обновить статус платежа (для webhooks)"""
    from app.models.payment import PaymentStatus
    
    payment = PaymentService.update_payment_status(
        db=db,
        payment_id=str(payment_id),
        status=PaymentStatus(status_data.status),
        external_id=status_data.external_id
    )
    
    return payment

