"""API routes for transaction management."""
import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import Transaction
from api.schemas import TransactionCreate, TransactionListResponse, TransactionResponse, TransactionUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
) -> TransactionResponse:
    """Create a new transaction record."""
    try:
        # Check if transaction already exists
        existing = (
            db.query(Transaction)
            .filter(Transaction.transaction_id == transaction.transaction_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Transaction with this ID already exists",
            )

        # Create new transaction
        db_transaction = Transaction(**transaction.model_dump())
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)

        return TransactionResponse.model_validate(db_transaction)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=TransactionListResponse)
async def list_transactions(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    transaction_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
) -> TransactionListResponse:
    """List transactions with pagination and filtering."""
    try:
        query = db.query(Transaction)

        # Apply filters
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        if status:
            query = query.filter(Transaction.status == status)

        # Get total count
        total = query.count()

        # Apply pagination
        items = query.offset(skip).limit(limit).all()

        return TransactionListResponse(
            total=total,
            page=skip // limit + 1,
            page_size=limit,
            items=[TransactionResponse.model_validate(item) for item in items],
        )

    except Exception as e:
        logger.error(f"Error listing transactions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
) -> TransactionResponse:
    """Get a specific transaction by ID."""
    try:
        transaction = (
            db.query(Transaction)
            .filter(Transaction.transaction_id == transaction_id)
            .first()
        )

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return TransactionResponse.model_validate(transaction)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    update_data: TransactionUpdate,
    db: Session = Depends(get_db),
) -> TransactionResponse:
    """Update a transaction record."""
    try:
        transaction = (
            db.query(Transaction)
            .filter(Transaction.transaction_id == transaction_id)
            .first()
        )

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(transaction, key, value)

        db.commit()
        db.refresh(transaction)

        return TransactionResponse.model_validate(transaction)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating transaction: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
) -> None:
    """Delete a transaction record."""
    try:
        transaction = (
            db.query(Transaction)
            .filter(Transaction.transaction_id == transaction_id)
            .first()
        )

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        db.delete(transaction)
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transaction: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
