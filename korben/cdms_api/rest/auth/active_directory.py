import json
import logging

import requests
from korben import config
from pyquery import PyQuery

from korben.cdms_api.cookie_storage import CookieStorage
from korben.cdms_api.exceptions import (
    CDMSUnauthorizedException,
    LoginErrorException,
    UnexpectedResponseException,
)


# Legacy logger from when auth was hard-wired into the API
logger = logging.getLogger('cmds_api.rest.api')


class ActiveDirectoryAuth:
    """
    Handle authentication via Active Directory using form submission, cookie
    retrieval and storage.

    Wraps a `requests.session` instance which it populates with Auth data.

    NOTE this is an extraction of auth functionality. Although the tests pass,
    many of them are mocked and this does not prove that auth works with API.
    """

    username = None
    password = None
    cookie_path = None

    def __init__(self, username=None, password=None, cookie_path=None):
        self.username = username or config.cdms_username
        self.password = password or config.cdms_password
        self.cookie_path = cookie_path or config.cdms_cookie_path
        self.cookie_storage = CookieStorage(self.cookie_path)
        self.setup_session()

    def setup_session(self, force=False):
        """
        So that we don't login every time, we save the cookie and load it afterwards.
        """
        if force:
            self.cookie_storage.reset()

        cookie = self.cookie_storage.read()
        if cookie:
            session = requests.session()
            jar = requests.cookies.RequestsCookieJar()
            jar._cookies = cookie
            session.cookies = jar
            self.session = session
        else:
            self.session = self.login()
            self.cookie_storage.write(self.session.cookies._cookies)

    def login(self):
        """
        This goes through the following steps:

        1. get login page
        2. submit the form with username and password
        3. the result is a form with a security token issued by the STS and the url of the next STS
            to validate the token
        4. submit the form of step 3. without making any changes
        5. repeat step 3. and 4 one more time to get the valid authentication cookie

        For more details, check: https://msdn.microsoft.com/en-us/library/aa480563.aspx
        """
        session = requests.session()

        # 1. get login page
        url = '{}/?whr={}'.format(config.cdms_base_url, config.cdms_adfs_url)
        resp = session.get(url)
        if not resp.ok:
            raise UnexpectedResponseException(
                '{} for status code {}'.format(url, resp.status_code),
                content=resp.content,
                status_code=resp.status_code
            )

        html_parser = PyQuery(resp.content)
        username_field_name = html_parser('input[name*=Username]')[0].name
        password_field_name = html_parser('input[name*=Password]')[0].name

        # 2. submit the login form with username and password
        resp = self._submit_form(
            session, resp.content,
            url=resp.url,
            params={
                username_field_name: self.username,
                password_field_name: self.password,
            }
        )

        # 3. and 4. re-submit the resulting form containing the security token so that the next STS can validate it
        resp = self._submit_form(session, resp.content)

        # 5. re-submit the form again to validate the token and get as result the authenticated cookie
        self._submit_form(session, resp.content)
        return session

    def _submit_form(self, session, source, url=None, params={}):
        """
        It submits the form contained in the `source` param optionally overriding form `params` and form `url`.

        This is needed as UKTI has a few STSes and the token has to be validated by all of them.
        For more details, check: https://msdn.microsoft.com/en-us/library/aa480563.aspx
        """
        html_parser = PyQuery(source)
        form_action = html_parser('form').attr('action')

        # get all inputs in the source + optional params passed in
        data = {field.get('name'): field.get('value') for field in html_parser('input')}
        data.update(params)

        url = url or form_action
        resp = session.post(url, data)

        # check status code
        if not resp.ok:
            raise UnexpectedResponseException(
                '{} for status code {}'.format(url, resp.status_code),
                content=resp.content,
                status_code=resp.status_code
            )

        # check response, if form action of source == form action of response => error page
        html_parser = PyQuery(resp.content)

        if form_action == html_parser('form').attr('action'):
            error_els = html_parser('[id$=ErrorTextLabel]')
            if error_els:
                raise LoginErrorException(', '.join([error_el.text for error_el in error_els]))
            raise UnexpectedResponseException(  # we don't know exactly what happened...
                'Unexpected Response.', content=resp.content
            )
        return resp

    def make_request(self, verb, url, data=None, headers=None):
        """
        Makes the call to CDMS, if 401 is found, it reauthenticates
        and tries again making the same call
        """
        if data is None:
            data = {}
        try:
            resp = self._make_request(verb, url, data=data, headers=headers)
        except CDMSUnauthorizedException:
            self.setup_session(force=True)
            return self.make_request(verb, url, data=data, headers=headers)
        return resp

    def _make_request(self, verb, url, data=None, headers=None):
        if data is None:
            data = {}
        logger.debug('Calling CDMS url (%s) on %s' % (verb, url))

        if data:
            data = json.dumps(data)
        default_headers = {
            'Accept': 'application/json', 'Content-Type': 'application/json'
        }
        if headers is not None:
            default_headers.update(headers)
        try:
            resp = getattr(self.session, verb)(
                url, data=data, headers=default_headers
            )
        except requests.exceptions.ConnectionError:
            return self._make_request(verb, url, data=data, headers=headers)
        if resp.status_code == 401:
            raise CDMSUnauthorizedException('De-auth')
        return resp
