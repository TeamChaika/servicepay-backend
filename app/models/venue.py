from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Venue(Base):
    __tablename__ = "venues"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    name = Column(String, nullable=False)
    description = Column(Text)
    address = Column(String, nullable=False)
    
    # Контакты
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    
    # Геолокация
    latitude = Column(String)
    longitude = Column(String)
    
    # Настройки
    capacity = Column(Integer)
    logo_url = Column(String)
    cover_image_url = Column(String)
    working_hours = Column(JSONB)  # {"monday": {"open": "10:00", "close": "22:00"}}
    
    # Статус
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="venues")
    events = relationship("Event", back_populates="venue", cascade="all, delete-orphan")
    staff = relationship("Staff", back_populates="venue", cascade="all, delete-orphan")
    terminals = relationship("Terminal", back_populates="venue", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Venue {self.name}>"

