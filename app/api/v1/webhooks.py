from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.payment_service import PaymentService
from app.models.payment import PaymentStatus
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/payment/callback")
async def payment_callback(request: Request, db: Session = Depends(get_db)):
    """
    Webhook для получения уведомлений о статусе платежа от QR Manager
    """
    try:
        payload = await request.json()
        logger.info(f"Received payment callback: {payload}")
        
        # TODO: Добавить проверку подписи webhook
        
        payment_id = payload.get("order_id")
        status = payload.get("status")
        external_id = payload.get("transaction_id")
        
        if not payment_id or not status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload"
            )
        
        # Маппинг статусов
        status_mapping = {
            "success": PaymentStatus.COMPLETED,
            "failed": PaymentStatus.FAILED,
            "cancelled": PaymentStatus.CANCELLED,
            "processing": PaymentStatus.PROCESSING
        }
        
        payment_status = status_mapping.get(status, PaymentStatus.PENDING)
        
        # Обновляем статус платежа
        payment = PaymentService.update_payment_status(
            db=db,
            payment_id=payment_id,
            status=payment_status,
            external_id=external_id
        )
        
        # TODO: Отправить уведомление пользователю
        # TODO: Если это пополнение баланса - начислить средства
        
        return {"status": "ok", "payment_id": payment_id}
        
    except Exception as e:
        logger.error(f"Error processing payment callback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/test")
def test_webhook():
    """Тестовый endpoint для проверки webhooks"""
    return {"message": "Webhooks are working"}

