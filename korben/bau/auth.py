from hashlib import sha256

from pyramid import security
from pyramid import interfaces
from streql import equals as constant_time_compare
from zope import interface

from korben import config


class Root(object):
    __acl__ = ((security.Allow, 'leeloo', 'access'),)
    def __init__(self, request):
        pass


def generate_signature(path, body, salt):
    message = path + body + salt
    return sha256(message).hexdigest()


def sign_request(request):
    path = bytes(request.path, 'utf-8')
    return generate_signature(path, request.body, config.datahub_secret)


@interface.implementer(interfaces.IAuthenticationPolicy)
class AuthenticationPolicy(object):

    def _check_signature(self, request):
        signature = request.headers.get('X-Signature', '')
        expected_signature = sign_request(request)
        return constant_time_compare(signature, expected_signature)

    def authenticated_userid(self, request):
        pass

    def unauthenticated_userid(self, request):
        pass

    def effective_principals(self, request):
        if self._check_signature(request):
            return ['leeloo', 'access']
        return []

    def remember(self, request, userid, **kw):
        return []

    def forget(self, request):
        return []
