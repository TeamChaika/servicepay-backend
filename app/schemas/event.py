from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    event_type: str = "other"
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    deposit_required: bool = False
    deposit_amount: Optional[int] = None
    tickets_enabled: bool = False
    max_tickets: Optional[int] = None
    cover_image_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    age_restriction: Optional[int] = None
    dress_code: Optional[str] = None


class EventCreate(EventBase):
    venue_id: UUID


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    event_type: Optional[str] = None
    status: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    deposit_required: Optional[bool] = None
    deposit_amount: Optional[int] = None
    tickets_enabled: Optional[bool] = None
    max_tickets: Optional[int] = None
    cover_image_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    age_restriction: Optional[int] = None
    dress_code: Optional[str] = None


class EventResponse(EventBase):
    id: UUID
    venue_id: UUID
    status: str
    tickets_sold: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TicketTypeCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    price: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class TicketTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price: Optional[int] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None


class TicketTypeResponse(BaseModel):
    id: UUID
    event_id: UUID
    name: str
    description: Optional[str]
    price: int
    quantity: int
    sold: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

