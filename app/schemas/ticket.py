from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class TicketPurchase(BaseModel):
    event_id: UUID
    ticket_type_id: UUID
    quantity: int = 1
    guest_name: str
    guest_email: EmailStr
    guest_phone: str


class TicketResponse(BaseModel):
    id: UUID
    event_id: UUID
    ticket_type_id: UUID
    ticket_code: str
    qr_code_url: Optional[str]
    status: str
    guest_name: Optional[str]
    guest_email: Optional[str]
    guest_phone: Optional[str]
    created_at: datetime
    used_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TicketVerify(BaseModel):
    ticket_code: str


class TicketUse(BaseModel):
    ticket_code: str

