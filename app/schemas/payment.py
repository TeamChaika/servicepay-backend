from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime


class PaymentCreate(BaseModel):
    payment_type: str  # deposit, ticket, balance_topup
    amount: int = Field(..., gt=0)
    event_id: Optional[UUID] = None
    payer_phone: Optional[str] = None
    payer_email: Optional[EmailStr] = None
    payer_name: Optional[str] = None
    description: Optional[str] = None
    extra_data: Optional[Dict] = None


class DepositCreate(BaseModel):
    venue_id: UUID
    event_id: Optional[UUID] = None
    amount: int = Field(..., gt=0)
    payer_phone: str
    payer_email: Optional[EmailStr] = None
    payer_name: Optional[str] = None
    description: Optional[str] = None
    reservation_date: Optional[str] = None  # YYYY-MM-DD
    reservation_time: Optional[str] = None  # HH:MM
    guests_count: Optional[int] = None


class PaymentResponse(BaseModel):
    id: UUID
    payment_type: str
    payment_method: str
    status: str
    amount: int
    commission: int
    total_amount: int
    payer_phone: Optional[str]
    payer_email: Optional[str]
    payer_name: Optional[str]
    qr_url: Optional[str]
    qr_id: Optional[str]
    description: Optional[str]
    created_at: datetime
    expired_at: Optional[datetime]
    paid_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PaymentStatusUpdate(BaseModel):
    status: str
    external_id: Optional[str] = None
    paid_at: Optional[datetime] = None

