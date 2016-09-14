import os
import pickle
from lxml import etree
from . import constants



def main(cache_dir, dry_run=False):
    for entity_name in constants.ENTITY_NAMES:
        pages = sorted(
            os.listdir(os.path.join(cache_dir, entity_name)),
            key=int,
            reverse=True,
        )
        empty = []
        for page in pages:
            path = os.path.join(cache_dir, entity_name, page)
            with open(path, 'rb') as fh:
                resp = pickle.load(fh)
            try:
                root = etree.fromstring(resp.content)
            except etree.XMLSyntaxError:
                print("Bad resp {0} {1}".format(entity_name, page))
                continue
            if not root.findall(constants.ENTRY_TAG):
                empty.append(path)
            else:
                break
        for path in empty:
            if dry_run:
                print(path)
            else:
                os.unlink(path)
                print("Removing `{0}`".format(path))
