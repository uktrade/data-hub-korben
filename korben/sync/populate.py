'Parse database rows from XML, throw into database'
import multiprocessing
import os
import time
import sqlalchemy as sqla
from .resp_csv import main as load_table

def main(cache_dir):
    pool = multiprocessing.Pool()
    engine = sqla.create_engine('postgresql://localhost/cdms_psql')
    metadata = sqla.MetaData(bind=engine)
    metadata.reflect()
    results = []
    complete = 0
    for entity_name in os.listdir(cache_dir):
        results.append(pool.apply_async(load_table, (metadata, cache_dir, entity_name)))
    while complete != len(results):  # wait for completion
        for result in results:
            if not result.ready():
                continue
            complete += 1
            tempfiles, returncode = result.get()
            if returncode > 0:
                print("COPY command for {0} failed".format(entity_name))
            for tempfile in tempfiles:
                try:
                    os.unlink(tempfile)
                except FileNotFoundError:
                    pass
        time.sleep(1)  # don’t spam
