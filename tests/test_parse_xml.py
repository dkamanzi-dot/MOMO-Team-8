"""Tests for XML parsing module."""
import pytest
from pathlib import Path
from datetime import datetime

from etl.parse_xml import XMLParser


@pytest.fixture
def parser():
    """Create parser instance."""
    return XMLParser()


@pytest.fixture
def sample_xml_file(tmp_path):
    """Create a sample XML file for testing."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <sms @date="01/01/2024 10:30:00" @address="250788123456" @body="You sent 5000 RWF to 250789654321"/>
    <sms @date="01/01/2024 11:15:00" @address="250787654321" @body="You received 2000 RWF from 250788123456"/>
    <sms @date="01/01/2024 12:00:00" @address="250789012345" @body="Airtime purchase of 1000 RWF successful"/>
</root>
"""
    file_path = tmp_path / "test_data.xml"
    file_path.write_text(xml_content)
    return file_path


def test_parser_initialization(parser):
    """Test parser initialization."""
    assert parser is not None
    assert parser.parser_name == "XMLParser"


def test_parse_valid_xml_file(parser, sample_xml_file):
    """Test parsing a valid XML file."""
    records = parser.parse_file(sample_xml_file)
    
    assert len(records) == 3
    assert all(isinstance(r, dict) for r in records)
    assert "raw_sms" in records[0]
    assert "timestamp" in records[0]


def test_parse_nonexistent_file(parser, tmp_path):
    """Test parsing a nonexistent file."""
    nonexistent_file = tmp_path / "nonexistent.xml"
    
    with pytest.raises(FileNotFoundError):
        parser.parse_file(nonexistent_file)


def test_parse_invalid_xml(parser, tmp_path):
    """Test parsing invalid XML content."""
    invalid_xml = tmp_path / "invalid.xml"
    invalid_xml.write_text("This is not valid XML!")
    
    with pytest.raises(ValueError):
        parser.parse_file(invalid_xml)


def test_parse_content_string(parser):
    """Test parsing XML content as string."""
    xml_content = """<?xml version="1.0"?>
    <root>
        <sms @body="Test SMS" @address="250788123456" @date="01/01/2024 10:00:00"/>
    </root>
    """
    records = parser.parse_content(xml_content)
    
    assert len(records) == 1
    assert records[0]["raw_sms"] == "Test SMS"
    assert records[0]["sender"] == "250788123456"


def test_timestamp_parsing(parser):
    """Test various timestamp formats."""
    xml_samples = [
        ('01/01/2024 10:30:00', "%d/%m/%Y %H:%M:%S"),
        ('2024-01-01 10:30:00', "%Y-%m-%d %H:%M:%S"),
    ]
    
    for timestamp_str, fmt in xml_samples:
        xml = f"""<?xml version="1.0"?>
        <root>
            <sms @date="{timestamp_str}" @address="250788123456" @body="Test"/>
        </root>
        """
        records = parser.parse_content(xml)
        assert len(records) == 1
        assert isinstance(records[0]["timestamp"], datetime)
