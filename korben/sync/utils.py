from logging.handlers import RotatingFileHandler
import logging
import multiprocessing
import os
import sys
import threading
import traceback

from lxml import etree

from . import constants


LOGGER = logging.getLogger('korben.sync.utils')


def file_leaf(*args):
    '''
    Where *args are str, the last str is the name of a file and the preceding
    str are path fragments, create necessary and suffcient directories for the
    file to be created at the path.
    '''
    path = os.path.join(*map(str, args))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def handle_multiprop(prop):
    name = etree.QName(prop).localname
    retval = {}
    for frag in prop:
        col_name = "{0}_{1}".format(name, etree.QName(frag.tag).localname)
        if frag.text is None:
            value = None
        else:
            value = frag.text.strip()
        retval[col_name] = value
    return retval


def handle_datetime(prop):
    try:
        psql_date = ' '.join(prop.text.strip('Z').split('T'))  # ???
    except:
        psql_date = None
    return {etree.QName(prop).localname: psql_date}


PROP_KV_MAP = {
    'Microsoft.Crm.Sdk.Data.Services.EntityReference': handle_multiprop,
    'Microsoft.Crm.Sdk.Data.Services.OptionSetValue': handle_multiprop,
    'Edm.DateTime': handle_datetime,
}


def entry_row(col_names, link_fkey_map, entry):
    'Extract a row dict from an OData entry'
    row = {}
    for prop in entry.find(constants.CONTENT_TAG)[0]:
        prop_type = prop.attrib.get(constants.TYPE_KEY)
        if prop_type in PROP_KV_MAP:
            row.update(PROP_KV_MAP[prop_type](prop))
        else:
            row.update({
                etree.QName(prop).localname:
                prop.text.strip() if prop.text else prop.text
            })
        to_pop = []
    '''
    for link in entry.find(LINK_TAG):
        import ipdb;ipdb.set_trace()
        pass
    '''
    if col_names:
        # optionally filter by a column set
        for key in row:
            if key not in col_names:
                to_pop.append(key)
        for key in to_pop:
            row.pop(key)
    return row


def link_fkey_map(table, entry):
    'Generate a mapping from table fkey to link name'
    import ipdb;ipdb.set_trace()
    link_map = {}
    fkey_names = map(lambda fkey: fkey.name, table.foreign_keys)
    for link in entry.findall(LINK_TAG):
        try:
            link_type = link.attrib['type'].split(';')[-1].replace('type=', '')
            if link_type == 'entry':
                link_title = link.attrib['title']
                link_map[link_title] = next([
                    # this is quite a loose way of finding the proper fkey name
                    # for a given link. it would be cool to have pylset
                    # generate a schema that names fkeys by their link title
                    x for x in fkey_names if link_title in fkey_names
                ])
        except:  # something happened
            pass
    return link_map


class MultiProcessingLog(logging.Handler):
    def __init__(self, name, mode, maxsize, rotate):
        logging.Handler.__init__(self)

        self._handler = RotatingFileHandler(name, mode, maxsize, rotate)
        self.queue = multiprocessing.Queue(-1)

        t = threading.Thread(target=self.receive)
        t.daemon = True
        t.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def receive(self):
        while True:
            try:
                record = self.queue.get()
                self._handler.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        # ensure that exc_info and args
        # have been stringified.  Removes any chance of
        # unpickleable things inside and possibly reduces
        # message size sent over the pipe
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            dummy = self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        self._handler.close()
        logging.Handler.close(self)


def parse_atom_entries(cache_dir, entity_name, name, path=None):
    'Parse <entry> elements from an XML document in Atom format'
    if path is None:
        path = os.path.join(cache_dir, 'atom', entity_name, name)
    with open(path, 'rb') as cache_fh:
        try:
            root = etree.fromstring(cache_fh.read())
            return root.findall(constants.ENTRY_TAG)
        except etree.XMLSyntaxError:
            LOGGER.error('Bad XML!')
            # scrape failed
            return
