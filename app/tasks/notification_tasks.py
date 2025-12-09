from celery import shared_task
from app.database import SessionLocal
from app.models.payment import Payment
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.notification_tasks.send_payment_success_notification")
def send_payment_success_notification(payment_id: str):
    """Отправить уведомление об успешной оплате"""
    db = SessionLocal()
    
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            logger.warning(f"Payment {payment_id} not found")
            return
        
        # Отправляем email
        if payment.payer_email:
            # TODO: Реализовать отправку email
            logger.info(f"Sending payment success email to {payment.payer_email}")
        
        # Отправляем SMS
        if payment.payer_phone:
            # TODO: Реализовать отправку SMS
            logger.info(f"Sending payment success SMS to {payment.payer_phone}")
        
    except Exception as e:
        logger.error(f"Error sending payment notification: {e}")
    finally:
        db.close()


@shared_task(name="app.tasks.notification_tasks.send_low_balance_notification")
def send_low_balance_notification(user_id: str):
    """Отправить уведомление о низком балансе"""
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"User {user_id} not found")
            return
        
        from app.services.billing_service import BillingService
        balance = BillingService.get_balance(db, user.id)
        
        # TODO: Отправить email
        logger.info(f"Sending low balance notification to {user.email}")
        logger.info(f"Current balance: {balance.amount / 100:.2f} RUB")
        
    except Exception as e:
        logger.error(f"Error sending low balance notification: {e}")
    finally:
        db.close()


@shared_task(name="app.tasks.notification_tasks.send_ticket_notification")
def send_ticket_notification(ticket_id: str):
    """Отправить билет пользователю"""
    db = SessionLocal()
    
    try:
        from app.models.ticket import Ticket
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            logger.warning(f"Ticket {ticket_id} not found")
            return
        
        # Отправляем билет на email
        if ticket.guest_email:
            # TODO: Реализовать отправку билета с QR кодом
            logger.info(f"Sending ticket to {ticket.guest_email}")
        
    except Exception as e:
        logger.error(f"Error sending ticket notification: {e}")
    finally:
        db.close()

