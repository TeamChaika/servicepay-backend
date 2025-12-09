from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class TransactionType(str, enum.Enum):
    TOPUP = "topup"
    PAYMENT = "payment"
    COMMISSION = "commission"
    REFUND = "refund"
    WITHDRAWAL = "withdrawal"
    SUBSCRIPTION = "subscription"


class Balance(Base):
    __tablename__ = "balances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Баланс в копейках
    amount = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="balance")
    transactions = relationship("BalanceTransaction", back_populates="balance", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Balance {self.user_id} - {self.amount}>"


class BalanceTransaction(Base):
    __tablename__ = "balance_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    balance_id = Column(UUID(as_uuid=True), ForeignKey("balances.id"), nullable=False)
    
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # положительное для пополнения, отрицательное для списания
    
    balance_before = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    
    description = Column(Text)
    reference_id = Column(UUID(as_uuid=True))  # ID связанного платежа/возврата
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    balance = relationship("Balance", back_populates="transactions")
    
    def __repr__(self):
        return f"<BalanceTransaction {self.transaction_type} - {self.amount}>"

