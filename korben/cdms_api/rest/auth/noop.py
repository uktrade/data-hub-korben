import json
from requests import Session


class NoopAuth(object):
    'No-op authentication for testing purposes'

    def __init__(self):
        self.session = Session()

    def make_request(self, verb, url, data=None, headers=None):
        'Pass calls to attached session object'
        if data is None:
            data = {}
        default_headers = {
            'Accept': 'application/json', 'Content-Type': 'application/json'
        }
        if headers is not None:
            default_headers.update(headers)
        return getattr(self.session, verb)(
            url, data=json.dumps(data), headers=default_headers
        )

    def setup_session(self, *args, **kwargs):
        'Make code that expects to set up the session happy with a noop'
        pass
