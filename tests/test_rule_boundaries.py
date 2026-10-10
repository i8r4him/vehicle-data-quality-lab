from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from vehicle_data_quality.database import connect, initialize
from vehicle_data_quality.pipeline import COLUMNS, validate


class RuleBoundaryTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.database = Path(temporary.name) / 'rules.sqlite'
        initialize(self.database)

    def check_value(self, field, value, accepted, expected=None):
        record = dict(zip(COLUMNS, ['TEST01', 'V001', 'Leasing', '123.45', '36', '10000', '2026-10-01']))
        record[field] = value
        with connect(self.database) as db:
            candidates, issues = validate([record], db)
        if accepted:
            self.assertEqual(issues, [])
            self.assertEqual(len(candidates), 1)
            if expected is not None:
                stored_field = 'price_cents' if field == 'price_eur' else field
                self.assertEqual(candidates[0][stored_field], expected)
        else:
            self.assertEqual(candidates, [])
            self.assertEqual([issue[1] for issue in issues], ['VALUE'])

    def test_price_boundaries_and_cent_precision(self):
        cases = [('0', False, None), ('0.001', False, None), ('0.01', True, 1),
                 ('10000000', True, 1000000000), ('10000000.01', False, None)]
        for value, accepted, cents in cases:
            with self.subTest(price=value):
                self.check_value('price_eur', value, accepted, cents)

    def test_term_boundaries(self):
        for value, accepted in [('0', False), ('1', True), ('120', True), ('121', False),
                                ('1.5', False), ('NaN', False), ('Infinity', False)]:
            with self.subTest(term=value):
                self.check_value('term_months', value, accepted, int(value) if accepted else None)

    def test_mileage_boundaries(self):
        for value, accepted in [('0', False), ('1', True), ('200000', True), ('200001', False),
                                ('1.5', False), ('NaN', False), ('Infinity', False)]:
            with self.subTest(mileage=value):
                self.check_value('annual_mileage', value, accepted, int(value) if accepted else None)

    def test_offer_id_boundaries(self):
        for value, accepted in [('A', True), ('A' * 40, True), ('A' * 41, False),
                                ('abc', False), ('A B', False), ('A_-9', True)]:
            with self.subTest(offer_id=value):
                self.check_value('offer_id', value, accepted, value if accepted else None)

    def test_product_values(self):
        for value, accepted in [('Leasing', True), ('Finanzierung', True), ('Kredit', False)]:
            with self.subTest(product=value):
                self.check_value('product', value, accepted, value if accepted else None)

    def test_update_date_regression(self):
        # Gleiche Daten bleiben erlaubt; eine echte Änderung braucht ein neueres Datum.
        for price, day, accepted in [('299.00', '2026-09-01', True),
                                     ('349.00', '2026-08-31', False),
                                     ('349.00', '2026-09-01', False),
                                     ('349.00', '2026-09-02', True)]:
            with self.subTest(price=price, date=day):
                record = dict(zip(COLUMNS, ['OFF001', 'V001', 'Leasing', price, '36', '10000', day]))
                with connect(self.database) as db:
                    candidates, issues = validate([record], db)
                self.assertEqual(bool(candidates), accepted)
                self.assertEqual([issue[1] for issue in issues], [] if accepted else ['STALE_UPDATE'])
