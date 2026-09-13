# MoMo Transaction Analytics System

## Team 8

### Team Members

1. **Olivier Dusabamahoro**
2. **Daniel Kenny Kamanzi**
3. **Divin Manzi Mulinda Elvis**

---

## Project Description

The **MoMo Transaction Analytics System** is an enterprise-level full-stack application designed to process Mobile Money (MoMo) SMS data stored in XML format.

The system will extract transaction information from XML data, clean and normalize the information, categorize transactions based on their types, store the processed data in a relational database, and provide a web-based dashboard for analyzing and visualizing the transaction data.

The project aims to transform raw MoMo SMS data into structured and meaningful information that can be used to understand transaction patterns, amounts, transaction types, and other relevant financial insights.

### Main Objectives

* Parse MoMo SMS data from XML format.
* Clean and normalize transaction data.
* Categorize transactions according to their types.
* Store structured transaction data in a relational database.
* Generate useful transaction analytics.
* Provide a web dashboard for data visualization.
* Follow a collaborative Agile development workflow.

---

## System Architecture

The planned system follows an ETL-based architecture:

```text
MoMo XML Data
      │
      ▼
┌──────────────────┐
│    XML Parser    │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│ Cleaning & Normalization │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Transaction Categorizing │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────┐
│ SQL Database     │
└────────┬─────────┘
         │
    ┌────┴─────┐
    ▼          ▼
┌─────────┐ ┌──────────────┐
│ FastAPI │ │ Dashboard    │
│   API   │ │ JSON Data    │
└────┬────┘ └──────┬───────┘
     │             │
     └──────┬──────┘
            ▼
   ┌──────────────────┐
   │  Web Dashboard   │
   │ Charts & Tables  │
   └──────────────────┘
```

### Architecture Diagram

The detailed architecture diagram is available in:

[docs/architecture.svg](docs/architecture.svg)

The database ERD is available as a GitHub-rendered diagram in
[docs/erd_diagram.md](docs/erd_diagram.md). It is generated from Mermaid source and
matches [database/database_setup.sql](database/database_setup.sql).
The image version required for submission is [docs/erd_diagram.png](docs/erd_diagram.png).

## Week 2 Database Design

The standalone SQL implementation is available in `database/database_setup.sql`.
It creates the following entities:

| Table | Purpose | Primary key | Important foreign keys |
| --- | --- | --- | --- |
| `users` | Customers, merchants, and agents involved in transactions | `user_id` | None |
| `transactions` | Amount, parties, status, balances, and original SMS | `transaction_id` | `sender_user_id`, `recipient_user_id` -> `users.user_id` |
| `transaction_categories_lookup` | Controlled vocabulary for payment types | `category_id` | None |
| `transaction_categories` | Resolves the transaction/category M:N relationship | (`transaction_id`, `category_id`) | Both parent tables |
| `system_logs` | ETL and export processing history | `log_id` | None |

### Design Rationale

The schema separates people, transaction facts, category definitions, and processing
history so each concept has one clear owner. A transaction stores sender and recipient
as foreign keys instead of repeating phone numbers and names; this preserves
referential integrity and allows a customer record to participate in many transactions.
The category lookup table keeps payment types consistent and makes it possible to add a
new category without changing the transaction table. A transaction may need more than
one classification, while each category applies to many transactions, so
`transaction_categories` resolves that many-to-many relationship with a composite key
that also prevents duplicate assignments. `system_logs` is independent of business
records because one ETL run can process many transactions and can fail before any
transaction is written. `CHECK` constraints protect amounts, fees, statuses, roles,
record counts, and currency values; unique constraints prevent duplicate phone numbers
and external references. Foreign keys use restrictive deletes for users and categories
to prevent accidental loss of historical meaning, while junction rows cascade when a
transaction is removed. Indexes support timestamp, party, status, category, and ETL
monitoring queries. Timestamps are stored in a standard database timestamp format and
are straightforward to serialize through the API. Seed data and commented CRUD queries
are included in the setup script for repeatable demonstrations and screenshots.

The normalized relational model is serialized into nested JSON in
`examples/json_schemas.json`: sender and recipient foreign keys become user objects,
and junction rows become the transaction's `categories` array.

### Example Database Queries

```sql
-- Read transactions with their parties and all categories
SELECT t.external_reference, s.full_name AS sender, r.full_name AS recipient,
    t.amount, STRING_AGG(c.category_name, ', ') AS categories
FROM transactions AS t
LEFT JOIN users AS s ON s.user_id = t.sender_user_id
LEFT JOIN users AS r ON r.user_id = t.recipient_user_id
JOIN transaction_categories AS tc ON tc.transaction_id = t.transaction_id
JOIN transaction_categories_lookup AS c ON c.category_id = tc.category_id
GROUP BY t.transaction_id;

-- Update a pending transaction after confirmation
UPDATE transactions SET status = 'success' WHERE transaction_id = 4;

-- Remove one classification without deleting the transaction
DELETE FROM transaction_categories
WHERE transaction_id = 5 AND category_id = 1;
```

The schema's accuracy and security rules include foreign-key enforcement, unique
identifiers, domain checks, non-negative monetary values, controlled status/role values,
and prevention of self-transfers. Foreign keys are enabled in the database schema.

---

## Scrum Board

Team 8 uses a Scrum board to organize project tasks and track progress.

**Scrum Board:**(https://github.com/users/dkamanzi-dot/projects/1)

The board contains the following columns:

* **To Do**
* **In Progress**
* **Done**

---

## Planned Technology Stack

### Backend

* Python
* ElementTree / lxml
* FastAPI

### Database

* SQL database

### Frontend

* HTML
* CSS
* JavaScript
* JavaScript charting library

### Testing

* pytest

### Development Tools

* Git
* GitHub
* Draw.io
* GitHub Projects / Trello / Jira

---

## Project Structure

```text
.
├── README.md
├── .env.example
├── requirements.txt
├── index.html
│
├── web/
│   ├── styles.css
│   ├── chart_handler.js
│   └── assets/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── logs/
│       ├── etl.log
│       └── dead_letter/
│
├── etl/
│   ├── __init__.py
│   ├── config.py
│   ├── parse_xml.py
│   ├── clean_normalize.py
│   ├── categorize.py
│   ├── load_db.py
│   └── run.py
│
├── api/
│   ├── __init__.py
│   ├── app.py
│   ├── db.py
│   └── schemas.py
│
├── scripts/
│   ├── run_etl.sh
│   ├── export_json.sh
│   └── serve_frontend.sh
│
├── tests/
│   ├── test_parse_xml.py
│   ├── test_clean_normalize.py
│   └── test_categorize.py
│
└── docs/
    └── architecture.png
```

---

## Development Workflow

Team 8 will use GitHub for collaborative development.

Each team member will work on assigned tasks using Git branches. Completed work will be reviewed and merged into the main branch.

The Scrum board will be used to track the progress of tasks from **To Do** to **In Progress** and finally to **Done**.


## Team Goal

Team 8 aims to develop a reliable and user-friendly MoMo Transaction Analytics System that transforms raw SMS transaction data into structured information and meaningful visual insights.