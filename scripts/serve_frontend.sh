#!/bin/bash
# Start FastAPI server

set -e

echo "Starting MoMo Analytics API..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Create data directories if they don't exist
mkdir -p data/raw data/processed data/logs data/logs/dead_letter

# Get host and port from arguments or use defaults
HOST="${1:-0.0.0.0}"
PORT="${2:-8000}"

echo "Starting API server on $HOST:$PORT"

# Start FastAPI server with auto-reload
python -m uvicorn api.app:app --host "$HOST" --port "$PORT" --reload

