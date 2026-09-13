# MoMo SMS Database ERD

This diagram is rendered by GitHub from Mermaid syntax. It is maintained beside the
SQL implementation so the visual design and the database structure stay consistent.

```mermaid
erDiagram
    USERS ||--o{ TRANSACTIONS : sends
    USERS ||--o{ TRANSACTIONS : receives
    TRANSACTIONS ||--o{ TRANSACTION_CATEGORIES : has
    TRANSACTION_CATEGORIES_LOOKUP ||--o{ TRANSACTION_CATEGORIES : classifies

    USERS {
        INTEGER user_id PK
        TEXT phone_number UK
        TEXT full_name
        TEXT user_role
        INTEGER is_active
        TEXT created_at
        TEXT updated_at
    }

    TRANSACTIONS {
        INTEGER transaction_id PK
        TEXT external_reference UK
        INTEGER sender_user_id FK
        INTEGER recipient_user_id FK
        TEXT transaction_timestamp
        NUMERIC amount
        TEXT currency
        NUMERIC fee
        TEXT status
        TEXT original_sms
        NUMERIC balance_before
        NUMERIC balance_after
        TEXT created_at
        TEXT updated_at
    }

    TRANSACTION_CATEGORIES_LOOKUP {
        INTEGER category_id PK
        TEXT category_code UK
        TEXT category_name UK
        TEXT description
        INTEGER is_active
    }

    TRANSACTION_CATEGORIES {
        INTEGER transaction_id PK, FK
        INTEGER category_id PK, FK
        TEXT assigned_at
    }

    SYSTEM_LOGS {
        INTEGER log_id PK
        TEXT process_name
        TEXT log_level
        TEXT status
        INTEGER records_processed
        INTEGER records_successful
        INTEGER records_failed
        TEXT source_file
        TEXT error_message
        TEXT started_at
        TEXT completed_at
    }
```

## Relationship Notes

- One user can send many transactions.
- One user can receive many transactions.
- One transaction can have many category assignments.
- One category can classify many transactions.
- `transaction_categories` resolves the many-to-many relationship between transactions
  and categories.
- `system_logs` records ETL activity independently of transaction records.

## Source

The authoritative implementation is [database/database_setup.sql](../database/database_setup.sql).