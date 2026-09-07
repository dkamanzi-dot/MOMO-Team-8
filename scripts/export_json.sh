#!/bin/bash
# Export transaction data as JSON

set -e

echo "Exporting transaction data as JSON..."

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Get output file from arguments or use default
OUTPUT_FILE="${1:-data/processed/transactions_export.json}"

# Create output directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Export data using API endpoint
echo "Fetching data from database..."

python3 << 'EOF'
import json
from datetime import datetime
from api.db import SessionLocal
from api.models import Transaction

db = SessionLocal()

try:
    # Query all transactions
    transactions = db.query(Transaction).all()
    
    # Convert to JSON-serializable format
    data = {
        "export_date": datetime.utcnow().isoformat(),
        "total_records": len(transactions),
        "transactions": [
            {
                "id": t.id,
                "transaction_id": t.transaction_id,
                "timestamp": t.timestamp.isoformat(),
                "sender": t.sender,
                "recipient": t.recipient,
                "amount": t.amount,
                "currency": t.currency,
                "transaction_type": str(t.transaction_type),
                "status": str(t.status),
                "description": t.description,
                "fee": t.fee,
            }
            for t in transactions
        ]
    }
    
    # Write to file
    output_file = "$OUTPUT_FILE"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Exported {len(transactions)} transactions to {output_file}")

finally:
    db.close()
EOF

echo "Export completed successfully!"
