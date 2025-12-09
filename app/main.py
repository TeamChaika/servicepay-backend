from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.config import settings
from app.database import engine, Base
from app.api.v1 import (
    auth, venues, events, payments, deposits, 
    tickets, balance, staff, refunds, reviews, 
    analytics, webhooks, terminals
)
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Создание таблиц (в production используйте Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="SaaS платформа для кафе и ресторанов",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Роуты
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(venues.router, prefix="/api/v1/venues", tags=["venues"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(deposits.router, prefix="/api/v1/deposits", tags=["deposits"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["tickets"])
app.include_router(balance.router, prefix="/api/v1/balance", tags=["balance"])
app.include_router(staff.router, prefix="/api/v1/staff", tags=["staff"])
app.include_router(refunds.router, prefix="/api/v1/refunds", tags=["refunds"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["reviews"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(terminals.router, prefix="/api/v1/terminals", tags=["terminals"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

