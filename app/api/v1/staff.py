from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.models.staff import Staff, StaffRole
from app.models.venue import Venue
from app.models.user import User
from app.dependencies import get_current_active_owner
from pydantic import BaseModel, EmailStr

router = APIRouter()


class StaffInvite(BaseModel):
    venue_id: UUID
    email: EmailStr
    role: StaffRole


class StaffResponse(BaseModel):
    id: UUID
    venue_id: UUID
    user_id: UUID
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("/invite", status_code=status.HTTP_201_CREATED)
def invite_staff(
    invite_data: StaffInvite,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Пригласить сотрудника в заведение"""
    # Проверяем, что заведение принадлежит пользователю
    venue = db.query(Venue).filter(
        Venue.id == invite_data.venue_id,
        Venue.owner_id == current_user.id
    ).first()
    
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    # Ищем пользователя по email
    staff_user = db.query(User).filter(User.email == invite_data.email).first()
    
    if not staff_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. User must register first."
        )
    
    # Проверяем, не добавлен ли уже
    existing_staff = db.query(Staff).filter(
        Staff.venue_id == invite_data.venue_id,
        Staff.user_id == staff_user.id
    ).first()
    
    if existing_staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a staff member"
        )
    
    # Создаем запись сотрудника
    staff = Staff(
        venue_id=invite_data.venue_id,
        user_id=staff_user.id,
        role=invite_data.role
    )
    
    db.add(staff)
    db.commit()
    
    return {"message": "Staff member added successfully"}


@router.get("/venue/{venue_id}", response_model=List[StaffResponse])
def list_venue_staff(
    venue_id: UUID,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Получить список сотрудников заведения"""
    venue = db.query(Venue).filter(
        Venue.id == venue_id,
        Venue.owner_id == current_user.id
    ).first()
    
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    staff_members = db.query(Staff).filter(Staff.venue_id == venue_id).all()
    return staff_members


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_staff(
    staff_id: UUID,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Удалить сотрудника"""
    staff = db.query(Staff).join(Venue).filter(
        Staff.id == staff_id,
        Venue.owner_id == current_user.id
    ).first()
    
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    db.delete(staff)
    db.commit()
    
    return None

