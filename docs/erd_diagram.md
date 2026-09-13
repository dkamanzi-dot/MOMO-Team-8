# MoMo SMS Database ERD

GitHub renders this Mermaid ERD directly. It shows the SQL database design.

```mermaid
erDiagram
    USERS ||--o{ TRANSACTIONS : sends
    USERS ||--o{ TRANSACTIONS : receives
    TRANSACTIONS ||--o{ TRANSACTION_CATEGORIES : has
    TRANSACTION_CATEGORIES_LOOKUP ||--o{ TRANSACTION_CATEGORIES : classifies

    USERS {
        INTEGER user_id PK "identity"
        TEXT phone_number UK
        TEXT full_name
        TEXT user_role
        BOOLEAN is_active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    TRANSACTIONS {
        INTEGER transaction_id PK "identity"
        TEXT external_reference UK
        INTEGER sender_user_id FK
        INTEGER recipient_user_id FK
        TIMESTAMP transaction_timestamp
        NUMERIC amount
        TEXT currency
        NUMERIC fee
        TEXT status
        TEXT original_sms
        NUMERIC balance_before
        NUMERIC balance_after
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    TRANSACTION_CATEGORIES_LOOKUP {
        INTEGER category_id PK "identity"
        TEXT category_code UK
        TEXT category_name UK
        TEXT description
        BOOLEAN is_active
    }

    TRANSACTION_CATEGORIES {
        INTEGER transaction_id PK FK
        INTEGER category_id PK FK
        TIMESTAMP assigned_at
    }

    SYSTEM_LOGS {
        INTEGER log_id PK "identity"
        TEXT process_name
        TEXT log_level
        TEXT status
        INTEGER records_processed
        INTEGER records_successful
        INTEGER records_failed
        TEXT source_file
        TEXT error_message
        TIMESTAMP started_at
        TIMESTAMP completed_at
    }
```

## Relationship Summary

Users send and receive transactions. Transactions and categories have a many-to-many
relationship resolved by `transaction_categories`. `system_logs` stores ETL activity.

## Source

The authoritative implementation is [database/database_setup.sql](../database/database_setup.sql).