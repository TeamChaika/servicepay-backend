from celery import Celery
from app.config import settings

celery_app = Celery(
    "helpchaika",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.payment_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.billing_tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Периодические задачи
celery_app.conf.beat_schedule = {
    "check-pending-payments": {
        "task": "app.tasks.payment_tasks.check_pending_payments",
        "schedule": 60.0,  # каждую минуту
    },
    "charge-monthly-subscription": {
        "task": "app.tasks.billing_tasks.charge_monthly_subscriptions",
        "schedule": 86400.0,  # раз в день
    },
    "check-low-balances": {
        "task": "app.tasks.billing_tasks.check_low_balances",
        "schedule": 3600.0,  # каждый час
    },
}

