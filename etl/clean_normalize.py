"""Data cleaning and normalization module."""
import logging
import re
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DataCleaner:
    """Clean and normalize MoMo transaction SMS data."""

    def __init__(self) -> None:
        """Initialize data cleaner."""
        self.cleaner_name = "DataCleaner"

    def clean_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """
        Clean and normalize a single transaction record.

        Args:
            record: Raw transaction record

        Returns:
            Cleaned transaction record
        """
        try:
            cleaned = {
                "raw_sms": record.get("raw_sms", "").strip(),
                "timestamp": record.get("timestamp", datetime.utcnow()),
                "sender": self._clean_phone_number(record.get("sender", "")),
                "original_data": record.get("original_data", {}),
            }

            # Extract transaction details from SMS text
            sms_text = cleaned["raw_sms"]
            extracted = self._extract_transaction_details(sms_text)
            cleaned.update(extracted)

            logger.debug(f"Cleaned record: {cleaned}")
            return cleaned

        except Exception as e:
            logger.error(f"Error cleaning record: {str(e)}")
            raise

    def clean_batch(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Clean a batch of records.

        Args:
            records: List of raw records

        Returns:
            List of cleaned records
        """
        cleaned_records = []
        errors = []

        for i, record in enumerate(records):
            try:
                cleaned = self.clean_record(record)
                cleaned_records.append(cleaned)
            except Exception as e:
                logger.warning(f"Failed to clean record {i}: {str(e)}")
                errors.append({"index": i, "error": str(e), "record": record})

        if errors:
            logger.warning(f"Failed to clean {len(errors)} out of {len(records)} records")

        return cleaned_records

    @staticmethod
    def _clean_phone_number(phone: str) -> str:
        """
        Clean and normalize phone number.

        Args:
            phone: Raw phone number string

        Returns:
            Cleaned phone number
        """
        if not phone:
            return ""

        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r"[\s\-().]", "", phone)

        # Remove leading +
        if cleaned.startswith("+"):
            cleaned = cleaned[1:]

        # Ensure it starts with country code (250 for Rwanda)
        if len(cleaned) == 10 and cleaned.startswith("7"):
            cleaned = "250" + cleaned[1:]
        elif len(cleaned) == 9 and cleaned.startswith("7"):
            cleaned = "250" + cleaned

        return cleaned

    @staticmethod
    def _extract_transaction_details(sms_text: str) -> dict[str, Any]:
        """
        Extract transaction details from SMS text.

        Args:
            sms_text: Raw SMS text

        Returns:
            Dictionary with extracted details
        """
        details = {
            "amount": None,
            "recipient": None,
            "transaction_type": "other",
            "description": sms_text[:100],
        }

        if not sms_text:
            return details

        # Convert to lowercase for pattern matching
        text_lower = sms_text.lower()

        # Extract amount (look for numbers followed by currency or digit patterns)
        amount_match = re.search(r"([\d,]+(?:\.\d{1,2})?)\s*(rwf|frw|kr)?", text_lower)
        if amount_match:
            amount_str = amount_match.group(1).replace(",", "")
            try:
                details["amount"] = float(amount_str)
            except ValueError:
                logger.warning(f"Could not parse amount: {amount_str}")

        # Extract recipient phone number (if present)
        phone_pattern = r"(?:to|from|account|a/c|recipient|receiver|sms from)[\s:]*([0-9]{9,13})"
        phone_match = re.search(phone_pattern, text_lower)
        if phone_match:
            details["recipient"] = DataCleaner._clean_phone_number(phone_match.group(1))

        # Classify transaction type
        if any(word in text_lower for word in ["airtime", "credit", "recharge"]):
            details["transaction_type"] = "airtime"
        elif any(word in text_lower for word in ["sent", "transfer", "send"]):
            details["transaction_type"] = "send_money"
        elif any(word in text_lower for word in ["received", "credit", "deposit"]):
            details["transaction_type"] = "receive_money"
        elif any(word in text_lower for word in ["bill", "payment", "electric", "water"]):
            details["transaction_type"] = "bill_payment"
        elif any(word in text_lower for word in ["cash out", "withdrawal"]):
            details["transaction_type"] = "cash_out"
        elif any(word in text_lower for word in ["cash in", "deposit"]):
            details["transaction_type"] = "cash_in"
        elif any(word in text_lower for word in ["merchant", "purchase", "payment"]):
            details["transaction_type"] = "merchant"

        return details
