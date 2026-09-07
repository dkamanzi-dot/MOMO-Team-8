"""API routes for analytics."""
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import Transaction
from api.schemas import AnalyticsResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary", response_model=AnalyticsResponse)
async def get_analytics_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
) -> AnalyticsResponse:
    """Get analytics summary for transactions."""
    try:
        query = db.query(Transaction)

        # Apply date filters
        if start_date:
            query = query.filter(Transaction.timestamp >= start_date)
        if end_date:
            query = query.filter(Transaction.timestamp <= end_date)

        # Get total transactions and amount
        total_transactions = query.count()

        if total_transactions == 0:
            return AnalyticsResponse(
                total_transactions=0,
                total_amount=0.0,
                average_amount=0.0,
                transaction_count_by_type={},
                daily_volume=[],
                top_senders=[],
                top_recipients=[],
            )

        total_amount = query.with_entities(func.sum(Transaction.amount)).scalar() or 0.0
        average_amount = total_amount / total_transactions if total_transactions > 0 else 0.0

        # Get transaction count by type
        type_counts = (
            query.with_entities(
                Transaction.transaction_type,
                func.count(Transaction.id),
            )
            .group_by(Transaction.transaction_type)
            .all()
        )
        transaction_count_by_type = {
            str(t[0]): t[1] for t in type_counts
        }

        # Get daily volume
        daily_volume = (
            query.with_entities(
                func.date(Transaction.timestamp).label("date"),
                func.count(Transaction.id).label("count"),
                func.sum(Transaction.amount).label("amount"),
            )
            .group_by(func.date(Transaction.timestamp))
            .order_by(func.date(Transaction.timestamp))
            .all()
        )
        daily_volume_list = [
            {
                "date": str(d[0]),
                "count": d[1],
                "amount": float(d[2] or 0),
            }
            for d in daily_volume
        ]

        # Get top senders
        top_senders = (
            query.filter(Transaction.sender.isnot(None))
            .with_entities(
                Transaction.sender,
                func.count(Transaction.id).label("count"),
                func.sum(Transaction.amount).label("total_amount"),
            )
            .group_by(Transaction.sender)
            .order_by(func.count(Transaction.id).desc())
            .limit(10)
            .all()
        )
        top_senders_list = [
            {
                "sender": s[0],
                "count": s[1],
                "total_amount": float(s[2] or 0),
            }
            for s in top_senders
        ]

        # Get top recipients
        top_recipients = (
            query.filter(Transaction.recipient.isnot(None))
            .with_entities(
                Transaction.recipient,
                func.count(Transaction.id).label("count"),
                func.sum(Transaction.amount).label("total_amount"),
            )
            .group_by(Transaction.recipient)
            .order_by(func.count(Transaction.id).desc())
            .limit(10)
            .all()
        )
        top_recipients_list = [
            {
                "recipient": r[0],
                "count": r[1],
                "total_amount": float(r[2] or 0),
            }
            for r in top_recipients
        ]

        return AnalyticsResponse(
            total_transactions=total_transactions,
            total_amount=float(total_amount),
            average_amount=float(average_amount),
            transaction_count_by_type=transaction_count_by_type,
            daily_volume=daily_volume_list,
            top_senders=top_senders_list,
            top_recipients=top_recipients_list,
        )

    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/by-type")
async def get_analytics_by_type(db: Session = Depends(get_db)) -> dict:
    """Get transaction distribution by type."""
    try:
        results = (
            db.query(
                Transaction.transaction_type,
                func.count(Transaction.id).label("count"),
                func.sum(Transaction.amount).label("total_amount"),
                func.avg(Transaction.amount).label("avg_amount"),
            )
            .group_by(Transaction.transaction_type)
            .all()
        )

        return {
            "data": [
                {
                    "type": str(r[0]),
                    "count": r[1],
                    "total_amount": float(r[2] or 0),
                    "avg_amount": float(r[3] or 0),
                }
                for r in results
            ]
        }

    except Exception as e:
        logger.error(f"Error getting analytics by type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/by-date-range")
async def get_analytics_by_date_range(
    days: int = 30,
    db: Session = Depends(get_db),
) -> dict:
    """Get analytics for date range (last N days)."""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        results = (
            db.query(
                func.date(Transaction.timestamp).label("date"),
                func.count(Transaction.id).label("count"),
                func.sum(Transaction.amount).label("total_amount"),
                func.avg(Transaction.amount).label("avg_amount"),
            )
            .filter(Transaction.timestamp >= start_date)
            .group_by(func.date(Transaction.timestamp))
            .order_by(func.date(Transaction.timestamp))
            .all()
        )

        return {
            "period_days": days,
            "data": [
                {
                    "date": str(r[0]),
                    "count": r[1],
                    "total_amount": float(r[2] or 0),
                    "avg_amount": float(r[3] or 0),
                }
                for r in results
            ]
        }

    except Exception as e:
        logger.error(f"Error getting analytics by date range: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
