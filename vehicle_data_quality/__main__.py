import argparse
import csv
from datetime import date
import json
import math
from pathlib import Path
import shutil
import sqlite3
import time

from openpyxl import Workbook

from .database import ROOT, initialize
from .pipeline import COLUMNS, process_file, scan
from .report import export_queries, export_report


def emit(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


def make_xlsx(csv_file, destination):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Updates'
    with Path(csv_file).open(encoding='utf-8-sig', newline='') as source:
        records = csv.DictReader(source)
        sheet.append(list(COLUMNS))
        for row in records:
            sheet.append([row['offer_id'], row['vehicle_id'], row['product'], float(row['price_eur']),
                          int(row['term_months']), int(row['annual_mileage']), date.fromisoformat(row['updated_at'])])
    for cell in sheet['D'][1:]:
        cell.number_format = '0.00'
    for cell in sheet['G'][1:]:
        cell.number_format = 'yyyy-mm-dd'
    sheet.freeze_panes = 'A2'
    sheet.auto_filter.ref = sheet.dimensions
    workbook.save(destination)
    workbook.close()


def demo(output):
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Demo-Ziel ist nicht leer. Bitte ein neues Verzeichnis wählen.')
    output.mkdir(parents=True, exist_ok=True)
    database, inbox = output / 'vehicle_data_quality.sqlite', output / 'inbox'
    inbox.mkdir(exist_ok=True)
    initialize(database)
    for name in ('01_invalid_updates.csv', '02_valid_updates.csv'):
        shutil.copyfile(ROOT / 'data' / name, inbox / name)
    results = scan(database, inbox)
    make_xlsx(inbox / '02_valid_updates.csv', inbox / '03_valid_updates.xlsx')
    results.append(process_file(database, inbox / '03_valid_updates.xlsx'))
    results.append(process_file(database, inbox / '02_valid_updates.csv'))
    export_report(database, output / 'report.xlsx')
    export_queries(database, output / 'sql-results')
    (output / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'results': results, 'report': str(output / 'report.xlsx')}


def main():
    parser = argparse.ArgumentParser(description='Vehicle Data Quality Lab: synthetische Daten prüfen, aktualisieren und auswerten.')
    parser.add_argument('--db', default='state/vehicle_data_quality.sqlite')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('init')
    importing = commands.add_parser('import')
    importing.add_argument('file')
    for name in ('scan', 'watch'):
        command = commands.add_parser(name)
        command.add_argument('inbox')
        if name == 'watch':
            command.add_argument('--interval', type=float, default=5)
    report = commands.add_parser('report')
    report.add_argument('--output', default='reports/report.xlsx')
    query = commands.add_parser('queries')
    query.add_argument('--output', default='reports/sql-results')
    example = commands.add_parser('demo')
    example.add_argument('--output', default='demo-output')
    args = parser.parse_args()
    try:
        if args.command == 'demo':
            emit(demo(args.output))
        elif args.command == 'init':
            initialize(args.db)
            emit({'database': args.db, 'status': 'initialized'})
        elif args.command == 'import':
            result = process_file(args.db, args.file)
            emit(result)
            return 2 if result['status'] == 'rejected' or result.get('previous_status') == 'rejected' else 0
        elif args.command in ('scan', 'watch'):
            if args.command == 'watch' and (not math.isfinite(args.interval) or args.interval <= 0):
                raise ValueError('Intervall muss endlich und positiv sein.')
            while True:
                for result in scan(args.db, args.inbox):
                    if result['status'] != 'skipped':
                        emit(result)
                if args.command == 'scan':
                    break
                time.sleep(args.interval)
        elif args.command == 'report':
            emit({'report': str(export_report(args.db, args.output))})
        elif args.command == 'queries':
            export_queries(args.db, args.output)
            emit({'directory': args.output})
    except KeyboardInterrupt:
        return 0
    except (ValueError, OSError, sqlite3.Error) as error:
        emit({'status': 'error', 'message': str(error)})
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
