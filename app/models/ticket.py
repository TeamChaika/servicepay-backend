from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class TicketStatus(str, enum.Enum):
    ACTIVE = "active"
    USED = "used"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class TicketType(Base):
    __tablename__ = "ticket_types"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    
    name = Column(String, nullable=False)  # VIP, Standart, Early Bird
    description = Column(String)
    price = Column(Integer, nullable=False)  # в копейках
    
    quantity = Column(Integer, nullable=False)
    sold = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="ticket_types")
    tickets = relationship("Ticket", back_populates="ticket_type")
    
    def __repr__(self):
        return f"<TicketType {self.name}>"


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    ticket_type_id = Column(UUID(as_uuid=True), ForeignKey("ticket_types.id"), nullable=False)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"))
    guest_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Уникальный код билета
    ticket_code = Column(String, unique=True, index=True, nullable=False)
    qr_code_url = Column(String)
    
    status = Column(Enum(TicketStatus), default=TicketStatus.ACTIVE)
    
    # Информация о госте
    guest_name = Column(String)
    guest_email = Column(String)
    guest_phone = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime)
    
    # Relationships
    event = relationship("Event", back_populates="tickets")
    ticket_type = relationship("TicketType", back_populates="tickets")
    payment = relationship("Payment", back_populates="tickets")
    guest = relationship("User", back_populates="tickets")
    
    def __repr__(self):
        return f"<Ticket {self.ticket_code}>"

