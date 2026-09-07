"""ETL Configuration Management."""
import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./momo_transactions.db")
    database_echo: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"

    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    # Data Paths
    raw_data_path: Path = Path(os.getenv("RAW_DATA_PATH", "./data/raw"))
    processed_data_path: Path = Path(os.getenv("PROCESSED_DATA_PATH", "./data/processed"))
    log_path: Path = Path(os.getenv("LOG_PATH", "./data/logs"))
    dead_letter_path: Path = Path(os.getenv("DEAD_LETTER_PATH", "./data/logs/dead_letter"))

    # Processing
    batch_size: int = int(os.getenv("BATCH_SIZE", "1000"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "100"))

    # Features
    enable_etl_logging: bool = os.getenv("ENABLE_ETL_LOGGING", "true").lower() == "true"
    enable_dead_letter_queue: bool = os.getenv("ENABLE_DEAD_LETTER_QUEUE", "true").lower() == "true"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False

    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.raw_data_path.mkdir(parents=True, exist_ok=True)
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
        self.log_path.mkdir(parents=True, exist_ok=True)
        self.dead_letter_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
