"""SQLAlchemy ORM Models for MoMo Transaction Database."""
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TransactionType(str, Enum):
    """Transaction type enumeration."""

    SEND_MONEY = "send_money"
    RECEIVE_MONEY = "receive_money"
    AIRTIME = "airtime"
    BILL_PAYMENT = "bill_payment"
    CASH_IN = "cash_in"
    CASH_OUT = "cash_out"
    MERCHANT = "merchant"
    OTHER = "other"


class TransactionStatus(str, Enum):
    """Transaction status enumeration."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REVERSED = "reversed"


class Transaction(Base):
    """MoMo Transaction Model."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Original XML data
    original_sms = Column(Text, nullable=False)
    
    # Parsed transaction data
    transaction_id = Column(String(100), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    
    # Parties involved
    sender = Column(String(50), index=True)
    recipient = Column(String(50), index=True)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="RWF")
    transaction_type = Column(SQLEnum(TransactionType), index=True, nullable=False)
    status = Column(SQLEnum(TransactionStatus), index=True, default=TransactionStatus.SUCCESS)
    
    # Balance information
    balance_before = Column(Float, nullable=True)
    balance_after = Column(Float, nullable=True)
    
    # Additional metadata
    description = Column(Text, nullable=True)
    reference = Column(String(255), nullable=True)
    fee = Column(Float, default=0.0)
    
    # Processing metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Transaction(id={self.id}, transaction_id={self.transaction_id}, "
            f"amount={self.amount}, type={self.transaction_type})>"
        )


class ProcessingLog(Base):
    """ETL Processing Logs."""

    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Processing information
    process_name = Column(String(100), index=True, nullable=False)
    status = Column(String(50), index=True, nullable=False)
    
    # Record counts
    records_processed = Column(Integer, default=0)
    records_successful = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_details = Column(Text, nullable=True)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # File information
    source_file = Column(String(255), nullable=True)
    dead_letter_count = Column(Integer, default=0)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<ProcessingLog(id={self.id}, process={self.process_name}, "
            f"status={self.status}, records={self.records_processed})>"
        )
