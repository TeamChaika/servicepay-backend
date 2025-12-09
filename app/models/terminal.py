from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Terminal(Base):
    __tablename__ = "terminals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False)
    
    name = Column(String, nullable=False)
    terminal_id = Column(String, unique=True, nullable=False)  # ID терминала от QR Manager
    
    # Настройки
    is_active = Column(Boolean, default=True)
    api_key_encrypted = Column(Text)  # Зашифрованный API ключ
    
    # Дополнительная информация
    description = Column(String)
    location = Column(String)  # Где находится терминал в заведении
    
    # Метаданные
    extra_data = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime)
    
    # Relationships
    venue = relationship("Venue", back_populates="terminals")
    
    def __repr__(self):
        return f"<Terminal {self.name}>"

