import os
import pickle
import sys

from . import constants



def main(cache_dir, entity_name, start=0, number=10):
    for page in map(str, range(start, start + (number * 50), 50)):
        fh = open(os.path.join(cache_dir, entity_name, page), 'rb')
        resp = pickle.load(fh)
        fh.close()
        print('===========================')
        print("{0} ({1})".format(entity_name, page))
        print('===========================')
        print(resp.content.decode(resp.encoding))
