-- Enable UUID extension (required for uuid_generate_v4())
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ──────────────────────────────────────────────────────────────
-- TABLE: payment_events
-- Raw payment failure data ingested from Razorpay webhooks
-- or synthetic test events.
-- ──────────────────────────────────────────────────────────────
CREATE TABLE payment_events (
    id                    UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    razorpay_payment_id   TEXT        NOT NULL,
    razorpay_order_id     TEXT,
    amount                INTEGER     NOT NULL,                -- in paise (₹1 = 100 paise)
    currency              TEXT        NOT NULL DEFAULT 'INR',
    failure_reason_code   TEXT,                               -- raw code, e.g. "BAD_REQUEST_ERROR"
    failure_description   TEXT,                               -- human-readable, e.g. "Payment timed out"
    customer_email        TEXT,
    customer_phone        TEXT,
    event_source          TEXT        NOT NULL,               -- 'live_webhook' | 'synthetic'
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────
-- TABLE: failure_classifications
-- Each payment_event gets classified into a category.
-- Filled by a rules engine first; later overrideable by the AI.
-- ──────────────────────────────────────────────────────────────
CREATE TABLE failure_classifications (
    id                UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_event_id  UUID        NOT NULL REFERENCES payment_events(id) ON DELETE CASCADE,
    category          TEXT        NOT NULL,  -- 'upi_timeout' | 'insufficient_funds' |
                                             -- 'card_auth_decline' | '3ds_drop' | 'bank_error'
    confidence        FLOAT,
    rationale         TEXT,                  -- AI explanation; null until AI block is wired up
    classified_by     TEXT        NOT NULL,  -- 'rules_engine' | 'ai_agent'
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────
-- TABLE: recovery_actions
-- The action decided for a given failure + classification pair.
-- ──────────────────────────────────────────────────────────────
CREATE TABLE recovery_actions (
    id                        UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_event_id          UUID        NOT NULL REFERENCES payment_events(id) ON DELETE CASCADE,
    classification_id         UUID        NOT NULL REFERENCES failure_classifications(id) ON DELETE CASCADE,
    action_type               TEXT        NOT NULL,  -- 'retry_now' | 'retry_delayed' |
                                                      -- 'suggest_alt_method' | 'no_action'
    action_delay_minutes      INTEGER,               -- only relevant for 'retry_delayed'
    executed                  BOOLEAN     NOT NULL DEFAULT FALSE,
    executed_at               TIMESTAMPTZ,
    razorpay_payment_link_id  TEXT,
    razorpay_payment_link_url TEXT,
    execution_error           TEXT,
    created_at                TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────
-- TABLE: outcomes
-- Did the recovery action succeed? Used for dashboard metrics.
-- ──────────────────────────────────────────────────────────────
CREATE TABLE outcomes (
    id                  UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    recovery_action_id  UUID        NOT NULL REFERENCES recovery_actions(id) ON DELETE CASCADE,
    recovered           BOOLEAN     NOT NULL DEFAULT FALSE,
    recovered_amount    INTEGER,               -- in paise; null if not recovered
    recovered_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────
-- Indexes for common query patterns
-- ──────────────────────────────────────────────────────────────
CREATE INDEX idx_payment_events_razorpay_payment_id
    ON payment_events(razorpay_payment_id);

CREATE INDEX idx_failure_classifications_payment_event_id
    ON failure_classifications(payment_event_id);

CREATE INDEX idx_recovery_actions_payment_event_id
    ON recovery_actions(payment_event_id);

CREATE INDEX idx_outcomes_recovery_action_id
    ON outcomes(recovery_action_id);
