from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class BalanceResponse(BaseModel):
    id: UUID
    user_id: UUID
    amount: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BalanceTopUp(BaseModel):
    amount: int = Field(..., gt=0)
    payment_method: str = "sbp"


class BalanceTransactionResponse(BaseModel):
    id: UUID
    balance_id: UUID
    transaction_type: str
    amount: int
    balance_before: int
    balance_after: int
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

