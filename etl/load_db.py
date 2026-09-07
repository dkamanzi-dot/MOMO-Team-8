"""Database loading module for storing processed transactions."""
import logging
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from api.models import ProcessingLog, Transaction, TransactionStatus, TransactionType

logger = logging.getLogger(__name__)


class DatabaseLoader:
    """Load processed transactions into the database."""

    def __init__(self, db: Session) -> None:
        """
        Initialize database loader.

        Args:
            db: SQLAlchemy session
        """
        self.db = db
        self.loader_name = "DatabaseLoader"

    def load_record(self, record: dict[str, Any]) -> Optional[Transaction]:
        """
        Load a single transaction record into database.

        Args:
            record: Cleaned and categorized transaction record

        Returns:
            Created Transaction object or None if failed
        """
        try:
            # Extract data from record
            transaction_id = self._generate_transaction_id(record)

            # Check if transaction already exists
            existing = self.db.query(Transaction).filter_by(transaction_id=transaction_id).first()
            if existing:
                logger.debug(f"Transaction already exists: {transaction_id}")
                return existing

            # Map category to TransactionType
            transaction_type = self._map_category_to_type(record.get("category", "other"))

            # Create transaction object
            transaction = Transaction(
                original_sms=record.get("raw_sms", ""),
                transaction_id=transaction_id,
                timestamp=record.get("timestamp", datetime.utcnow()),
                sender=record.get("sender"),
                recipient=record.get("recipient"),
                amount=record.get("amount", 0.0),
                currency=record.get("currency", "RWF"),
                transaction_type=transaction_type,
                status=self._determine_status(record),
                balance_before=record.get("balance_before"),
                balance_after=record.get("balance_after"),
                description=record.get("description"),
                reference=record.get("reference"),
                fee=record.get("fee", 0.0),
                processed_at=datetime.utcnow(),
            )

            self.db.add(transaction)
            self.db.flush()

            logger.debug(f"Loaded transaction: {transaction_id}")
            return transaction

        except Exception as e:
            logger.error(f"Error loading record into database: {str(e)}")
            self.db.rollback()
            return None

    def load_batch(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Load a batch of records into database.

        Args:
            records: List of cleaned and categorized records

        Returns:
            Dictionary with load statistics
        """
        stats = {
            "total": len(records),
            "successful": 0,
            "failed": 0,
            "duplicates": 0,
            "errors": [],
        }

        for i, record in enumerate(records):
            try:
                result = self.load_record(record)
                if result:
                    stats["successful"] += 1
                else:
                    stats["duplicates"] += 1
            except Exception as e:
                logger.error(f"Error loading record {i}: {str(e)}")
                stats["failed"] += 1
                stats["errors"].append({"index": i, "error": str(e)})

        # Commit all changes
        try:
            self.db.commit()
            logger.info(f"Batch load completed: {stats}")
        except Exception as e:
            logger.error(f"Error committing batch: {str(e)}")
            self.db.rollback()
            stats["failed"] = len(records)
            stats["successful"] = 0

        return stats

    def log_processing(self, process_name: str, stats: dict[str, Any], error: Optional[str] = None) -> ProcessingLog:
        """
        Log ETL processing information.

        Args:
            process_name: Name of the process
            stats: Processing statistics
            error: Error message if any

        Returns:
            Created ProcessingLog object
        """
        try:
            log = ProcessingLog(
                process_name=process_name,
                status="success" if stats.get("failed", 0) == 0 else "partial_failure",
                records_processed=stats.get("total", 0),
                records_successful=stats.get("successful", 0),
                records_failed=stats.get("failed", 0),
                error_message=error,
                dead_letter_count=stats.get("dead_letter_count", 0),
                completed_at=datetime.utcnow(),
            )

            self.db.add(log)
            self.db.commit()

            logger.info(f"Processing log created: {log}")
            return log

        except Exception as e:
            logger.error(f"Error creating processing log: {str(e)}")
            self.db.rollback()
            raise

    @staticmethod
    def _generate_transaction_id(record: dict[str, Any]) -> str:
        """
        Generate a unique transaction ID.

        Args:
            record: Transaction record

        Returns:
            Unique transaction ID
        """
        import hashlib

        # Create ID from sender, recipient, amount, and timestamp
        id_components = (
            f"{record.get('sender', '')}-"
            f"{record.get('recipient', '')}-"
            f"{record.get('amount', '')}-"
            f"{record.get('timestamp', '')}"
        )

        return hashlib.md5(id_components.encode()).hexdigest()[:16]

    @staticmethod
    def _map_category_to_type(category: str) -> TransactionType:
        """
        Map category to TransactionType enum.

        Args:
            category: Category string

        Returns:
            TransactionType enum value
        """
        category_map = {
            "send_money": TransactionType.SEND_MONEY,
            "receive_money": TransactionType.RECEIVE_MONEY,
            "airtime": TransactionType.AIRTIME,
            "bill_payment": TransactionType.BILL_PAYMENT,
            "cash_in": TransactionType.CASH_IN,
            "cash_out": TransactionType.CASH_OUT,
            "merchant": TransactionType.MERCHANT,
        }

        return category_map.get(category, TransactionType.OTHER)

    @staticmethod
    def _determine_status(record: dict[str, Any]) -> TransactionStatus:
        """
        Determine transaction status.

        Args:
            record: Transaction record

        Returns:
            TransactionStatus enum value
        """
        status = record.get("status", "success").lower()

        status_map = {
            "success": TransactionStatus.SUCCESS,
            "pending": TransactionStatus.PENDING,
            "failed": TransactionStatus.FAILED,
            "reversed": TransactionStatus.REVERSED,
        }

        return status_map.get(status, TransactionStatus.SUCCESS)
