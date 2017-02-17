'''
Authentication-related code for Pyramid app

 - Root object with ACL for Configurator
 - Utils for request signature
 - IAuthenticationPolicy implementation
'''
from pyramid import security
from pyramid import interfaces
from streql import equals as constant_time_compare
from zope import interface

from korben import config
from korben.utils import generate_signature


class Root(object):
    'Provide the most basic non-trivial ACL imaginable'
    __acl__ = ((security.Allow, 'leeloo', 'access'),)
    def __init__(self, request):
        pass


def sign_request(request):
    'Generate signature for passed request'
    path = bytes(request.path, 'utf-8')
    return generate_signature(path, request.body, config.datahub_secret)


@interface.implementer(interfaces.IAuthenticationPolicy)
class AuthenticationPolicy(object):
    'Apply shared secret authentication'

    def _check_signature(self, request):
        'Extract signature from headers and compare it with expected sig'
        signature = request.headers.get('X-Signature', '')
        expected_signature = sign_request(request)
        return constant_time_compare(signature, expected_signature)

    def authenticated_userid(self, request):
        pass

    def unauthenticated_userid(self, request):
        pass

    def effective_principals(self, request):
        'Check provided signature on incoming request, allowing access or not'
        if self._check_signature(request):
            return ['leeloo', 'access']
        return []

    def remember(self, request, userid, **kw):
        return []

    def forget(self, request):
        return []
