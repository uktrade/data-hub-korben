import os
import pickle
import sys


def main(entity_name, start, number=10):
    for page in map(str, range(start, start + (number * 50), 50)):
        fh = open(os.path.join('../cache/list', entity_name, page), 'rb')
        resp = pickle.load(fh)
        fh.close()
        print('===========================')
        print("{0} ({1})".format(entity_name, page))
        print('===========================')
        print(resp.content.decode(resp.encoding))

if __name__ == '__main__':
    entity_name = sys.argv[1]
    start = int(sys.argv[2])
    try:
        number = int(sys.argv[3])
        main(entity_name, start, number)
    except IndexError:
        main(entity_name, start)
