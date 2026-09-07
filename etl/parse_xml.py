"""XML parsing module for MoMo SMS data."""
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import xmltodict

logger = logging.getLogger(__name__)


class XMLParser:
    """Parse MoMo SMS data from XML format."""

    def __init__(self) -> None:
        """Initialize XML parser."""
        self.parser_name = "XMLParser"

    def parse_file(self, file_path: Path) -> list[dict[str, Any]]:
        """
        Parse XML file and extract transaction records.

        Args:
            file_path: Path to XML file

        Returns:
            List of parsed transaction records

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not valid XML
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                xml_content = f.read()

            # Parse XML to dictionary
            data = xmltodict.parse(xml_content)
            logger.info(f"Successfully parsed XML file: {file_path}")

            # Extract SMS records
            records = self._extract_records(data)
            logger.info(f"Extracted {len(records)} records from {file_path}")

            return records

        except Exception as e:
            logger.error(f"Error parsing XML file {file_path}: {str(e)}")
            raise ValueError(f"Invalid XML file: {str(e)}")

    def parse_content(self, xml_content: str) -> list[dict[str, Any]]:
        """
        Parse XML content string.

        Args:
            xml_content: XML content as string

        Returns:
            List of parsed transaction records
        """
        try:
            data = xmltodict.parse(xml_content)
            records = self._extract_records(data)
            logger.info(f"Extracted {len(records)} records from XML content")
            return records
        except Exception as e:
            logger.error(f"Error parsing XML content: {str(e)}")
            raise ValueError(f"Invalid XML: {str(e)}")

    def _extract_records(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract SMS records from parsed XML.

        Args:
            data: Parsed XML dictionary

        Returns:
            List of SMS records
        """
        records = []

        # Navigate to SMS records (adjust based on actual XML structure)
        if "root" in data:
            sms_list = data["root"].get("sms", [])
        elif "sms" in data:
            sms_list = data["sms"]
        else:
            logger.warning("Could not find SMS records in XML")
            return records

        # Ensure it's a list
        if not isinstance(sms_list, list):
            sms_list = [sms_list]

        for sms in sms_list:
            if isinstance(sms, dict):
                record = {
                    "raw_sms": sms.get("@body") or sms.get("body") or "",
                    "timestamp": self._parse_timestamp(sms),
                    "sender": sms.get("@address") or sms.get("address") or sms.get("sender") or "",
                    "original_data": sms,
                }
                records.append(record)

        return records

    @staticmethod
    def _parse_timestamp(sms: dict[str, Any]) -> datetime:
        """
        Parse timestamp from SMS record.

        Args:
            sms: SMS record dictionary

        Returns:
            Parsed datetime object
        """
        timestamp_str = sms.get("@date") or sms.get("date") or sms.get("timestamp") or ""

        if not timestamp_str:
            return datetime.utcnow()

        # Try multiple timestamp formats
        formats = [
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d-%m-%Y %H:%M:%S",
            "%d.%m.%Y %H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        logger.warning(f"Could not parse timestamp: {timestamp_str}")
        return datetime.utcnow()
