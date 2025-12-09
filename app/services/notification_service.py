from typing import Optional
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    async def send_notification(
        recipient: str,
        subject: str,
        message: str,
        channel: str = "email"
    ) -> bool:
        """
        Отправляет уведомление через указанный канал
        """
        try:
            if channel == "email":
                return await NotificationService.send_email(recipient, subject, message)
            elif channel == "sms":
                return await NotificationService.send_sms(recipient, message)
            else:
                logger.warning(f"Unknown notification channel: {channel}")
                return False
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    @staticmethod
    async def send_email(to: str, subject: str, body: str) -> bool:
        """
        Отправляет email уведомление
        """
        # TODO: Реализовать отправку через EmailService
        logger.info(f"Sending email to {to}: {subject}")
        return True
    
    @staticmethod
    async def send_sms(phone: str, message: str) -> bool:
        """
        Отправляет SMS уведомление
        """
        # TODO: Реализовать отправку через SMSService
        logger.info(f"Sending SMS to {phone}: {message}")
        return True
    
    @staticmethod
    async def notify_payment_success(payment_id: str, recipient: str) -> bool:
        """Уведомление об успешной оплате"""
        message = f"Ваш платеж {payment_id} успешно обработан"
        return await NotificationService.send_notification(
            recipient, 
            "Платеж успешен",
            message,
            "email"
        )
    
    @staticmethod
    async def notify_low_balance(user_email: str, balance: int) -> bool:
        """Уведомление о низком балансе"""
        message = f"Ваш баланс составляет {balance/100:.2f} руб. Пополните баланс для продолжения работы."
        return await NotificationService.send_notification(
            user_email,
            "Низкий баланс",
            message,
            "email"
        )

