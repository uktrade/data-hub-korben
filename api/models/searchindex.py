class SearchIndex(object):
    def __init__(self, source_id, source_type, title, summary, postcode, sub_title=None, alt_address=None, alt_postcode=None):
        self.source_id = source_id
        self.source_type = source_type
        self.title = title
        self.sub_title = sub_title
        self.summary = summary
        self.postcode = postcode
        self.alt_address = alt_address
        self.alt_postcode = alt_postcode

        class Meta:
            es_index_name = 'datahub'
            es_type_name = 'searchindex'
            es_mapping = {
                'properties': {
                    'source_id': {'type': 'string', 'index': 'not_analyzed'},
                    'source_type': {'type': 'string', 'index': 'not_analyzed'},
                    'title': {'type': 'string', 'index': 'no'},
                    'sub_title': {'type': 'string', 'index': 'not_analyzed'},
                    'summary': {'type': 'string', 'index': 'not_analyzed'},
                    'postcode': {'type': 'string', 'index': 'not_analyzed'},
                    'alt_address': {'type': 'string', 'index': 'not_analyzed'},
                    'alt_postcode': {'type': 'string', 'index': 'not_analyzed'},
                }
            }