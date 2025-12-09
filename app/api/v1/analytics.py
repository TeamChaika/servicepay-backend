from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.venue import Venue
from app.models.event import Event
from app.models.payment import Payment, PaymentStatus
from app.models.ticket import Ticket
from app.dependencies import get_current_active_owner

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_analytics(
    venue_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Получить аналитику для dashboard"""
    # Базовые запросы для владельца
    venues_query = db.query(Venue).filter(Venue.owner_id == current_user.id)
    
    if venue_id:
        venues_query = venues_query.filter(Venue.id == venue_id)
        venue_ids = [venue_id]
    else:
        venue_ids = [v.id for v in venues_query.all()]
    
    # Статистика за последние 30 дней
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Количество мероприятий
    total_events = db.query(func.count(Event.id)).filter(
        Event.venue_id.in_(venue_ids)
    ).scalar()
    
    # Проданные билеты
    total_tickets = db.query(func.count(Ticket.id)).join(Event).filter(
        Event.venue_id.in_(venue_ids)
    ).scalar()
    
    # Доход
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.venue_id.in_(venue_ids),
        Payment.status == PaymentStatus.COMPLETED
    ).scalar() or 0
    
    # Доход за 30 дней
    recent_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.venue_id.in_(venue_ids),
        Payment.status == PaymentStatus.COMPLETED,
        Payment.paid_at >= thirty_days_ago
    ).scalar() or 0
    
    return {
        "total_venues": len(venue_ids),
        "total_events": total_events,
        "total_tickets_sold": total_tickets,
        "total_revenue": total_revenue,
        "recent_revenue_30d": recent_revenue,
        "currency": "RUB"
    }


@router.get("/revenue")
def get_revenue_analytics(
    venue_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_owner),
    db: Session = Depends(get_db)
):
    """Получить аналитику по доходам"""
    query = db.query(Payment).filter(Payment.status == PaymentStatus.COMPLETED)
    
    if venue_id:
        # Проверяем доступ
        venue = db.query(Venue).filter(
            Venue.id == venue_id,
            Venue.owner_id == current_user.id
        ).first()
        
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venue not found"
            )
        
        query = query.filter(Payment.venue_id == venue_id)
    else:
        # Все заведения владельца
        venue_ids = [v.id for v in db.query(Venue).filter(Venue.owner_id == current_user.id).all()]
        query = query.filter(Payment.venue_id.in_(venue_ids))
    
    if start_date:
        query = query.filter(Payment.paid_at >= start_date)
    
    if end_date:
        query = query.filter(Payment.paid_at <= end_date)
    
    # Группировка по типу платежа
    revenue_by_type = db.query(
        Payment.payment_type,
        func.count(Payment.id).label('count'),
        func.sum(Payment.amount).label('total')
    ).filter(
        Payment.id.in_([p.id for p in query.all()])
    ).group_by(Payment.payment_type).all()
    
    return {
        "revenue_by_type": [
            {
                "type": item.payment_type,
                "count": item.count,
                "total": item.total
            }
            for item in revenue_by_type
        ]
    }

