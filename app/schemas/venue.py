from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime


class VenueBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    capacity: Optional[int] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    working_hours: Optional[Dict] = None


class VenueCreate(VenueBase):
    pass


class VenueUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    capacity: Optional[int] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    working_hours: Optional[Dict] = None
    is_active: Optional[bool] = None


class VenueResponse(VenueBase):
    id: UUID
    owner_id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

