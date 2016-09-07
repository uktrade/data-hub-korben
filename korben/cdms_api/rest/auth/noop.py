import json
from requests import Session


class NoopAuth(object):
    'No-op authentication for testing purposes'

    def __init__(self):
        self.session = Session()

    def make_request(self, verb, url, data=None):
        'Pass calls to attached session object'
        if data is None:
            data = {}
        return getattr(self.session, verb)(url, data=json.dumps(data))
