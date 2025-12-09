from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID, uuid4
from app.database import get_db
from app.schemas.ticket import TicketPurchase, TicketResponse, TicketVerify
from app.models.ticket import Ticket, TicketType, TicketStatus
from app.models.event import Event
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/purchase", response_model=List[TicketResponse], status_code=status.HTTP_201_CREATED)
async def purchase_tickets(
    purchase_data: TicketPurchase,
    db: Session = Depends(get_db)
):
    """Купить билеты на мероприятие"""
    # Проверяем мероприятие
    event = db.query(Event).filter(Event.id == purchase_data.event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if not event.tickets_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tickets are not enabled for this event"
        )
    
    # Проверяем тип билета
    ticket_type = db.query(TicketType).filter(
        TicketType.id == purchase_data.ticket_type_id,
        TicketType.event_id == purchase_data.event_id
    ).first()
    
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket type not found"
        )
    
    if not ticket_type.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This ticket type is not available"
        )
    
    # Проверяем доступность
    available = ticket_type.quantity - ticket_type.sold
    if available < purchase_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {available} tickets available"
        )
    
    # TODO: Создать платеж и после успешной оплаты создать билеты
    # Сейчас создаем билеты напрямую
    
    tickets = []
    for i in range(purchase_data.quantity):
        ticket = Ticket(
            event_id=purchase_data.event_id,
            ticket_type_id=purchase_data.ticket_type_id,
            ticket_code=str(uuid4())[:8].upper(),
            guest_name=purchase_data.guest_name,
            guest_email=purchase_data.guest_email,
            guest_phone=purchase_data.guest_phone
        )
        db.add(ticket)
        tickets.append(ticket)
    
    # Обновляем количество проданных билетов
    ticket_type.sold += purchase_data.quantity
    event.tickets_sold += purchase_data.quantity
    
    db.commit()
    
    for ticket in tickets:
        db.refresh(ticket)
    
    return tickets


@router.get("/", response_model=List[TicketResponse])
def list_my_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список билетов текущего пользователя"""
    tickets = db.query(Ticket).filter(Ticket.guest_id == current_user.id).all()
    return tickets


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    """Получить информацию о билете"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    return ticket


@router.post("/verify")
def verify_ticket(
    verify_data: TicketVerify,
    db: Session = Depends(get_db)
):
    """Проверить валидность билета"""
    ticket = db.query(Ticket).filter(Ticket.ticket_code == verify_data.ticket_code).first()
    
    if not ticket:
        return {"valid": False, "message": "Ticket not found"}
    
    if ticket.status != TicketStatus.ACTIVE:
        return {"valid": False, "message": f"Ticket status: {ticket.status}"}
    
    return {
        "valid": True,
        "ticket": {
            "code": ticket.ticket_code,
            "guest_name": ticket.guest_name,
            "event_id": str(ticket.event_id)
        }
    }


@router.post("/{ticket_id}/use", response_model=TicketResponse)
def use_ticket(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Использовать билет (отметить как использованный)"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    if ticket.status != TicketStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket is not active"
        )
    
    from datetime import datetime
    ticket.status = TicketStatus.USED
    ticket.used_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ticket)
    
    return ticket

