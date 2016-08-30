'Unpickle response objects in passed directory, output CSV for loading'
import os
import sys

import sqlalchemy as sqla

from resp_csv import main as load_table

if __name__ == '__main__':
    engine = sqla.create_engine('postgresql://localhost/cdms_psql')
    metadata = sqla.MetaData(bind=engine)
    metadata.reflect()

    cache_dir = sys.argv[1]
    results = []
    for entity_name in os.listdir(cache_dir):
        tempfiles, returncode = load_table(metadata, cache_dir, entity_name)
        if returncode > 0:
            print("COPY command for {0} failed".format(entity_name))
        for tempfile in tempfiles:
            os.unlink(tempfile.name)
        # results.append(load_table(metadata, cache_dir, entity_name))
    # for tempfiles, proc in results:
        # proc.wait()
        # for tempfile in tempfiles:
            # os.unlink(tempfile.name)
