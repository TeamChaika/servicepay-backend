from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.database import get_db
from app.models.terminal import Terminal
from app.models.venue import Venue
from app.models.user import User
from app.dependencies import get_current_active_owner
from app.core.encryption import encryption_service
from pydantic import BaseModel

router = APIRouter()


class TerminalCreate(BaseModel):
    venue_id: UUID
    name: str
    terminal_id: str
    api_key: str
    description: str = ""
    location: str = ""
    is_active: bool = True


class TerminalUpdate(BaseModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class TerminalResponse(BaseModel):
    id: UUID
    venue_id: UUID
    name: str
    terminal_id: str
    description: str
    location: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=TerminalResponse, status_code=status.HTTP_201_CREATED)
def create_terminal(
    terminal_data: TerminalCreate,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Создать СБП терминал для заведения"""
    # Проверяем, что заведение принадлежит пользователю
    venue = db.query(Venue).filter(
        Venue.id == terminal_data.venue_id,
        Venue.owner_id == current_user.id
    ).first()
    
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    # Проверяем уникальность terminal_id
    existing = db.query(Terminal).filter(
        Terminal.terminal_id == terminal_data.terminal_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terminal ID already exists"
        )
    
    # Шифруем API ключ
    encrypted_api_key = encryption_service.encrypt(terminal_data.api_key)
    
    # Создаем терминал
    terminal = Terminal(
        venue_id=terminal_data.venue_id,
        name=terminal_data.name,
        terminal_id=terminal_data.terminal_id,
        api_key_encrypted=encrypted_api_key,
        description=terminal_data.description,
        location=terminal_data.location,
        is_active=terminal_data.is_active
    )
    
    db.add(terminal)
    db.commit()
    db.refresh(terminal)
    
    return terminal


@router.get("/venue/{venue_id}", response_model=List[TerminalResponse])
def list_venue_terminals(
    venue_id: UUID,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Получить список терминалов заведения"""
    venue = db.query(Venue).filter(
        Venue.id == venue_id,
        Venue.owner_id == current_user.id
    ).first()
    
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    terminals = db.query(Terminal).filter(Terminal.venue_id == venue_id).all()
    return terminals


@router.get("/", response_model=List[TerminalResponse])
def list_all_terminals(
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Получить все терминалы пользователя"""
    # Получаем ID всех заведений пользователя
    venue_ids = [v.id for v in db.query(Venue).filter(Venue.owner_id == current_user.id).all()]
    
    terminals = db.query(Terminal).filter(Terminal.venue_id.in_(venue_ids)).all()
    return terminals


@router.put("/{terminal_id}", response_model=TerminalResponse)
def update_terminal(
    terminal_id: UUID,
    terminal_data: TerminalUpdate,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Обновить терминал"""
    terminal = db.query(Terminal).join(Venue).filter(
        Terminal.id == terminal_id,
        Venue.owner_id == current_user.id
    ).first()
    
    if not terminal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terminal not found"
        )
    
    # Обновляем поля
    update_data = terminal_data.model_dump(exclude_unset=True)
    
    # Если обновляется API ключ - шифруем его
    if 'api_key' in update_data and update_data['api_key']:
        update_data['api_key_encrypted'] = encryption_service.encrypt(update_data['api_key'])
        del update_data['api_key']
    
    for key, value in update_data.items():
        setattr(terminal, key, value)
    
    db.commit()
    db.refresh(terminal)
    
    return terminal


@router.delete("/{terminal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_terminal(
    terminal_id: UUID,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Удалить терминал"""
    terminal = db.query(Terminal).join(Venue).filter(
        Terminal.id == terminal_id,
        Venue.owner_id == current_user.id
    ).first()
    
    if not terminal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terminal not found"
        )
    
    db.delete(terminal)
    db.commit()
    
    return None

