from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class StaffRole(str, enum.Enum):
    MANAGER = "manager"
    CASHIER = "cashier"
    WAITER = "waiter"
    SECURITY = "security"
    ADMIN = "admin"


class Staff(Base):
    __tablename__ = "staff"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    role = Column(Enum(StaffRole), nullable=False)
    
    # Права доступа
    permissions = Column(JSONB)  # {"can_refund": true, "can_check_tickets": true}
    
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    venue = relationship("Venue", back_populates="staff")
    user = relationship("User", back_populates="staff_profiles")
    
    def __repr__(self):
        return f"<Staff {self.user_id} at {self.venue_id}>"

