from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.database import get_db
from app.schemas.event import (
    EventCreate, EventUpdate, EventResponse,
    TicketTypeCreate, TicketTypeUpdate, TicketTypeResponse
)
from app.models.event import Event
from app.models.ticket import TicketType
from app.models.venue import Venue
from app.models.user import User
from app.dependencies import get_current_user, get_current_active_owner

router = APIRouter()


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Создать новое мероприятие"""
    # Проверяем, что заведение принадлежит пользователю
    venue = db.query(Venue).filter(
        Venue.id == event_data.venue_id,
        Venue.owner_id == current_user.id
    ).first()
    
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found or access denied"
        )
    
    # Проверяем наличие активного СБП терминала для заведения
    from app.models.terminal import Terminal
    active_terminal = db.query(Terminal).filter(
        Terminal.venue_id == event_data.venue_id,
        Terminal.is_active == True
    ).first()
    
    if not active_terminal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно создать мероприятие: у заведения нет активного СБП терминала. Добавьте терминал в разделе 'СБП Терминалы'."
        )
    
    event = Event(**event_data.model_dump())
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event


@router.get("/", response_model=List[EventResponse])
def list_events(
    venue_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список мероприятий"""
    query = db.query(Event)
    
    if venue_id:
        query = query.filter(Event.venue_id == venue_id)
    
    if status:
        query = query.filter(Event.status == status)
    
    events = query.offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: UUID, db: Session = Depends(get_db)):
    """Получить информацию о мероприятии"""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: UUID,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Обновить мероприятие"""
    event = db.query(Event).join(Venue).filter(
        Event.id == event_id,
        Venue.owner_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    update_data = event_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)
    
    db.commit()
    db.refresh(event)
    
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: UUID,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Удалить мероприятие"""
    event = db.query(Event).join(Venue).filter(
        Event.id == event_id,
        Venue.owner_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete(event)
    db.commit()
    
    return None


# Ticket Types endpoints

@router.post("/{event_id}/ticket-types", response_model=TicketTypeResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_type(
    event_id: UUID,
    ticket_type_data: TicketTypeCreate,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Создать тип билета для мероприятия"""
    event = db.query(Event).join(Venue).filter(
        Event.id == event_id,
        Venue.owner_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    ticket_type = TicketType(
        event_id=event_id,
        **ticket_type_data.model_dump()
    )
    
    db.add(ticket_type)
    db.commit()
    db.refresh(ticket_type)
    
    return ticket_type


@router.get("/{event_id}/ticket-types", response_model=List[TicketTypeResponse])
def list_ticket_types(event_id: UUID, db: Session = Depends(get_db)):
    """Получить список типов билетов для мероприятия"""
    ticket_types = db.query(TicketType).filter(TicketType.event_id == event_id).all()
    return ticket_types

