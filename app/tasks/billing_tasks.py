from celery import shared_task
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.balance import TransactionType
from app.services.billing_service import BillingService
from app.config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.billing_tasks.charge_monthly_subscriptions")
def charge_monthly_subscriptions():
    """Списать ежемесячную подписку у всех владельцев"""
    db = SessionLocal()
    
    try:
        # Получаем всех владельцев
        owners = db.query(User).filter(
            User.role == UserRole.OWNER,
            User.is_active == True
        ).all()
        
        logger.info(f"Processing monthly subscription for {len(owners)} owners")
        
        for owner in owners:
            try:
                balance = BillingService.get_balance(db, owner.id)
                
                if balance.amount >= settings.MONTHLY_SUBSCRIPTION:
                    # Списываем подписку
                    BillingService.deduct_funds(
                        db=db,
                        user_id=owner.id,
                        amount=settings.MONTHLY_SUBSCRIPTION,
                        transaction_type=TransactionType.SUBSCRIPTION,
                        description=f"Monthly subscription for {datetime.utcnow().strftime('%B %Y')}"
                    )
                    
                    logger.info(f"Charged subscription for user {owner.id}")
                else:
                    # Недостаточно средств - отправляем уведомление
                    logger.warning(f"Insufficient balance for user {owner.id}")
                    from app.tasks.notification_tasks import send_low_balance_notification
                    send_low_balance_notification.delay(str(owner.id))
                    
            except Exception as e:
                logger.error(f"Error charging subscription for user {owner.id}: {e}")
                continue
        
    except Exception as e:
        logger.error(f"Error charging monthly subscriptions: {e}")
    finally:
        db.close()


@shared_task(name="app.tasks.billing_tasks.check_low_balances")
def check_low_balances():
    """Проверить балансы и отправить уведомления"""
    db = SessionLocal()
    
    try:
        owners = db.query(User).filter(
            User.role == UserRole.OWNER,
            User.is_active == True
        ).all()
        
        for owner in owners:
            try:
                if BillingService.check_low_balance(db, owner.id):
                    logger.info(f"Low balance detected for user {owner.id}")
                    
                    from app.tasks.notification_tasks import send_low_balance_notification
                    send_low_balance_notification.delay(str(owner.id))
                    
            except Exception as e:
                logger.error(f"Error checking balance for user {owner.id}: {e}")
                continue
        
    except Exception as e:
        logger.error(f"Error checking low balances: {e}")
    finally:
        db.close()


@shared_task(name="app.tasks.billing_tasks.process_commission")
def process_commission(payment_id: str):
    """Обработать комиссию с платежа"""
    db = SessionLocal()
    
    try:
        from app.models.payment import Payment
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment or not payment.venue_id:
            return
        
        # Получаем владельца заведения
        from app.models.venue import Venue
        venue = db.query(Venue).filter(Venue.id == payment.venue_id).first()
        
        if not venue:
            return
        
        # Списываем комиссию с баланса владельца
        if payment.commission > 0:
            try:
                BillingService.deduct_funds(
                    db=db,
                    user_id=venue.owner_id,
                    amount=payment.commission,
                    transaction_type=TransactionType.COMMISSION,
                    description=f"Commission for payment {payment.id}",
                    reference_id=payment.id
                )
                
                logger.info(f"Processed commission for payment {payment.id}")
                
            except Exception as e:
                logger.error(f"Error deducting commission: {e}")
        
    except Exception as e:
        logger.error(f"Error processing commission: {e}")
    finally:
        db.close()

