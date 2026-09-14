-- =====================================================================
-- MoMo SMS Database - MySQL translation of teammate's design
-- Matches the pushed PostgreSQL schema and ERD diagram, converted to
-- valid MySQL 8.0+ syntax (AUTO_INCREMENT, DATETIME, DECIMAL, ENUM,
-- ON UPDATE CURRENT_TIMESTAMP instead of plpgsql triggers).
-- =====================================================================

DROP DATABASE IF EXISTS momo_sms_db_v2;
CREATE DATABASE momo_sms_db_v2;
USE momo_sms_db_v2;

-- =====================================================================
-- TABLE: users
-- =====================================================================
CREATE TABLE users (
    user_id         INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique internal identifier',
    phone_number    VARCHAR(15) NOT NULL UNIQUE COMMENT 'Phone number, 10-15 characters',
    full_name       VARCHAR(100) NOT NULL COMMENT 'Full name of the user',
    user_role       ENUM('customer', 'merchant', 'agent', 'system') NOT NULL DEFAULT 'customer' COMMENT 'Role of this party',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Whether this user account is active',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Row creation time',
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Auto-updates on every row change',
    CONSTRAINT chk_phone_length CHECK (CHAR_LENGTH(phone_number) BETWEEN 10 AND 15),
    CONSTRAINT chk_name_not_blank CHECK (CHAR_LENGTH(TRIM(full_name)) > 0)
) COMMENT = 'Senders and recipients of MoMo transactions';

-- =====================================================================
-- TABLE: transaction_categories_lookup
-- =====================================================================
CREATE TABLE transaction_categories_lookup (
    category_id     INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique identifier for a category',
    category_code   VARCHAR(20) NOT NULL UNIQUE COMMENT 'Machine code, e.g. P2P, AIRTIME, BILL',
    category_name   VARCHAR(50) NOT NULL UNIQUE COMMENT 'Human-readable category name',
    description     VARCHAR(255) DEFAULT NULL COMMENT 'What this category covers',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Whether this category is currently in use'
) COMMENT = 'Lookup table of MoMo transaction types';

-- =====================================================================
-- TABLE: transactions
-- =====================================================================
CREATE TABLE transactions (
    transaction_id          INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique internal transaction ID',
    external_reference      VARCHAR(50) NOT NULL UNIQUE COMMENT 'MoMo-issued transaction reference',
    sender_user_id           INT DEFAULT NULL COMMENT 'FK to users, who sent the money, NULL if not applicable',
    recipient_user_id        INT DEFAULT NULL COMMENT 'FK to users, who received the money, NULL if not applicable',
    transaction_timestamp    DATETIME NOT NULL COMMENT 'When the transaction occurred',
    amount                    DECIMAL(15,2) NOT NULL COMMENT 'Transaction amount',
    currency                  CHAR(3) NOT NULL DEFAULT 'RWF' COMMENT 'ISO currency code',
    fee                        DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT 'Fee charged',
    status                     ENUM('pending', 'success', 'failed', 'reversed') NOT NULL DEFAULT 'success' COMMENT 'Transaction outcome status',
    original_sms                TEXT NOT NULL COMMENT 'Raw SMS text this transaction was parsed from',
    balance_before                DECIMAL(15,2) DEFAULT NULL COMMENT 'Balance before the transaction',
    balance_after                  DECIMAL(15,2) DEFAULT NULL COMMENT 'Balance after the transaction',
    created_at                       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_txn_sender FOREIGN KEY (sender_user_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_txn_recipient FOREIGN KEY (recipient_user_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    CONSTRAINT chk_amount_nonneg CHECK (amount >= 0),
    CONSTRAINT chk_fee_nonneg CHECK (fee >= 0),
    CONSTRAINT chk_currency_len CHECK (CHAR_LENGTH(currency) = 3),
    CONSTRAINT chk_balance_before_nonneg CHECK (balance_before IS NULL OR balance_before >= 0),
    CONSTRAINT chk_balance_after_nonneg CHECK (balance_after IS NULL OR balance_after >= 0),
    CONSTRAINT chk_sender_ne_recipient CHECK (sender_user_id IS NULL OR recipient_user_id IS NULL OR sender_user_id <> recipient_user_id)
) COMMENT = 'Core table of all parsed MoMo transactions';

-- =====================================================================
-- JUNCTION TABLE: transaction_categories
-- Resolves M:N between transactions and categories. A transaction can
-- carry multiple categories, a category can classify many transactions.
-- =====================================================================
CREATE TABLE transaction_categories (
    transaction_id  INT NOT NULL COMMENT 'FK to transactions',
    category_id     INT NOT NULL COMMENT 'FK to transaction_categories_lookup',
    assigned_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When this category was assigned',
    PRIMARY KEY (transaction_id, category_id),
    CONSTRAINT fk_tc_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    CONSTRAINT fk_tc_category FOREIGN KEY (category_id) REFERENCES transaction_categories_lookup(category_id) ON DELETE RESTRICT
) COMMENT = 'Junction table resolving many-to-many between transactions and categories';

-- =====================================================================
-- TABLE: system_logs
-- Batch/pipeline-run level logging, independent of individual transactions.
-- =====================================================================
CREATE TABLE system_logs (
    log_id                  INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique log entry ID',
    process_name            VARCHAR(50) NOT NULL COMMENT 'Pipeline stage, e.g. xml_import, normalization, categorization',
    log_level                ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL DEFAULT 'INFO',
    status                    ENUM('started', 'success', 'partial_failure', 'failed') NOT NULL,
    records_processed         INT NOT NULL DEFAULT 0,
    records_successful         INT NOT NULL DEFAULT 0,
    records_failed               INT NOT NULL DEFAULT 0,
    source_file                    VARCHAR(255) DEFAULT NULL,
    error_message                    VARCHAR(255) DEFAULT NULL,
    started_at                          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at                          DATETIME DEFAULT NULL,
    CONSTRAINT chk_records_processed CHECK (records_processed >= 0),
    CONSTRAINT chk_records_successful CHECK (records_successful >= 0),
    CONSTRAINT chk_records_failed CHECK (records_failed >= 0),
    CONSTRAINT chk_records_total CHECK (records_successful + records_failed <= records_processed)
) COMMENT = 'Pipeline/batch-run audit log, independent of individual transactions';

-- =====================================================================
-- INDEXES
-- =====================================================================
CREATE INDEX idx_transactions_timestamp ON transactions(transaction_timestamp);
CREATE INDEX idx_transactions_sender ON transactions(sender_user_id);
CREATE INDEX idx_transactions_recipient ON transactions(recipient_user_id);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transaction_categories_category ON transaction_categories(category_id);
CREATE INDEX idx_system_logs_process_status ON system_logs(process_name, status);

-- =====================================================================
-- SAMPLE DATA (5 records per main table, matching teammate's seed data)
-- =====================================================================

INSERT INTO users (user_id, phone_number, full_name, user_role) VALUES
(1, '0781000001', 'Aline Uwase', 'customer'),
(2, '0781000002', 'Brian Niyonsenga', 'customer'),
(3, '0781000003', 'Chantal Mukamana', 'customer'),
(4, '0781000004', 'Kigali Market', 'merchant'),
(5, '0781000005', 'MoMo Agent 05', 'agent');

INSERT INTO transaction_categories_lookup (category_id, category_code, category_name, description) VALUES
(1, 'P2P', 'Person to Person', 'Transfer between individual customers'),
(2, 'AIRTIME', 'Airtime', 'Mobile airtime purchase'),
(3, 'BILL', 'Bill Payment', 'Payment to a biller or service provider'),
(4, 'CASH_IN', 'Cash In', 'Cash deposited through an agent'),
(5, 'MERCHANT', 'Merchant Payment', 'Payment to a registered merchant');

INSERT INTO transactions
    (transaction_id, external_reference, sender_user_id, recipient_user_id,
     transaction_timestamp, amount, currency, fee, status, original_sms,
     balance_before, balance_after) VALUES
(1, 'TXN-20260901-0001', 1, 2, '2026-09-01 08:15:00', 15000, 'RWF', 100, 'success', 'You sent 15,000 RWF to Brian.', 50000, 34900),
(2, 'TXN-20260901-0002', 2, 4, '2026-09-01 09:30:00', 8500, 'RWF', 0, 'success', 'Payment of 8,500 RWF to Kigali Market.', 40000, 31500),
(3, 'TXN-20260902-0001', 3, NULL, '2026-09-02 10:00:00', 2000, 'RWF', 0, 'success', 'Airtime purchase of 2,000 RWF.', 10000, 8000),
(4, 'TXN-20260902-0002', 5, 1, '2026-09-02 12:45:00', 30000, 'RWF', 200, 'pending', 'Cash deposit of 30,000 RWF.', 100000, 69800),
(5, 'TXN-20260903-0001', 1, NULL, '2026-09-03 14:20:00', 5000, 'RWF', 50, 'reversed', 'Reversed bill payment of 5,000 RWF.', 34900, 34900);

INSERT INTO transaction_categories (transaction_id, category_id) VALUES
(1, 1), (2, 5), (3, 2), (4, 4), (5, 3), (5, 1);

INSERT INTO system_logs
    (log_id, process_name, log_level, status, records_processed, records_successful, records_failed, source_file) VALUES
(1, 'xml_import', 'INFO', 'started', 0, 0, 0, 'momo_week2.xml'),
(2, 'xml_import', 'INFO', 'success', 5, 5, 0, 'momo_week2.xml'),
(3, 'normalization', 'INFO', 'success', 5, 5, 0, 'momo_week2.xml'),
(4, 'categorization', 'WARNING', 'partial_failure', 5, 4, 1, 'momo_week2.xml'),
(5, 'json_export', 'INFO', 'success', 5, 5, 0, 'transactions.json');

-- =====================================================================
-- SAMPLE CRUD OPERATIONS (for testing / documentation screenshots)
-- =====================================================================
 
-- READ: transactions with sender, recipient, and all assigned categories
SELECT t.external_reference, s.full_name AS sender, r.full_name AS recipient,
       t.amount, GROUP_CONCAT(c.category_name SEPARATOR ', ') AS categories
FROM transactions t
LEFT JOIN users s ON s.user_id = t.sender_user_id
LEFT JOIN users r ON r.user_id = t.recipient_user_id
JOIN transaction_categories tc ON tc.transaction_id = t.transaction_id
JOIN transaction_categories_lookup c ON c.category_id = tc.category_id
GROUP BY t.transaction_id
ORDER BY t.transaction_timestamp;

-- UPDATE: mark a pending transaction as successful
UPDATE transactions SET status = 'success' WHERE transaction_id = 4;

-- DELETE: remove one category assignment from a multi-category transaction
DELETE FROM transaction_categories WHERE transaction_id = 5 AND category_id = 1;

-- CREATE: log a new pipeline run
INSERT INTO system_logs (process_name, log_level, status, records_processed, records_successful, records_failed, source_file)
VALUES ('validation', 'INFO', 'success', 5, 5, 0, 'momo_week2.xml');

SELECT * FROM transactions;