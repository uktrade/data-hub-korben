import datetime
import json
import logging
import os
import re


LOGGER = logging.getLogger('korben.sync.utils')
RE_ODATA_DATE = re.compile('\/Date\((?P<timestamp_milliseconds_str>\d+)\)')


def file_leaf(*args):
    '''
    Where *args are str, the last str is the name of a file and the preceding
    str are path fragments, create necessary and suffcient directories for the
    file to be created at the path.
    '''
    path = os.path.join(*map(str, args))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def handle_multiprop(prop_name, prop_value):
    retval = {}
    for frag_name, frag_value in prop_value.items():
        if frag_name.startswith('__'):
            continue
        retval["{0}_{1}".format(prop_name, frag_name)] = frag_value
    return retval


PROP_KV_MAP = {
    'Microsoft.Crm.Sdk.Data.Services.EntityReference': handle_multiprop,
    'Microsoft.Crm.Sdk.Data.Services.OptionSetValue': handle_multiprop,
}


def could_be_a_date_value(value):
    try:
        date_match = re.match(RE_ODATA_DATE, value)
    except TypeError:
        return  # it’s probably an int
    if not date_match:
        return
    timestamp_milliseconds_int = int(
        date_match.group('timestamp_milliseconds_str')
    )
    timestamp = timestamp_milliseconds_int / 1000
    date_object = datetime.datetime.fromtimestamp(timestamp)
    return date_object.isoformat().replace('T', ' ')


def entry_row(col_names, link_fkey_map, entry):
    'Extract a row dict from an OData entry'
    row = {}
    for name, value in entry.items():
        if name.startswith('__'):
            continue
        try:
            prop_type = value['__metadata']['type']
        except TypeError:
            date = could_be_a_date_value(value)
            # the above is pretty gross
            # TODO: refer to metadata for type info
            if date:
                row.update({name: date})
            else:
                row.update({name: value})
            continue
        except KeyError:
            continue  # ignore __deferred things
        if prop_type in PROP_KV_MAP:
            row.update(PROP_KV_MAP[prop_type](name, value))
    if col_names:
        to_pop = []
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


def parse_json_entries(cache_dir, entity_name, name, path=None):
    'Parse entry objects from a JSON document'
    if path is None:
        path = os.path.join(cache_dir, 'json', entity_name, name)
    with open(path, 'r') as cache_fh:
        try:
            json_resp = json.loads(cache_fh.read())
            return json_resp['d']
        except json.JSONDecodeError:
            LOGGER.error('Bad JSON!')
            # scrape failed
            return
