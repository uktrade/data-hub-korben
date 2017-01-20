import datetime
import json
import logging
import os

from korben.cdms_api.rest.api import CDMSRestApi
from korben import services
from . import types

LOGGER = logging.getLogger('korben.sync.scrape.utils')


def raise_on_cdms_resp_errors(entity_name, offset, resp):
    '''
    carry out a healthy whack of inspection
    it’s hairy, but that’s how we like it

    this function just raises an exception signalling the outcome of the
    request (see `types` module) or doesn’t raise if all is well
    '''
    resp_str = resp.content.decode(resp.encoding or 'utf8')
    if not resp.ok:
        if resp.status_code == 401:  # ACCESS DENIED!
            raise types.EntityPageDeAuth(
                "{0} {1} said ACCESS DENIED!".format(entity_name, offset)
            )
        try:
            resp_json = json.loads(resp_str)
            if 'paging' in resp_json['error']['message']['value']:
                # assuming this means we tried to reach beyond the last page
                raise types.EntityPageNoData(
                    "500 page out {0} {1}".format(entity_name, offset)
                )
        except types.EntityPageNoData:  # pass through
            raise
        except KeyError:
            # no error message in json
            LOGGER.error(resp_str)
            raise types.EntityPageDynamicsBombed(
                "{0} {1} had no error message".format(entity_name, offset)
            )
        except json.JSONDecodeError:
            # no json in json
            LOGGER.error(resp_str)
            raise types.EntityPageDynamicsBombed(
                "{0} {1} wasn’t in JSON".format(entity_name, offset)
            )
        except Exception as exc:
            LOGGER.error(resp_str)
            raise RuntimeError(
                "{0} {1} raised something unhandled".format(
                    entity_name, offset
                )
            )
    try:
        resp_json = json.loads(resp_str)
        # plain OData doesn't return in `results` key
        try:
            results = resp_json['d']['results']
        except TypeError as exc:
            results = resp_json['d']
        if not results:
            # paged out with empty response (ie. 'd.results' is an empty list)
            raise types.EntityPageNoData(
                "{0} {1} was beyond the last page".format(entity_name, offset)
            )
    except json.JSONDecodeError:
        raise types.EntityPageDeAuth(
            "{0} {1} said OK but not in JSON".format(entity_name, offset)
        )


def json_cache_key(entity_name, offset):
    'Return the path where JSON responses are cached'
    return os.path.join(*map(str, ('cache', 'json', entity_name, offset)))


def duration_record(entity_name, offset):
    'Return the path where a request duration record should be written'
    return os.path.join(*map(str, ('cache', 'duration', entity_name, offset)))


def is_cached(entity_name, offset):
    '''
    Determine if a certain request is cached, return is a 2-tup (bool, str)
    where the bool is whether or not the request is cached and the str is the
    path it either is or should be cached at.
    '''
    path = json_cache_key(entity_name, offset)
    value = services.redis.get(path)
    if not value:
        return False, path
    try:
        json.loads(value)
    except json.JSONDecodeError as exc:
        return False, path
    return True, path


def is_pending(entity_page):
    'Convenience function to test if an EntityPage object is in pending state'
    return entity_page.state == types.EntityPageState.pending


def cdms_list(client, entity_name, offset):
    '''
    Call the `cdms_api.list` method, passing through the entity_name and
    offset. This function records the duration of the network request. It also
    caches the resulting response if it’s successful and raises an informative
    exception if it’s not.
    '''
    cached, cache_path = is_cached(entity_name, offset)
    if cached:  # nothing to do, just load resp from cache
        return services.redis.get(cache_path)
    start_time = datetime.datetime.now()
    if client is None:
        client = CDMSRestApi()
    resp = client.list(entity_name, skip=offset)  # the actual request
    time_delta = (datetime.datetime.now() - start_time).seconds

    # the below will raise something useful, or pass by quietly
    raise_on_cdms_resp_errors(entity_name, offset, resp)

    # record our expensive network request
    services.redis.set(duration_record(entity_name, offset), str(time_delta))
    services.redis.set(
        cache_path, resp.content.decode(resp.encoding or 'utf-8')
    )
    LOGGER.info("{0} ({1}) {2}s".format(entity_name, offset, time_delta))
    return resp.content
