import datetime
import logging
import os

from lxml import etree

from korben.cdms_api.rest.api import CDMSRestApi

from .. import utils as sync_utils
from .. import constants
from . import types

LOGGER = logging.getLogger('korben.sync.scrape.utils')


def raise_on_cdms_resp_errors(entity_name, offset, resp):
    '''
    carry out a healthy whack of inspection
    it’s hairy, but that’s how we like it
    '''
    if not resp.ok:
        try:
            root = etree.fromstring(resp.content)
            if 'paging' in root.find(constants.MESSAGE_TAG).text:
                # assuming this means we tried to reach beyond the last page
                raise types.EntityPageNoData(
                    "500 page out {0} {1}".format(
                        entity_name, offset
                    )
                )
        except AttributeError:
            # no message in xml
            raise types.EntityPageDynamicsBombed(
                "{0} {1}".format(entity_name, offset)
            )
        except etree.XMLSyntaxError:
            # no xml in xml
            raise types.EntityPageDynamicsBombed(
                "{0} {1}".format(entity_name, offset)
            )
        raise RuntimeError("{0} {1} unhandled".format(entity_name, offset))
    try:
        root = etree.fromstring(resp.content)  # check XML is parseable
        if not root.findall('{http://www.w3.org/2005/Atom}entry'):
            # paged out in a useless way
            raise types.EntityPageNoData("{0} {1}".format(entity_name, offset))
    except etree.XMLSyntaxError:
        raise types.EntityPageDeAuth("{0} {1}".format(entity_name, offset))


def atom_cache_key(entity_name, offset):
    'Return the path where atom reqponses are cached'
    return sync_utils.file_leaf('cache', 'atom', entity_name, offset)


def duration_record(entity_name, offset):
    'Return the path where a request duration record should be written'
    return sync_utils.file_leaf('cache', 'duration', entity_name, offset)


def is_cached(entity_name, offset):
    '''
    Determine if a certain request is cached, return is a 2-tup (bool, str)
    where the bool is whether or not the request is cached and the str is the
    path it either is or should be cached at.
    '''
    path = atom_cache_key(entity_name, offset)
    if not os.path.isfile(path):
        return False, path
    try:
        with open(path, 'rb') as cache_fh:
            etree.fromstring(cache_fh.read())
    except etree.XMLSyntaxError as exc:
        return False, path
    return True, path


def is_pending(entity_page):
    'Convenience function to test if an EntityPage object is in pending state'
    return entity_page.state == types.EntityPageState.pending


api = CDMSRestApi()  # puke


def cdms_list(entity_name, offset):
    '''
    Call the `cdms_api.list` method, passing through the entity_name and
    offset. This function records the duration of the network request. It also
    caches the resulting response if it’s successful and raises an informative
    exception if it’s not.
    '''
    cached, cache_path = is_cached(entity_name, offset)
    if cached:  # nothing to do, just load resp from cache
        with open(cache_path, 'rb') as cache_fh:
            return cache_fh.read()
    start_time = datetime.datetime.now()
    resp = api.list(entity_name, skip=offset)  # the actual request
    time_delta = (datetime.datetime.now() - start_time).seconds

    # the below will raise if the response is no good
    raise_on_cdms_resp_errors(entity_name, offset, resp)

    # record our expensive network request
    with open(duration_record(entity_name, offset), 'w') as duration_fh:
        duration_fh.write(str(time_delta))
    with open(cache_path, 'wb') as cache_fh:
        cache_fh.write(resp.content)
    LOGGER.info("{0} ({1}) {2}s".format(entity_name, offset, time_delta))
    return resp.content
