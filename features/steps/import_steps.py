import csv

from behave import given, when, then

from vehicle_data_quality.__main__ import make_xlsx
from vehicle_data_quality.database import connect
from vehicle_data_quality.pipeline import COLUMNS, process_file


@given('eine Datei mit folgenden Angebotsdaten')
def offer_file(context):
    defaults = dict(zip(COLUMNS, ['TEST01', 'V001', 'Leasing', '123.45', '36', '10000', '2026-10-01']))
    context.file = context.directory / 'updates.csv'
    with context.file.open('w', encoding='utf-8', newline='') as destination:
        writer = csv.DictWriter(destination, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows({**defaults, **row.as_dict()} for row in context.table)


@given('die Datei liegt als XLSX vor')
def xlsx_file(context):
    destination = context.file.with_suffix('.xlsx')
    make_xlsx(context.file, destination)
    context.file = destination


@when('ich die Datei importiere')
def import_file(context):
    context.result = process_file(context.database, context.file)


@then('lautet der Importstatus "{status}"')
def import_status(context, status):
    assert context.result['status'] == status, context.result


@then('beträgt die Anzahl neuer Angebote mit Änderungshistorie {count:d}')
def inserted_offers(context, count):
    assert context.result['inserted'] == count, context.result
    with connect(context.database) as db:
        assert db.execute('SELECT COUNT(*) FROM offers').fetchone()[0] == len(context.before) + count
        assert db.execute('SELECT COUNT(*) FROM changes').fetchone()[0] == count


@then('bleiben Bestand und Änderungshistorie unverändert')
def unchanged_database(context):
    with connect(context.database) as db:
        actual = [dict(row) for row in db.execute('SELECT * FROM offers ORDER BY offer_id')]
        assert actual == context.before
        assert db.execute('SELECT COUNT(*) FROM changes').fetchone()[0] == 0


@then('wird der Fehler "{code}" für Zeile {number:d} protokolliert')
def recorded_issue(context, code, number):
    with connect(context.database) as db:
        issues = {(row['code'], row['row_number']) for row in db.execute(
            'SELECT code, row_number FROM issues WHERE batch_id=?', (context.result['batch_id'],))}
    assert (code, number) in issues, issues


@then('ist die Rate von "{offer_id}" genau {cents:d} Cent')
def stored_price(context, offer_id, cents):
    with connect(context.database) as db:
        actual = db.execute('SELECT price_cents FROM offers WHERE offer_id=?', (offer_id,)).fetchone()
    assert actual is not None and actual[0] == cents, actual


@then('beträgt die Anzahl protokollierter Imports {count:d}')
def batch_count(context, count):
    with connect(context.database) as db:
        assert db.execute('SELECT COUNT(*) FROM batches').fetchone()[0] == count


@then('beträgt die Anzahl protokollierter Änderungen {count:d}')
def change_count(context, count):
    with connect(context.database) as db:
        assert db.execute('SELECT COUNT(*) FROM changes').fetchone()[0] == count
