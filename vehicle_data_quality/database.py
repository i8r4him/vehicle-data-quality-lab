from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parent.parent


@contextmanager
def connect(path):
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.executescript((ROOT / 'vehicle_data_quality' / 'schema.sql').read_text(encoding='utf-8'))
        db.executemany('INSERT OR IGNORE INTO brands VALUES (?, ?)', [
            ('B01', 'Nordlicht'), ('B02', 'Rheinmotor'), ('B03', 'Elbwerk'),
        ])
        db.executemany('INSERT OR IGNORE INTO vehicles VALUES (?, ?, ?)', [
            ('V001', 'B01', 'City E'), ('V002', 'B01', 'Touring'),
            ('V003', 'B02', 'Urban'), ('V004', 'B03', 'Family'),
        ])
        db.executemany('INSERT OR IGNORE INTO offers VALUES (?, ?, ?, ?, ?, ?, ?)', [
            ('OFF001', 'V001', 'Leasing', 29900, 36, 10000, '2026-09-01'),
            ('OFF002', 'V002', 'Finanzierung', 39900, 48, 15000, '2026-09-01'),
            ('OFF003', 'V003', 'Leasing', 24900, 24, 10000, '2026-09-01'),
            ('OFF004', 'V004', 'Finanzierung', 45900, 60, 20000, '2026-09-01'),
        ])
        # Deliberately constructed examples, not measured performance data.
        records = []
        for phase, durations in [('manuell', [24, 36, 48]), ('automatisiert', [8, 12, 16])]:
            for index, category in enumerate(['Datenpflege', 'Produktupdate', 'Fehlerklärung']):
                for repeat in range(2):
                    created = datetime(2026, 9 if phase == 'manuell' else 10, 1 + repeat, tzinfo=timezone.utc)
                    resolved = created + timedelta(hours=durations[index] + repeat * 2)
                    records.append((len(records) + 1, category, phase, created.isoformat(), resolved.isoformat()))
        db.executemany('INSERT OR IGNORE INTO service_requests VALUES (?, ?, ?, ?, ?)', records)


def queries(db):
    result = {}
    for path in sorted((ROOT / 'sql').glob('*.sql')):
        cursor = db.execute(path.read_text(encoding='utf-8'))
        result[path.stem] = ([column[0] for column in cursor.description], [list(row) for row in cursor])
    return result
