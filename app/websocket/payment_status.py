from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import logging

logger = logging.getLogger(__name__)


class PaymentStatusManager:
    def __init__(self):
        # payment_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, payment_id: str):
        await websocket.accept()
        
        if payment_id not in self.active_connections:
            self.active_connections[payment_id] = set()
        
        self.active_connections[payment_id].add(websocket)
        logger.info(f"WebSocket connected for payment {payment_id}")
    
    def disconnect(self, websocket: WebSocket, payment_id: str):
        if payment_id in self.active_connections:
            self.active_connections[payment_id].discard(websocket)
            
            if not self.active_connections[payment_id]:
                del self.active_connections[payment_id]
        
        logger.info(f"WebSocket disconnected for payment {payment_id}")
    
    async def send_status_update(self, payment_id: str, status: str, data: dict = None):
        """Отправить обновление статуса всем подключенным клиентам"""
        if payment_id not in self.active_connections:
            return
        
        message = {
            "payment_id": payment_id,
            "status": status,
            "data": data or {}
        }
        
        disconnected = set()
        
        for connection in self.active_connections[payment_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)
        
        # Удаляем отключенные соединения
        for connection in disconnected:
            self.disconnect(connection, payment_id)
    
    async def broadcast(self, message: dict):
        """Отправить сообщение всем подключенным клиентам"""
        for payment_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting message: {e}")


payment_status_manager = PaymentStatusManager()

