"""Pydantic schemas for request/response validation."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


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


class TransactionBase(BaseModel):
    """Base schema for transaction data."""

    transaction_id: str
    timestamp: datetime
    sender: Optional[str] = None
    recipient: Optional[str] = None
    amount: float
    currency: str = "RWF"
    transaction_type: TransactionType
    status: TransactionStatus = TransactionStatus.SUCCESS
    balance_before: Optional[float] = None
    balance_after: Optional[float] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    fee: float = 0.0


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction."""

    original_sms: str


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""

    status: Optional[TransactionStatus] = None
    balance_after: Optional[float] = None
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Schema for returning transaction data."""

    id: int
    original_sms: str
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class TransactionListResponse(BaseModel):
    """Schema for returning list of transactions with pagination."""

    total: int
    page: int
    page_size: int
    items: list[TransactionResponse]


class ProcessingLogCreate(BaseModel):
    """Schema for creating processing log."""

    process_name: str
    records_processed: int = 0
    records_successful: int = 0
    records_failed: int = 0
    source_file: Optional[str] = None
    dead_letter_count: int = 0


class ProcessingLogResponse(BaseModel):
    """Schema for returning processing log."""

    id: int
    process_name: str
    status: str
    records_processed: int
    records_successful: int
    records_failed: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    source_file: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class AnalyticsResponse(BaseModel):
    """Schema for analytics data."""

    total_transactions: int = Field(..., description="Total number of transactions")
    total_amount: float = Field(..., description="Total transaction amount")
    average_amount: float = Field(..., description="Average transaction amount")
    transaction_count_by_type: dict = Field(..., description="Count by transaction type")
    daily_volume: list[dict] = Field(..., description="Daily transaction volume")
    top_senders: list[dict] = Field(..., description="Top senders")
    top_recipients: list[dict] = Field(..., description="Top recipients")


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""

    status: str
    database: str
    version: str = "1.0.0"
