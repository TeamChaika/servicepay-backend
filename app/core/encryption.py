from cryptography.fernet import Fernet
from app.config import settings


class EncryptionService:
    def __init__(self):
        # В production используйте безопасный ключ из настроек
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
    
    def encrypt(self, data: str) -> str:
        """Шифрует данные"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Расшифровывает данные"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


encryption_service = EncryptionService()

