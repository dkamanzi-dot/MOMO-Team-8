#!/bin/bash
# Run ETL pipeline

set -e

echo "Starting MoMo ETL Pipeline..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Create data directories if they don't exist
mkdir -p data/raw data/processed data/logs data/logs/dead_letter

# Check if input file/directory is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <input_file_or_directory>"
    echo "Example: $0 data/raw/transactions.xml"
    echo "Example: $0 data/raw/"
    exit 1
fi

INPUT_PATH="$1"

# Verify input exists
if [ ! -e "$INPUT_PATH" ]; then
    echo "Error: Input path does not exist: $INPUT_PATH"
    exit 1
fi

# Run ETL pipeline
echo "Processing: $INPUT_PATH"
python -m etl.run "$INPUT_PATH"

echo "ETL Pipeline completed successfully!"
