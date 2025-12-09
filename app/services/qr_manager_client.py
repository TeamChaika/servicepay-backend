import httpx
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class QRManagerClient:
    """
    Клиент для работы с QR Manager API (СБП)
    API URL: https://app.wapiserv.qrm.ooo/operations/qr-code/
    """
    
    def __init__(self, api_url: str = "https://app.wapiserv.qrm.ooo/operations/qr-code/"):
        self.api_url = api_url
        self.timeout = 20
    
    async def create_qr(
        self,
        api_key: str,
        sum_kop: int,
        payment_purpose: str,
        notification_url: str,
        redirect_url: str,
        qr_size: int = 600
    ) -> Dict[str, Any]:
        """
        Создает QR код для оплаты через СБП
        
        Args:
            api_key: API ключ терминала
            sum_kop: Сумма в копейках
            payment_purpose: Назначение платежа
            notification_url: URL для webhook уведомлений
            redirect_url: URL для редиректа после оплаты
            qr_size: Размер QR кода в пикселях (default: 600)
            
        Returns:
            Dict с результатами создания QR кода
        """
        if not api_key:
            raise RuntimeError("QR API key is not configured for this enterprise")
        
        payload = {
            "sum": sum_kop,
            "qr_size": qr_size,
            "payment_purpose": payment_purpose,
            "notification_url": notification_url,
            "redirect_url": redirect_url,
        }
        
        headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        }
        
        logger.info(f"📤 Creating QR via QR Manager")
        logger.info(f"URL: {self.api_url}")
        logger.info(f"Sum: {sum_kop} kop ({sum_kop/100:.2f} RUB)")
        logger.info(f"Purpose: {payment_purpose[:60]}...")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(self.api_url, headers=headers, json=payload)
                
                if resp.status_code >= 400:
                    logger.error(f"❌ QR API {resp.status_code}: {resp.text}")
                    raise RuntimeError(f"QR API {resp.status_code}: {resp.text}")
                
                data = resp.json() or {}
                results = data.get("results", data)
                
                logger.info(f"✅ QR code created successfully")
                logger.info(f"Response: {list(results.keys())}")
                
                return results
                
        except httpx.ConnectError as e:
            logger.error(f"❌ Cannot connect to QR Manager API: {e}")
            raise RuntimeError(f"Cannot connect to QR Manager: {e}")
        except Exception as e:
            logger.error(f"❌ QR Manager error: {e}")
            raise
    
    async def check_payment_status(self, qr_id: str) -> Dict:
        """
        Проверяет статус платежа по QR коду
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/{qr_id}/status",
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to check payment status: {e}")
            raise
    
    async def cancel_qr(self, qr_id: str) -> bool:
        """
        Отменяет QR код
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/{qr_id}/cancel",
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                logger.info(f"QR {qr_id} cancelled")
                return True
        except Exception as e:
            logger.error(f"Failed to cancel QR: {e}")
            return False


def get_qr_manager_client() -> QRManagerClient:
    """Получить экземпляр QR Manager клиента с настройками из конфига"""
    from app.config import settings
    return QRManagerClient(api_url=settings.QR_MANAGER_API_URL)


qr_manager_client = get_qr_manager_client()
