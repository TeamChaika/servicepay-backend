from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.venue import VenueCreate, VenueUpdate, VenueResponse
from app.models.venue import Venue
from app.models.user import User
from app.dependencies import get_current_user, get_current_active_owner

router = APIRouter()


@router.post("/", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
def create_venue(
    venue_data: VenueCreate,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Создать новое заведение"""
    venue = Venue(
        owner_id=current_user.id,
        **venue_data.model_dump()
    )
    
    db.add(venue)
    db.commit()
    db.refresh(venue)
    
    return venue


@router.get("/", response_model=List[VenueResponse])
def list_venues(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список заведений текущего пользователя"""
    venues = db.query(Venue).filter(Venue.owner_id == current_user.id).offset(skip).limit(limit).all()
    return venues


@router.get("/{venue_id}", response_model=VenueResponse)
def get_venue(
    venue_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить информацию о заведении"""
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    # Проверка доступа
    if venue.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return venue


@router.put("/{venue_id}", response_model=VenueResponse)
def update_venue(
    venue_id: UUID,
    venue_data: VenueUpdate,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Обновить информацию о заведении"""
    venue = db.query(Venue).filter(Venue.id == venue_id, Venue.owner_id == current_user.id).first()
    
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    update_data = venue_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(venue, key, value)
    
    db.commit()
    db.refresh(venue)
    
    return venue


@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venue(
    venue_id: UUID,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Удалить заведение"""
    venue = db.query(Venue).filter(Venue.id == venue_id, Venue.owner_id == current_user.id).first()
    
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    db.delete(venue)
    db.commit()
    
    return None

