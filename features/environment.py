from pathlib import Path
from tempfile import TemporaryDirectory

from vehicle_data_quality.database import connect, initialize


def before_scenario(context, scenario):
    temporary = TemporaryDirectory()
    context.add_cleanup(temporary.cleanup)
    context.directory = Path(temporary.name)
    context.database = context.directory / 'offers.sqlite'
    initialize(context.database)
    with connect(context.database) as db:
        context.before = [dict(row) for row in db.execute('SELECT * FROM offers ORDER BY offer_id')]
