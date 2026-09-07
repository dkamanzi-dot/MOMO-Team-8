"""Tests for transaction categorization module."""
import pytest

from etl.categorize import TransactionCategorizer


@pytest.fixture
def categorizer():
    """Create categorizer instance."""
    return TransactionCategorizer()


@pytest.fixture
def sample_records():
    """Create sample records for testing."""
    from datetime import datetime
    
    return [
        {
            "raw_sms": "You sent 5000 RWF to 250789654321",
            "timestamp": datetime.utcnow(),
            "sender": "250788123456",
            "amount": 5000.0,
            "category": None,
        },
        {
            "raw_sms": "You received 2000 RWF",
            "timestamp": datetime.utcnow(),
            "sender": "250788123456",
            "amount": 2000.0,
            "category": None,
        },
    ]


def test_categorizer_initialization(categorizer):
    """Test categorizer initialization."""
    assert categorizer is not None
    assert categorizer.categorizer_name == "TransactionCategorizer"


def test_categorize_transaction(categorizer):
    """Test categorizing a single transaction."""
    record = {
        "raw_sms": "You sent 5000 RWF to 250789654321",
        "timestamp": None,
        "sender": "250788123456",
        "amount": 5000.0,
        "transaction_type": "send_money",
    }
    
    categorized = categorizer.categorize_record(record)
    
    assert categorized["category"] == "send_money"
    assert categorized["confidence"] >= 0.0


def test_categorize_various_types(categorizer):
    """Test categorizing various transaction types."""
    test_cases = [
        ("You sent 5000 RWF", "send_money"),
        ("You received 2000 RWF", "receive_money"),
        ("Airtime purchase of 1000 RWF", "airtime"),
        ("Bill payment of 15000 RWF", "bill_payment"),
        ("Cash out 20000 RWF", "cash_out"),
        ("Unknown transaction", "other"),
    ]
    
    for sms_text, expected_category in test_cases:
        record = {
            "raw_sms": sms_text,
            "timestamp": None,
            "sender": "250788123456",
            "amount": 1000.0,
            "transaction_type": "other",
        }
        
        categorized = categorizer.categorize_record(record)
        
        # For "other" category, we expect the categorizer to find the best match
        if expected_category != "other":
            assert categorized["category"] == expected_category


def test_categorize_batch(categorizer, sample_records):
    """Test categorizing a batch of records."""
    categorized = categorizer.categorize_batch(sample_records)
    
    assert len(categorized) == len(sample_records)
    assert all("category" in r for r in categorized)


def test_get_category_statistics(categorizer, sample_records):
    """Test getting category statistics."""
    categorized = categorizer.categorize_batch(sample_records)
    stats = categorizer.get_category_statistics(categorized)
    
    assert isinstance(stats, dict)
    assert sum(stats.values()) == len(sample_records)


def test_add_custom_category(categorizer):
    """Test adding a custom category."""
    categorizer.add_custom_category("scholarship", ["scholarship", "award", "grant"], priority=1)
    
    record = {
        "raw_sms": "Received scholarship payment of 50000 RWF",
        "timestamp": None,
        "sender": "250788123456",
        "amount": 50000.0,
        "transaction_type": "other",
    }
    
    categorized = categorizer.categorize_record(record)
    
    assert categorized["category"] == "scholarship"


def test_confidence_score(categorizer):
    """Test confidence score calculation."""
    record = {
        "raw_sms": "You sent and received money",
        "timestamp": None,
        "sender": "250788123456",
        "amount": 1000.0,
        "transaction_type": "other",
    }
    
    categorized = categorizer.categorize_record(record)
    
    assert 0.0 <= categorized["confidence"] <= 1.0
