from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.database import get_db
from app.schemas.payment import DepositCreate, PaymentResponse
from app.models.event import Event
from app.models.payment import Payment
from app.models.venue import Venue
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deposit(
    deposit_data: DepositCreate,
    db: Session = Depends(get_db)
):
    """Создать депозит для заведения (с опциональной привязкой к мероприятию)"""
    from app.models.venue import Venue
    
    # Проверяем существование заведения
    venue = db.query(Venue).filter(Venue.id == deposit_data.venue_id).first()
    
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    # ОБЯЗАТЕЛЬНАЯ проверка наличия активного СБП терминала
    from app.models.terminal import Terminal
    active_terminal = db.query(Terminal).filter(
        Terminal.venue_id == deposit_data.venue_id,
        Terminal.is_active == True
    ).first()
    
    if not active_terminal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно создать депозит: у заведения нет активного СБП терминала. Добавьте терминал для приёма оплат."
        )
    
    event = None
    
    # Формируем описание с деталями резервирования
    if deposit_data.reservation_date and deposit_data.reservation_time:
        description = f"Резервирование на {deposit_data.reservation_date} в {deposit_data.reservation_time}"
        if deposit_data.guests_count:
            description += f", гостей: {deposit_data.guests_count}"
        if deposit_data.description:
            description += f". {deposit_data.description}"
    else:
        description = deposit_data.description or "Deposit for venue reservation"
    
    # Сохраняем детали резервирования в extra_data
    extra_data = {}
    if deposit_data.reservation_date:
        extra_data['reservation_date'] = deposit_data.reservation_date
    if deposit_data.reservation_time:
        extra_data['reservation_time'] = deposit_data.reservation_time
    if deposit_data.guests_count:
        extra_data['guests_count'] = deposit_data.guests_count
    
    # Если указано мероприятие - проверяем его
    if deposit_data.event_id:
        event = db.query(Event).filter(
            Event.id == deposit_data.event_id,
            Event.venue_id == deposit_data.venue_id
        ).first()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found or does not belong to this venue"
            )
        
        description = f"Deposit for event: {event.title}"
        
        # Если у мероприятия есть требование депозита, проверяем сумму
        if event.deposit_required and event.deposit_amount:
            if deposit_data.amount != event.deposit_amount:
                # Предупреждение, но не блокируем
                description += f" (standard: {event.deposit_amount}, paid: {deposit_data.amount})"
    else:
        description = f"Deposit for {venue.name}"
        if deposit_data.description:
            description += f" - {deposit_data.description}"
    
    # Создаем платеж
    from app.schemas.payment import PaymentCreate
    
    payment_data = PaymentCreate(
        payment_type="deposit",
        amount=deposit_data.amount,
        event_id=deposit_data.event_id,
        payer_phone=deposit_data.payer_phone,
        payer_email=deposit_data.payer_email,
        payer_name=deposit_data.payer_name,
        description=description,
        extra_data=extra_data if extra_data else None
    )
    
    payment = PaymentService.create_payment(
        db=db,
        payment_data=payment_data,
        venue_id=str(deposit_data.venue_id)
    )
    
    # Добавляем публичную ссылку в ответ
    from app.config import settings
    payment_dict = PaymentResponse.model_validate(payment).model_dump()
    payment_dict['deposit_url'] = f"{settings.GUEST_PORTAL_URL}/deposit/{payment.id}"
    
    return payment_dict


@router.get("/{deposit_id}/public", response_model=dict)
async def get_deposit_public(
    deposit_id: UUID,
    db: Session = Depends(get_db)
):
    """Получить информацию о депозите (публичный endpoint без авторизации)"""
    payment = db.query(Payment).filter(
        Payment.id == deposit_id,
        Payment.payment_type == "deposit"
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )
    
    # Получаем информацию о заведении
    venue = db.query(Venue).filter(Venue.id == payment.venue_id).first()
    
    # Получаем информацию о мероприятии (если есть)
    event = None
    if payment.event_id:
        event = db.query(Event).filter(Event.id == payment.event_id).first()
    
    return {
        "id": str(payment.id),
        "status": payment.status,
        "amount": payment.amount,
        "total_amount": payment.total_amount,
        "commission": payment.commission,
        "description": payment.description,
        "qr_url": payment.qr_url,
        "qr_id": payment.qr_id,
        "created_at": payment.created_at.isoformat(),
        "expired_at": payment.expired_at.isoformat() if payment.expired_at else None,
        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
        "extra_data": payment.extra_data,
        "venue": {
            "id": str(venue.id),
            "name": venue.name,
            "address": venue.address,
            "phone": venue.phone
        } if venue else None,
        "event": {
            "id": str(event.id),
            "title": event.title,
            "description": event.description,
            "start_datetime": event.start_datetime.isoformat()
        } if event else None
    }

