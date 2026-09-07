"""Transaction categorization module."""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class TransactionCategorizer:
    """Categorize MoMo transactions."""

    # Category mappings
    TRANSACTION_CATEGORIES = {
        "send_money": {
            "keywords": ["sent", "transfer", "send", "transferred"],
            "priority": 1,
        },
        "receive_money": {
            "keywords": ["received", "credit", "deposit", "incoming"],
            "priority": 1,
        },
        "airtime": {
            "keywords": ["airtime", "credit", "recharge", "air"],
            "priority": 1,
        },
        "bill_payment": {
            "keywords": ["bill", "payment", "electric", "water", "utility"],
            "priority": 2,
        },
        "cash_in": {
            "keywords": ["cash in", "deposit", "add money"],
            "priority": 1,
        },
        "cash_out": {
            "keywords": ["cash out", "withdrawal", "withdraw"],
            "priority": 1,
        },
        "merchant": {
            "keywords": ["merchant", "purchase", "shop", "store"],
            "priority": 2,
        },
    }

    def __init__(self) -> None:
        """Initialize transaction categorizer."""
        self.categorizer_name = "TransactionCategorizer"

    def categorize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """
        Categorize a transaction record.

        Args:
            record: Cleaned transaction record

        Returns:
            Record with category information
        """
        categorized = record.copy()

        # Use existing transaction_type if available
        if record.get("transaction_type") and record.get("transaction_type") != "other":
            categorized["category"] = record.get("transaction_type")
            categorized["confidence"] = 0.9
            logger.debug(f"Assigned category: {record.get('transaction_type')} (confidence: 0.9)")
            return categorized

        # Categorize based on SMS description
        sms_text = record.get("raw_sms", "").lower()
        category = self._find_category(sms_text)

        categorized["category"] = category["name"]
        categorized["confidence"] = category["confidence"]

        logger.debug(f"Categorized as: {category['name']} (confidence: {category['confidence']})")

        return categorized

    def categorize_batch(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Categorize a batch of records.

        Args:
            records: List of cleaned records

        Returns:
            List of categorized records
        """
        categorized_records = []

        for record in records:
            try:
                categorized = self.categorize_record(record)
                categorized_records.append(categorized)
            except Exception as e:
                logger.error(f"Error categorizing record: {str(e)}")
                # Keep the original record if categorization fails
                categorized_records.append(record)

        return categorized_records

    def _find_category(self, sms_text: str) -> dict[str, Any]:
        """
        Find the best matching category for SMS text.

        Args:
            sms_text: SMS text to categorize

        Returns:
            Dictionary with category name and confidence score
        """
        best_match = {"name": "other", "confidence": 0.0, "priority": 999}

        for category, info in self.TRANSACTION_CATEGORIES.items():
            keywords = info.get("keywords", [])
            priority = info.get("priority", 999)

            # Count keyword matches
            matches = sum(1 for keyword in keywords if keyword in sms_text)

            if matches > 0:
                # Calculate confidence based on number of matches
                confidence = min(matches / len(keywords), 1.0)

                # Prefer higher priority (lower number) with same or higher confidence
                if (
                    confidence > best_match["confidence"]
                    or (confidence == best_match["confidence"] and priority < best_match["priority"])
                ):
                    best_match = {
                        "name": category,
                        "confidence": confidence,
                        "priority": priority,
                    }

        return best_match

    def add_custom_category(self, name: str, keywords: list[str], priority: int = 3) -> None:
        """
        Add a custom transaction category.

        Args:
            name: Category name
            keywords: List of keywords to match
            priority: Priority level (lower = higher priority)
        """
        self.TRANSACTION_CATEGORIES[name] = {
            "keywords": keywords,
            "priority": priority,
        }
        logger.info(f"Added custom category: {name}")

    def get_category_statistics(self, records: list[dict[str, Any]]) -> dict[str, int]:
        """
        Get statistics of categorized records.

        Args:
            records: List of categorized records

        Returns:
            Dictionary with category counts
        """
        stats = {}

        for record in records:
            category = record.get("category", "other")
            stats[category] = stats.get(category, 0) + 1

        return stats
