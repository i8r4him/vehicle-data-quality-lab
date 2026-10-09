PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS brands (
    id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS vehicles (
    id TEXT PRIMARY KEY, brand_id TEXT NOT NULL REFERENCES brands(id), model TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS offers (
    offer_id TEXT PRIMARY KEY,
    vehicle_id TEXT NOT NULL REFERENCES vehicles(id),
    product TEXT NOT NULL CHECK(product IN ('Leasing', 'Finanzierung')),
    price_cents INTEGER NOT NULL CHECK(price_cents > 0),
    term_months INTEGER NOT NULL CHECK(term_months BETWEEN 1 AND 120),
    annual_mileage INTEGER NOT NULL CHECK(annual_mileage BETWEEN 1 AND 200000),
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS batches (
    id INTEGER PRIMARY KEY, file_name TEXT NOT NULL, sha256 TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('accepted', 'rejected')),
    started_at TEXT NOT NULL, completed_at TEXT NOT NULL,
    rows_total INTEGER NOT NULL, rows_valid INTEGER NOT NULL,
    inserted INTEGER NOT NULL DEFAULT 0, updated INTEGER NOT NULL DEFAULT 0,
    unchanged INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS import_rows (
    batch_id INTEGER NOT NULL REFERENCES batches(id), row_number INTEGER NOT NULL,
    raw_json TEXT NOT NULL, PRIMARY KEY(batch_id, row_number)
);
CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY, batch_id INTEGER NOT NULL REFERENCES batches(id),
    row_number INTEGER NOT NULL, code TEXT NOT NULL, field TEXT NOT NULL, message TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS changes (
    id INTEGER PRIMARY KEY, batch_id INTEGER NOT NULL REFERENCES batches(id),
    offer_id TEXT NOT NULL, operation TEXT NOT NULL CHECK(operation IN ('insert', 'update')),
    old_json TEXT, new_json TEXT NOT NULL, changed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS service_requests (
    id INTEGER PRIMARY KEY, category TEXT NOT NULL,
    phase TEXT NOT NULL CHECK(phase IN ('manuell', 'automatisiert')),
    created_at TEXT NOT NULL, resolved_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS issues_batch ON issues(batch_id);
CREATE INDEX IF NOT EXISTS changes_offer ON changes(offer_id);
