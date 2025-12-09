from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class PaymentType(str, enum.Enum):
    DEPOSIT = "deposit"
    TICKET = "ticket"
    BALANCE_TOPUP = "balance_topup"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    SBP = "sbp"
    CARD = "card"
    CASH = "cash"


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id"))
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"))
    
    payment_type = Column(Enum(PaymentType), nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.SBP)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Суммы (в копейках)
    amount = Column(Integer, nullable=False)
    commission = Column(Integer, default=0)
    total_amount = Column(Integer, nullable=False)
    
    # Данные плательщика
    payer_phone = Column(String)
    payer_email = Column(String)
    payer_name = Column(String)
    
    # Внешние идентификаторы (от платежной системы)
    external_id = Column(String, unique=True, index=True)
    qr_id = Column(String)
    qr_url = Column(Text)
    
    # Дополнительная информация
    description = Column(Text)
    extra_data = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = Column(DateTime)
    expired_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    venue = relationship("Venue")
    event = relationship("Event", back_populates="payments")
    tickets = relationship("Ticket", back_populates="payment")
    refund = relationship("Refund", back_populates="payment", uselist=False)
    
    def __repr__(self):
        return f"<Payment {self.id} - {self.status}>"

