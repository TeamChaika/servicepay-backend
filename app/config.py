from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # App
    APP_NAME: str = "HelpChaika"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    ENCRYPTION_KEY: str
    
    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str
    
    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000", "http://localhost:3001"]'
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # URLs
    API_BASE_URL: str
    ADMIN_PORTAL_URL: str
    GUEST_PORTAL_URL: str
    
    # SMS
    SMSAERO_EMAIL: str = ""
    SMSAERO_API_KEY: str = ""
    
    # Email
    EMAIL_PROVIDER: str = "sendgrid"
    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str
    EMAIL_FROM_NAME: str
    
    # SMTP
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # Биллинг
    DEFAULT_COMMISSION_RATE: float = 0.008
    MONTHLY_SUBSCRIPTION: int = 50000
    LOW_BALANCE_THRESHOLD: int = 10000
    
    # QR Manager (СБП) - единственный способ генерации QR кодов
    QR_MANAGER_API_URL: str = "https://app.wapiserv.qrm.ooo/operations/qr-code/"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

