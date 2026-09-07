"""Tests for data cleaning and normalization module."""
import pytest

from etl.clean_normalize import DataCleaner


@pytest.fixture
def cleaner():
    """Create cleaner instance."""
    return DataCleaner()


@pytest.fixture
def sample_record():
    """Create sample transaction record."""
    from datetime import datetime
    
    return {
        "raw_sms": "You sent 5000 RWF to +250 789 654 321",
        "timestamp": datetime.utcnow(),
        "sender": "+250-788-123-456",
        "original_data": {},
    }


def test_cleaner_initialization(cleaner):
    """Test cleaner initialization."""
    assert cleaner is not None
    assert cleaner.cleaner_name == "DataCleaner"


def test_clean_phone_number(cleaner):
    """Test phone number cleaning."""
    test_cases = [
        ("+250 788 123 456", "250788123456"),
        ("+250-788-123-456", "250788123456"),
        ("0788123456", "250788123456"),
        ("788123456", "250788123456"),
    ]
    
    for input_phone, expected in test_cases:
        result = cleaner._clean_phone_number(input_phone)
        assert result == expected


def test_clean_record(cleaner, sample_record):
    """Test cleaning a single record."""
    cleaned = cleaner.clean_record(sample_record)
    
    assert cleaned["sender"] == "250788123456"
    assert cleaned["raw_sms"] == "You sent 5000 RWF to +250 789 654 321"
    assert "amount" in cleaned
    assert "transaction_type" in cleaned


def test_extract_transaction_details(cleaner):
    """Test extracting transaction details from SMS."""
    test_cases = [
        ("You sent 5000 RWF to 250789654321", {"amount": 5000.0, "transaction_type": "send_money"}),
        ("You received 2000 RWF from 250788123456", {"amount": 2000.0, "transaction_type": "receive_money"}),
        ("Airtime purchase of 1000 RWF successful", {"amount": 1000.0, "transaction_type": "airtime"}),
        ("Bill payment of 15000 RWF completed", {"amount": 15000.0, "transaction_type": "bill_payment"}),
    ]
    
    for sms_text, expected in test_cases:
        result = cleaner._extract_transaction_details(sms_text)
        
        if "amount" in expected:
            assert result["amount"] == expected["amount"]
        if "transaction_type" in expected:
            assert result["transaction_type"] == expected["transaction_type"]


def test_clean_batch(cleaner):
    """Test cleaning a batch of records."""
    from datetime import datetime
    
    records = [
        {
            "raw_sms": "Sent 1000 RWF to 0789654321",
            "timestamp": datetime.utcnow(),
            "sender": "0788123456",
            "original_data": {},
        },
        {
            "raw_sms": "Received 2000 RWF from 0788654321",
            "timestamp": datetime.utcnow(),
            "sender": "0789123456",
            "original_data": {},
        },
    ]
    
    cleaned = cleaner.clean_batch(records)
    
    assert len(cleaned) == 2
    assert all(isinstance(r, dict) for r in cleaned)


def test_empty_record(cleaner):
    """Test cleaning empty record."""
    empty_record = {
        "raw_sms": "",
        "timestamp": None,
        "sender": "",
        "original_data": {},
    }
    
    cleaned = cleaner.clean_record(empty_record)
    
    assert cleaned["sender"] == ""
    assert cleaned["raw_sms"] == ""
