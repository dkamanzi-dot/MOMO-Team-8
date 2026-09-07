"""ETL Pipeline - Main orchestrator."""
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from api.db import SessionLocal, get_db, init_db
from etl.categorize import TransactionCategorizer
from etl.clean_normalize import DataCleaner
from etl.config import settings
from etl.load_db import DatabaseLoader
from etl.parse_xml import XMLParser

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """Main ETL pipeline orchestrator."""

    def __init__(self, db: Session) -> None:
        """
        Initialize ETL pipeline.

        Args:
            db: SQLAlchemy session
        """
        self.db = db
        self.parser = XMLParser()
        self.cleaner = DataCleaner()
        self.categorizer = TransactionCategorizer()
        self.loader = DatabaseLoader(db)

        logger.info("ETL Pipeline initialized")

    def process_file(self, file_path: Path) -> dict[str, Any]:
        """
        Process a single XML file through the entire pipeline.

        Args:
            file_path: Path to XML file

        Returns:
            Dictionary with processing results
        """
        logger.info(f"Starting ETL pipeline for file: {file_path}")

        results = {
            "file": str(file_path),
            "stages": {},
            "total_records": 0,
            "successful_records": 0,
            "failed_records": 0,
        }

        try:
            # Stage 1: Parse XML
            logger.info("Stage 1: Parsing XML")
            parsed_records = self.parser.parse_file(file_path)
            results["stages"]["parse"] = {
                "records": len(parsed_records),
                "status": "success",
            }
            results["total_records"] = len(parsed_records)
            logger.info(f"Parsed {len(parsed_records)} records")

            # Stage 2: Clean and Normalize
            logger.info("Stage 2: Cleaning and normalizing data")
            cleaned_records = self.cleaner.clean_batch(parsed_records)
            results["stages"]["clean"] = {
                "records": len(cleaned_records),
                "status": "success",
            }
            logger.info(f"Cleaned {len(cleaned_records)} records")

            # Stage 3: Categorize
            logger.info("Stage 3: Categorizing transactions")
            categorized_records = self.categorizer.categorize_batch(cleaned_records)
            results["stages"]["categorize"] = {
                "records": len(categorized_records),
                "status": "success",
            }
            logger.info(f"Categorized {len(categorized_records)} records")

            # Stage 4: Load to Database
            logger.info("Stage 4: Loading to database")
            load_stats = self.loader.load_batch(categorized_records)
            results["stages"]["load"] = load_stats
            results["successful_records"] = load_stats.get("successful", 0)
            results["failed_records"] = load_stats.get("failed", 0)

            logger.info(f"Loaded {results['successful_records']} records to database")

            # Log processing
            self.loader.log_processing("ETL_PIPELINE", load_stats)

            logger.info(f"ETL pipeline completed successfully for {file_path}")
            results["status"] = "success"

        except Exception as e:
            logger.error(f"Error in ETL pipeline: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
            self.loader.log_processing("ETL_PIPELINE", results, error=str(e))

        return results

    def process_directory(self, directory_path: Path) -> dict[str, Any]:
        """
        Process all XML files in a directory.

        Args:
            directory_path: Path to directory containing XML files

        Returns:
            Dictionary with processing results for all files
        """
        logger.info(f"Starting batch ETL processing for directory: {directory_path}")

        results = {
            "directory": str(directory_path),
            "files": [],
            "total_files": 0,
            "successful_files": 0,
            "failed_files": 0,
            "total_records": 0,
        }

        if not directory_path.exists():
            logger.error(f"Directory not found: {directory_path}")
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        # Find all XML files
        xml_files = list(directory_path.glob("*.xml"))
        results["total_files"] = len(xml_files)

        logger.info(f"Found {len(xml_files)} XML files to process")

        for xml_file in xml_files:
            try:
                file_results = self.process_file(xml_file)
                results["files"].append(file_results)

                if file_results.get("status") == "success":
                    results["successful_files"] += 1
                else:
                    results["failed_files"] += 1

                results["total_records"] += file_results.get("total_records", 0)

            except Exception as e:
                logger.error(f"Error processing file {xml_file}: {str(e)}")
                results["failed_files"] += 1
                results["files"].append(
                    {
                        "file": str(xml_file),
                        "status": "failed",
                        "error": str(e),
                    }
                )

        logger.info(
            f"Batch processing completed: {results['successful_files']} "
            f"successful, {results['failed_files']} failed"
        )

        return results


def run_etl(file_path: str) -> None:
    """
    Run ETL pipeline on specified file.

    Args:
        file_path: Path to XML file or directory
    """
    # Initialize database
    init_db()

    # Create database session
    db = SessionLocal()

    try:
        path = Path(file_path)

        # Initialize pipeline
        pipeline = ETLPipeline(db)

        # Process file or directory
        if path.is_file():
            results = pipeline.process_file(path)
        elif path.is_dir():
            results = pipeline.process_directory(path)
        else:
            logger.error(f"Path not found: {path}")
            return

        # Print results
        logger.info(f"Processing results: {results}")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run MoMo ETL Pipeline")
    parser.add_argument("input", help="Path to XML file or directory")
    args = parser.parse_args()

    run_etl(args.input)
