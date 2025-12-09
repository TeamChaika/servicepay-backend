from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class EventType(str, enum.Enum):
    CONCERT = "concert"
    PARTY = "party"
    WORKSHOP = "workshop"
    CONFERENCE = "conference"
    DINING = "dining"
    OTHER = "other"


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Event(Base):
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text)
    event_type = Column(Enum(EventType), default=EventType.OTHER)
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT)
    
    # Время проведения
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)
    
    # Депозит
    deposit_required = Column(Boolean, default=False)
    deposit_amount = Column(Integer)  # в копейках
    
    # Билеты
    tickets_enabled = Column(Boolean, default=False)
    max_tickets = Column(Integer)
    tickets_sold = Column(Integer, default=0)
    
    # Медиа
    cover_image_url = Column(String)
    gallery_images = Column(JSONB)  # ["url1", "url2", ...]
    
    # Дополнительные поля
    tags = Column(JSONB)  # ["music", "live", "dj"]
    age_restriction = Column(Integer)  # 18+
    dress_code = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    venue = relationship("Venue", back_populates="events")
    ticket_types = relationship("TicketType", back_populates="event", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="event", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="event")
    reviews = relationship("Review", back_populates="event")
    
    def __repr__(self):
        return f"<Event {self.title}>"

