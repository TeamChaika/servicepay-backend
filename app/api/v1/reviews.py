from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.models.review import Review
from app.models.event import Event
from app.models.user import User
from app.dependencies import get_current_user
from pydantic import BaseModel, Field

router = APIRouter()


class ReviewCreate(BaseModel):
    event_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: str


class ReviewResponse(BaseModel):
    id: UUID
    event_id: UUID
    user_id: UUID
    rating: int
    comment: str
    is_published: bool
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать отзыв о мероприятии"""
    # Проверяем мероприятие
    event = db.query(Event).filter(Event.id == review_data.event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Проверяем, не оставлял ли уже отзыв
    existing_review = db.query(Review).filter(
        Review.event_id == review_data.event_id,
        Review.user_id == current_user.id
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this event"
        )
    
    # Создаем отзыв
    review = Review(
        event_id=review_data.event_id,
        user_id=current_user.id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    return review


@router.get("/event/{event_id}", response_model=List[ReviewResponse])
def list_event_reviews(
    event_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить отзывы о мероприятии"""
    reviews = db.query(Review).filter(
        Review.event_id == event_id,
        Review.is_published == True
    ).offset(skip).limit(limit).all()
    
    return reviews

