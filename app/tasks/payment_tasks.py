from celery import shared_task
from app.database import SessionLocal
from app.models.payment import Payment, PaymentStatus
from app.services.qr_manager_client import qr_manager_client
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.payment_tasks.check_payment_status")
def check_payment_status(payment_id: str):
    """Проверить статус платежа"""
    db = SessionLocal()
    
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            logger.warning(f"Payment {payment_id} not found")
            return
        
        if payment.status != PaymentStatus.PENDING:
            logger.info(f"Payment {payment_id} already processed: {payment.status}")
            return
        
        # Проверяем статус в QR Manager (async метод, нужно адаптировать)
        # status_data = await qr_manager_client.check_payment_status(payment.qr_id)
        
        # TODO: Обновить статус платежа на основе ответа
        
        logger.info(f"Payment {payment_id} status checked")
        
    except Exception as e:
        logger.error(f"Error checking payment status: {e}")
    finally:
        db.close()


@shared_task(name="app.tasks.payment_tasks.check_pending_payments")
def check_pending_payments():
    """Проверить все pending платежи"""
    db = SessionLocal()
    
    try:
        pending_payments = db.query(Payment).filter(
            Payment.status == PaymentStatus.PENDING
        ).all()
        
        logger.info(f"Found {len(pending_payments)} pending payments")
        
        for payment in pending_payments:
            # Проверяем истекшие платежи
            if payment.expired_at and payment.expired_at < datetime.utcnow():
                payment.status = PaymentStatus.CANCELLED
                db.commit()
                logger.info(f"Payment {payment.id} expired")
                continue
            
            # Запускаем проверку статуса
            check_payment_status.delay(str(payment.id))
        
    except Exception as e:
        logger.error(f"Error checking pending payments: {e}")
    finally:
        db.close()


@shared_task(name="app.tasks.payment_tasks.process_payment_success")
def process_payment_success(payment_id: str):
    """Обработать успешный платеж"""
    db = SessionLocal()
    
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            logger.warning(f"Payment {payment_id} not found")
            return
        
        # Если это пополнение баланса - начисляем средства
        if payment.payment_type == "balance_topup":
            from app.services.billing_service import BillingService
            from app.models.balance import TransactionType
            
            BillingService.add_funds(
                db=db,
                user_id=payment.user_id,
                amount=payment.amount,
                transaction_type=TransactionType.TOPUP,
                description=f"Balance top-up via payment {payment.id}",
                reference_id=payment.id
            )
            
            logger.info(f"Balance topped up for user {payment.user_id}")
        
        # TODO: Отправить уведомление
        from app.tasks.notification_tasks import send_payment_success_notification
        send_payment_success_notification.delay(payment_id)
        
    except Exception as e:
        logger.error(f"Error processing payment success: {e}")
    finally:
        db.close()

