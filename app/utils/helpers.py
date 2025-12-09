import re
from typing import Optional
from datetime import datetime, timedelta


def format_phone(phone: str) -> str:
    """Форматировать номер телефона"""
    # Убираем все нецифровые символы
    digits = re.sub(r'\D', '', phone)
    
    # Добавляем +7 если нужно
    if len(digits) == 10:
        digits = '7' + digits
    elif len(digits) == 11 and digits[0] == '8':
        digits = '7' + digits[1:]
    
    return '+' + digits


def validate_email(email: str) -> bool:
    """Проверить валидность email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def format_currency(amount: int, currency: str = "RUB") -> str:
    """Форматировать сумму в копейках в строку"""
    rubles = amount / 100
    return f"{rubles:.2f} {currency}"


def generate_order_id(prefix: str = "ORD") -> str:
    """Генерировать уникальный ID заказа"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    import uuid
    short_uuid = str(uuid.uuid4())[:8]
    return f"{prefix}-{timestamp}-{short_uuid}"


def calculate_commission(amount: int, rate: float = 0.008) -> int:
    """Рассчитать комиссию"""
    return int(amount * rate)


def get_expiration_datetime(minutes: int = 15) -> datetime:
    """Получить время истечения"""
    return datetime.utcnow() + timedelta(minutes=minutes)

