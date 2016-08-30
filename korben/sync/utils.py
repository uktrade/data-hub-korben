from lxml import etree

TYPE_KEY = '{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}type'
CONTENT_TAG = '{http://www.w3.org/2005/Atom}content'

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
    for prop in entry.find(CONTENT_TAG)[0]:
        prop_type = prop.attrib.get(TYPE_KEY)
        if prop_type in PROP_KV_MAP:
            row.update(PROP_KV_MAP[prop_type](prop))
        else:
            row.update({
                etree.QName(prop).localname:
                prop.text.strip() if prop.text else prop.text
            })
        to_pop = []
    for link in entry.find(LINK_TAG):
        import ipdb;ipdb.set_trace()
        pass
    for key in row:
        if key not in col_names:
            to_pop.append(key)
    for key in to_pop:
        row.pop(key)
    return row


def get_link_fkey_map(table, entry):
    'Generate a mapping from table fkey to link name'
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
