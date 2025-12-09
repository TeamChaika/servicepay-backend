from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional
from uuid import uuid4
from app.models.payment import Payment, PaymentStatus, PaymentType
from app.models.event import Event
from app.models.terminal import Terminal
from app.schemas.payment import PaymentCreate
from fastapi import HTTPException, status
import logging
import asyncio

logger = logging.getLogger(__name__)


class PaymentService:
    @staticmethod
    def create_payment(
        db: Session,
        payment_data: PaymentCreate,
        user_id: Optional[str] = None,
        venue_id: Optional[str] = None
    ) -> Payment:
        # Вычисляем комиссию (0.8% по умолчанию)
        from app.config import settings
        commission = int(payment_data.amount * settings.DEFAULT_COMMISSION_RATE)
        total_amount = payment_data.amount + commission
        
        # Создаем платеж
        payment = Payment(
            user_id=user_id,
            venue_id=venue_id,
            event_id=payment_data.event_id,
            payment_type=payment_data.payment_type,
            amount=payment_data.amount,
            commission=commission,
            total_amount=total_amount,
            payer_phone=payment_data.payer_phone,
            payer_email=payment_data.payer_email,
            payer_name=payment_data.payer_name,
            description=payment_data.description,
            extra_data=payment_data.extra_data,
            expired_at=datetime.utcnow() + timedelta(minutes=15)
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # Генерируем QR код ТОЛЬКО через QR Manager API (fallback удалён!)
        try:
            # Находим активный терминал для заведения (обязательно!)
            terminal = None
            if venue_id:
                terminal = db.query(Terminal).filter(
                    Terminal.venue_id == venue_id,
                    Terminal.is_active == True
                ).first()
            
            if not terminal:
                logger.error(f"❌ No active terminal found for venue {venue_id}")
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="У заведения нет активного СБП терминала. Оплата невозможна."
                )
            
            # Используем ТОЛЬКО QR Manager API (без fallback!)
            logger.info(f"🔄 Using QR Manager API for payment {payment.id}")
            logger.info(f"Terminal: {terminal.name} (ID: {terminal.terminal_id})")
            
            # Вызываем QR Manager
            qr_response = PaymentService._create_qr_via_manager_sync(payment, terminal, db)
            
            if not qr_response.get("qr_url"):
                logger.error(f"❌ QR Manager returned empty qr_url")
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="QR Manager не вернул QR код. Проверьте настройки терминала."
                )
            
            payment.qr_id = qr_response["qr_id"]
            payment.qr_url = qr_response["qr_url"]
            db.commit()
            db.refresh(payment)
            
            logger.info(f"✅ QR code generated successfully via QR Manager")
            logger.info(f"QR ID: {payment.qr_id}")
            
        except HTTPException:
            # Пробрасываем HTTPException как есть
            raise
        except Exception as e:
            logger.error(f"❌ Failed to generate QR code via QR Manager: {e}")
            # Откатываем транзакцию - депозит НЕ будет создан
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Ошибка при создании QR кода для оплаты через QR Manager. Проверьте API ключ терминала."
            )
        
        logger.info(f"Payment created: {payment.id}")
        return payment
    
    @staticmethod
    def _create_qr_via_manager_sync(payment: Payment, terminal: Terminal, db: Session) -> dict:
        """Создание QR кода через QR Manager API (синхронная версия)"""
        from app.core.encryption import encryption_service
        import httpx
        from app.config import settings
        
        # Расшифровываем API ключ терминала
        api_key = encryption_service.decrypt(terminal.api_key_encrypted)
        
        # Формируем URLs для callback и redirect
        notification_url = f"{settings.API_BASE_URL}/api/webhooks/payment/callback"
        redirect_url = f"{settings.GUEST_PORTAL_URL}/deposit/{payment.id}"
        
        # Формируем назначение платежа
        payment_purpose = payment.description or f"Депозит #{payment.id}"
        if payment.payer_name:
            payment_purpose = f"{payment_purpose} ({payment.payer_name})"
        
        # Payload для QR Manager API
        payload = {
            "sum": payment.total_amount,  # В копейках!
            "qr_size": 600,
            "payment_purpose": payment_purpose,
            "notification_url": notification_url,
            "redirect_url": redirect_url,
        }
        
        headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        }
        
        logger.info(f"📤 Calling QR Manager API")
        logger.info(f"URL: {settings.QR_MANAGER_API_URL}")
        logger.info(f"Sum: {payment.total_amount} kop ({payment.total_amount/100:.2f} RUB)")
        logger.info(f"Purpose: {payment_purpose[:60]}...")
        logger.info(f"Notification URL: {notification_url}")
        logger.info(f"Redirect URL: {redirect_url}")
        
        try:
            # Синхронный HTTP запрос к QR Manager
            response = httpx.post(
                settings.QR_MANAGER_API_URL,
                json=payload,
                headers=headers,
                timeout=20.0
            )
            
            if response.status_code >= 400:
                logger.error(f"❌ QR API {response.status_code}: {response.text}")
                raise RuntimeError(f"QR API {response.status_code}: {response.text}")
            
            data = response.json() or {}
            results = data.get("results", data)
            
            logger.info(f"✅ QR Manager response received")
            logger.info(f"Response keys: {list(results.keys())}")
            
            # Извлекаем URL QR кода из ответа
            qr_url = (
                results.get("qr_url") or 
                results.get("url") or 
                results.get("qr_image_url") or 
                results.get("image") or
                results.get("qr_code")
            )
            qr_id = results.get("qr_id") or results.get("id") or results.get("payment_id")
            
            if qr_url:
                logger.info(f"✅ QR URL found: {qr_url[:80]}...")
            else:
                logger.warning(f"⚠️ No QR URL in response: {results}")
            
            return {
                "qr_id": str(qr_id) if qr_id else f"QR-{payment.id}",
                "qr_url": qr_url or "",
                "raw_response": results
            }
            
        except httpx.ConnectError as e:
            logger.error(f"❌ Cannot connect to QR Manager API: {e}")
            raise RuntimeError(f"Cannot connect to QR Manager API")
        except Exception as e:
            logger.error(f"❌ QR Manager error: {type(e).__name__}: {e}")
            raise
    
    @staticmethod
    def update_payment_status(
        db: Session,
        payment_id: str,
        status: PaymentStatus,
        external_id: Optional[str] = None
    ) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        payment.status = status
        if external_id:
            payment.external_id = external_id
        
        if status == PaymentStatus.COMPLETED:
            payment.paid_at = datetime.utcnow()
        
        db.commit()
        db.refresh(payment)
        
        logger.info(f"Payment {payment_id} status updated to {status}")
        return payment
    
    @staticmethod
    def get_payment(db: Session, payment_id: str) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        return payment

