from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class RefundStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Refund(Base):
    __tablename__ = "refunds"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), unique=True, nullable=False)
    
    amount = Column(Integer, nullable=False)  # в копейках
    status = Column(Enum(RefundStatus), default=RefundStatus.PENDING)
    
    reason = Column(Text)
    admin_notes = Column(Text)
    
    # Внешний ID возврата (от платежной системы)
    external_id = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    payment = relationship("Payment", back_populates="refund")
    
    def __repr__(self):
        return f"<Refund {self.id} - {self.status}>"

