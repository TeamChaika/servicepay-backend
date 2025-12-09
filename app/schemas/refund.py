from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class RefundCreate(BaseModel):
    payment_id: UUID
    amount: int = Field(..., gt=0)
    reason: str


class RefundUpdate(BaseModel):
    status: str
    admin_notes: Optional[str] = None


class RefundResponse(BaseModel):
    id: UUID
    payment_id: UUID
    amount: int
    status: str
    reason: Optional[str]
    admin_notes: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

