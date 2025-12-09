from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class Location(Base):
    """
    Таблица для хранения геолокаций и поиска ближайших заведений
    """
    __tablename__ = "locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Координаты
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    
    # Адрес
    address = Column(String)
    city = Column(String, index=True)
    country = Column(String)
    postal_code = Column(String)
    
    # Для поиска по радиусу
    geohash = Column(String, index=True)
    
    def __repr__(self):
        return f"<Location {self.city} - {self.latitude}, {self.longitude}>"

