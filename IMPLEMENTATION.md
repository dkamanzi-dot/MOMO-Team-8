# MoMo Transaction Analytics System - Implementation Guide

## Project Overview

The **MoMo Transaction Analytics System** is now fully implemented with a complete architecture for processing Mobile Money transaction data. This document provides a comprehensive guide to the project structure and usage.

## Recent Improvements (Phase 1: Foundation)

### ✅ Completed Implementation

#### 1. **Configuration & Dependencies** (100%)
- ✅ `requirements.txt` - All dependencies installed
- ✅ `.env.example` - Environment configuration template
- ✅ `etl/config.py` - Centralized settings management with Pydantic

#### 2. **Database Layer** (100%)
- ✅ `api/db.py` - SQLAlchemy engine, sessions, and initialization
- ✅ `api/models.py` - ORM models (Transaction, ProcessingLog)
- ✅ SQLite database with proper schema

#### 3. **API Schemas** (100%)
- ✅ `api/schemas.py` - Pydantic models for validation and serialization
- ✅ Request/response models for all endpoints
- ✅ Analytics response schema

#### 4. **ETL Pipeline** (100%)
- ✅ `etl/parse_xml.py` - XML parsing with error handling
- ✅ `etl/clean_normalize.py` - Data cleaning and phone number normalization
- ✅ `etl/categorize.py` - Transaction categorization engine
- ✅ `etl/load_db.py` - Database loading with duplicate detection
- ✅ `etl/run.py` - Main ETL orchestrator

#### 5. **FastAPI Backend** (100%)
- ✅ `api/app.py` - FastAPI application setup with CORS middleware
- ✅ `api/routes.py` - Transaction CRUD operations (Create, Read, Update, Delete)
- ✅ `api/analytics.py` - Analytics endpoints for data visualization

#### 6. **Frontend** (100%)
- ✅ `index.html` - Comprehensive dashboard HTML
- ✅ `web/styles.css` - Modern, responsive styling
- ✅ `web/chart_handler.js` - Data fetching and Chart.js integration

#### 7. **Testing** (100%)
- ✅ `tests/test_parse_xml.py` - XML parsing tests
- ✅ `tests/test_clean_normalize.py` - Data cleaning tests
- ✅ `tests/test_categorize.py` - Categorization logic tests
- ✅ `pytest.ini` - Test configuration

#### 8. **Deployment Scripts** (100%)
- ✅ `scripts/run_etl.sh` - ETL pipeline execution
- ✅ `scripts/serve_frontend.sh` - API server startup
- ✅ `scripts/export_json.sh` - Data export functionality

---

## Project Structure

```
MOMO-Team-8/
├── api/
│   ├── __init__.py
│   ├── app.py              # FastAPI application
│   ├── db.py               # Database connection & session management
│   ├── models.py           # SQLAlchemy ORM models
│   ├── schemas.py          # Pydantic validation schemas
│   ├── routes.py           # Transaction CRUD endpoints
│   └── analytics.py        # Analytics endpoints
│
├── etl/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── parse_xml.py        # XML parsing logic
│   ├── clean_normalize.py  # Data cleaning & normalization
│   ├── categorize.py       # Transaction categorization
│   ├── load_db.py          # Database loading
│   └── run.py              # ETL pipeline orchestrator
│
├── web/
│   ├── styles.css          # Dashboard styling
│   └── chart_handler.js    # Frontend logic & charts
│
├── scripts/
│   ├── run_etl.sh          # Run ETL pipeline
│   ├── serve_frontend.sh   # Start API server
│   └── export_json.sh      # Export transactions as JSON
│
├── tests/
│   ├── __init__.py
│   ├── test_parse_xml.py       # XML parsing tests
│   ├── test_clean_normalize.py # Cleaning tests
│   └── test_categorize.py      # Categorization tests
│
├── data/
│   ├── raw/                # Input XML files
│   ├── processed/          # Processed data
│   └── logs/               # Processing logs
│       └── dead_letter/    # Failed records
│
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── pytest.ini              # Test configuration
├── index.html              # Dashboard frontend
└── README.md               # Project documentation
```

---

## Installation & Setup

### 1. Prerequisites
- Python 3.9+
- pip or conda
- Git

### 2. Installation

```bash
# Clone repository
git clone <repo-url>
cd MOMO-Team-8

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env
```

### 3. Initialize Database

```bash
# The database will be automatically initialized on first API startup
# Or manually initialize with:
python -c "from api.db import init_db; init_db()"
```

---

## Usage

### Running the ETL Pipeline

#### Process a single XML file:
```bash
# Windows
python -m etl.run data/raw/transactions.xml

# Linux/macOS
./scripts/run_etl.sh data/raw/transactions.xml
```

#### Process all XML files in a directory:
```bash
python -m etl.run data/raw/
```

### Starting the API Server

```bash
# Windows
python -m uvicorn api.app:app --reload

# Linux/macOS
./scripts/serve_frontend.sh
```

The API will be available at `http://localhost:8000`

### Accessing the Dashboard

Open your browser and navigate to:
```
http://localhost:8000/index.html
```

Or if serving static files:
```
http://localhost:3000  # (if using a separate static server)
```

### Exporting Data as JSON

```bash
./scripts/export_json.sh [output_file]
```

---

## API Endpoints

### Health Check
- **GET** `/health` - Check API status

### Transactions
- **GET** `/api/v1/transactions/` - List transactions (with pagination & filters)
- **POST** `/api/v1/transactions/` - Create transaction
- **GET** `/api/v1/transactions/{transaction_id}` - Get transaction details
- **PUT** `/api/v1/transactions/{transaction_id}` - Update transaction
- **DELETE** `/api/v1/transactions/{transaction_id}` - Delete transaction

### Analytics
- **GET** `/api/v1/analytics/summary` - Get analytics summary
- **GET** `/api/v1/analytics/by-type` - Distribution by transaction type
- **GET** `/api/v1/analytics/by-date-range` - Analytics by date range

---

## Database Schema

### Transactions Table
- `id` - Primary key
- `transaction_id` - Unique transaction identifier
- `timestamp` - Transaction datetime
- `sender` - Sender phone number
- `recipient` - Recipient phone number
- `amount` - Transaction amount
- `currency` - Currency code
- `transaction_type` - Type (send_money, receive_money, airtime, etc.)
- `status` - Status (success, pending, failed, reversed)
- `balance_before/after` - Account balances
- `description` - Transaction description
- `reference` - Reference number
- `fee` - Transaction fee
- `created_at/updated_at` - Timestamps
- `processed_at` - ETL processing time

### Processing Logs Table
- `id` - Primary key
- `process_name` - ETL process name
- `status` - Execution status
- `records_processed/successful/failed` - Record counts
- `error_message` - Error details
- `started_at/completed_at` - Timing information
- `duration_seconds` - Execution duration
- `source_file` - Source XML file
- `dead_letter_count` - Failed record count

---

## Testing

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_parse_xml.py -v
```

### Run with coverage:
```bash
pytest --cov=etl --cov=api --cov-report=html
```

### Run specific test:
```bash
pytest tests/test_parse_xml.py::test_parse_valid_xml_file -v
```

---

## Key Features

### 1. XML Parsing
- Supports multiple XML timestamp formats
- Extracts SMS content and metadata
- Error handling with detailed logging

### 2. Data Cleaning
- Phone number normalization
- Transaction amount extraction
- SMS text parsing with regex patterns

### 3. Categorization
- 8 transaction categories
- Confidence scoring
- Support for custom categories
- Priority-based category matching

### 4. Database Management
- Automatic duplicate detection
- Transaction status tracking
- Processing logs for audit trail
- SQLite with future migration path

### 5. REST API
- Full CRUD operations
- Pagination and filtering
- Comprehensive analytics endpoints
- CORS enabled for cross-origin requests

### 6. Dashboard
- Real-time analytics visualization
- Interactive charts with Chart.js
- Transaction filtering and search
- Responsive design for mobile/tablet
- Live API status monitoring

---

## Configuration

### Environment Variables (.env)
```ini
# Application
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./momo_transactions.db
DATABASE_ECHO=false

# API
API_HOST=0.0.0.0
API_PORT=8000

# ETL
RAW_DATA_PATH=./data/raw
PROCESSED_DATA_PATH=./data/processed
LOG_PATH=./data/logs
DEAD_LETTER_PATH=./data/logs/dead_letter

# Processing
BATCH_SIZE=1000
CHUNK_SIZE=100

# Features
ENABLE_ETL_LOGGING=true
ENABLE_DEAD_LETTER_QUEUE=true
```

---

## Error Handling

### ETL Pipeline
- **Dead Letter Queue** - Failed records saved for manual review
- **Detailed Logging** - All processing steps logged
- **Batch Recovery** - Continues processing despite individual record failures

### API
- **HTTP Error Codes** - Standard REST error responses
- **Validation Errors** - Pydantic model validation
- **Database Errors** - Transaction rollback on failure

### Frontend
- **API Connection Monitoring** - Health check status
- **Error Messages** - User-friendly error notifications
- **Graceful Degradation** - Dashboard functions without data

---

## Performance Optimizations

1. **Batch Processing** - Processes records in configurable chunks
2. **Database Indexing** - Indexed fields for faster queries
3. **Pagination** - Efficient data retrieval with limit/offset
4. **Chart Caching** - Browser-side chart instance management
5. **Query Optimization** - Aggregation queries for analytics

---

## Next Steps for Phase 2

### Backend Enhancement
- [ ] Add authentication/authorization
- [ ] Implement data validation rules engine
- [ ] Add background task queue (Celery)
- [ ] Create data import webhooks
- [ ] Implement rate limiting

### Frontend Enhancement
- [ ] Add user authentication UI
- [ ] Implement advanced filtering
- [ ] Add data export formats (CSV, Excel)
- [ ] Create custom report builder
- [ ] Add real-time notifications

### Testing
- [ ] Integration tests for full pipeline
- [ ] API endpoint load testing
- [ ] Frontend E2E tests with Selenium/Playwright
- [ ] Database migration tests

### Deployment
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline setup
- [ ] Production database migration (PostgreSQL)
- [ ] Load balancing configuration

---

## Troubleshooting

### Database Connection Error
```
Error: database is locked
Solution: Ensure no other process is using the database. Close other connections.
```

### API Port Already in Use
```
Error: Address already in use
Solution: Change port in .env or use: lsof -i :8000 (kill process)
```

### XML Parsing Error
```
Error: Invalid XML
Solution: Validate XML file structure and encoding (UTF-8)
```

### Module Import Error
```
Error: ModuleNotFoundError
Solution: Ensure PYTHONPATH includes project root or activate virtual environment
```

---

## Contributing

Team members should follow this workflow:

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Run tests: `pytest`
4. Commit with clear messages: `git commit -m "Add feature: description"`
5. Push to repository: `git push origin feature/your-feature`
6. Create Pull Request for review
7. Merge to main after approval

---

## Team Members

- **Olivier Dusabamahoro** - Project Lead
- **Daniel Kenny Kamanzi** - Backend Development
- **Divin Manzi Mulinda Elvis** - Frontend Development

---

## License

This project is part of Team 8's coursework.

---

## Status

**Status:** Complete - Full Foundation Implementation  
**Next Phase:** Backend Enhancement & Advanced Features
