from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from vehicle_data_quality.database import connect, initialize
from vehicle_data_quality.pipeline import COLUMNS


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.database = self.directory / 'test.sqlite'
        initialize(self.database)

    def rows(self, sql):
        with connect(self.database) as db:
            return [dict(row) for row in db.execute(sql)]

    def record(self, **overrides):
        defaults = dict(zip(COLUMNS, ['TEST01', 'V001', 'Leasing', '123.45', '36', '10000', '2026-10-01']))
        return {**defaults, **overrides}
