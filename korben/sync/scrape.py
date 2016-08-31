import datetime
import logging
import multiprocessing
import os
import pickle
import time
import random
import uuid

from korben.cdms_api.connection import rest_connection as api
from . import constants

from lxml import etree

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger('korben.sync.scrape')


PROCESSES = 128

ENTITY_REQUEST = multiprocessing.Array('i', len(constants.ENTITY_NAMES))
ENTITY_OFFSETS = multiprocessing.Array('i', len(constants.ENTITY_NAMES))
AUTH_IN_PROGRESS = multiprocessing.Value('i', 0)


def file_leaf(*args):
    path = os.path.join(*map(str, args))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def list_cache_key(service, offset):
    return file_leaf('cache', 'list', service, offset)


def timing_record(service, offset):
    return file_leaf('cache', 'timing', service, offset)


class CDMSListRequestCache(object):

    def holds(self, service, skip):
        path = list_cache_key(service, skip)
        if not os.path.isfile(path):
            return False
        try:
            with open(path, 'rb') as cache_fh:
                resp = pickle.load(cache_fh)
                etree.fromstring(resp.content)
        except etree.XMLSyntaxError as exc:
            return False
        return True

    def list(self, service, skip):
        cache_path = list_cache_key(service, skip)
        if self.holds(service, skip):
            with open(cache_path, 'rb') as cache_fh:
                return pickle.load(cache_fh)
        start_time = datetime.datetime.now()
        resp = api.list(service, skip=skip)
        with open(timing_record(service, skip), 'w') as timing_fh:
            time_delta = (datetime.datetime.now() - start_time).seconds
            timing_fh.write(str(time_delta))
        if not resp.ok:
            return resp  # don't cache fails
        try:
            root = etree.fromstring(resp.content)  # check XML is parseable
            if not root.findall('{http://www.w3.org/2005/Atom}entry'):
                # some weird crap from M$ here
                return None
        except etree.XMLSyntaxError as exc:
            # assume we got deauth'd, trust poll_auth to fix it, don't cache
            LOGGER.error(
                "{0} ({1}) {2}s (DEAUTH)".format(service, skip, time_delta)
            )
            return False
        LOGGER.info("{0} ({1}) {2}s".format(service, skip, time_delta))
        with open(cache_path, 'wb') as cache_fh:
            pickle.dump(resp, cache_fh)
        return resp


def cache_passthrough(cdms_api, entity_name, offset):
    entity_index = constants.ENTITY_INT_MAP[entity_name]
    ENTITY_OFFSETS[entity_index] += 50  # bump offset
    identifier = uuid.uuid4()
    LOGGER.debug(
        "Starting {0} {1} {2}".format(entity_name, offset, identifier)
    )
    resp = cdms_api.list(entity_name, offset)
    if resp is None:
        # means trash response
        ENTITY_REQUEST[entity_index] = -1  # kill it
        return
    if resp is False:
        # means deauth'd
        ENTITY_REQUEST[entity_index] -= 1  # this request is over
                                           # don't increment offset
        return

    if resp.ok:
        try:
            etree.fromstring(resp.content)  # check XML is parseable
            root = etree.fromstring(resp.content)
            if not root.findall('{http://www.w3.org/2005/Atom}entry'):
                LOGGER.info(
                    "No entries {0} {1} {2}".format(
                        entity_name, offset, identifier
                    )
                )
                return
        except etree.XMLSyntaxError as exc:
            # need to auth
            return
        # everything went according to plan
        ENTITY_REQUEST[entity_index] -= 1  # this request is complete
        LOGGER.debug(
            "Completing {0} {1} {2}".format(entity_name, offset, identifier)
        )
        return

    if not resp.ok:
        ENTITY_REQUEST[entity_index] = -1  # don’t carry on with this entity
                                           # will get picked up on next run
        if resp.status_code == 500:
            try:
                root = etree.fromstring(resp.content)
                if 'paging' in root.find(constants.MESSAGE_TAG).text:
                    # let's pretend this means we reached the end and set this
                    # entity type to spent
                    LOGGER.info(
                        "Spent {0} {1} {2}".format(
                            entity_name, offset, identifier
                        )
                    )
                    return
                LOGGER.error(
                    "Error {0} {1} {2}".format(
                        entity_name, offset, identifier
                    )
                )
            except Exception as exc:
                LOGGER.error(
                    "Failing {0} {1} {2}".format(
                        entity_name, offset, identifier
                    )
                )
                ENTITY_REQUEST[entity_index] -= 1
                # something bad, unknown and unknowable happened
                return
        else:
            ENTITY_REQUEST[entity_index] = -1
            LOGGER.error(
                "Failing {0} {1} {2}".format(entity_name, offset, identifier)
            )
            return


def poll_auth(n):
    resp = api.list('FixedMonthlyFiscalCalendar')  # requests here seem fast
    if not resp.ok:
        time.sleep(1)
        return poll_auth(True)
    try:
        etree.fromstring(resp.content)  # check XML is parseable
    except etree.XMLSyntaxError as exc:
        LOGGER.debug('Authenticating')
        # assume we got the login page, just try again
        AUTH_IN_PROGRESS.value = 1
        api.auth.setup_session(True)
        AUTH_IN_PROGRESS.value = 0
        LOGGER.debug('Authentication complete')


def main():
    cache = CDMSListRequestCache()
    pool = multiprocessing.Pool(processes=PROCESSES)
    for index, entity_name in enumerate(constants.ENTITY_NAMES):
        ENTITY_REQUEST[index] = 0
        try:
            caches = os.listdir(os.path.join('cache', 'list', entity_name))
            ENTITY_OFFSETS[index] = max(map(int, caches)) + 50
        except (FileNotFoundError, ValueError) as exc:
            ENTITY_OFFSETS[index] = 0
    api.auth.setup_session(True)
    last_polled = 0
    last_report = 0
    first_loop = True
    pending = []
    while True:
        now = datetime.datetime.now()

        # reporting, pending tracking
        if now.second and now.second % 3 == 0 and last_report != now.second:
            last_report = now.second
            pending_swap = []
            complete = 0
            for result in pending:
                if not result.ready():
                    pending_swap.append(result)
                else:
                    complete += 1
            pending = pending_swap
            LOGGER.debug('Entity request status:')
            dead = 0
            for entity_index, request_count in enumerate(ENTITY_REQUEST[:]):
                if request_count > 0:
                    LOGGER.debug(
                        "  {0} {1}".format(
                            constants.ENTITY_NAMES[entity_index],
                            request_count
                        )
                    )
                else:
                    dead += 1
            print("Entities complete/dead/errored: {0}".format(dead))
            waiting = len(list(filter(lambda x: x == 0, ENTITY_REQUEST[:])))
            report_fmt = (
                "{0} - "
                "{1} requests pending, "
                "{2} entity types waiting, "
                "{3} complete since last report"
            )
            LOGGER.info(report_fmt.format(
                now.strftime('%Y-%m-%d %H:%M:%S'),
                len(pending),
                waiting,
                complete
            ))
            done_conditions = (
                not first_loop,
                not len(pending),
                not waiting,
                not complete,
            )
            if all(done_conditions):
                LOGGER.info("Scrape complete!?")
                exit(1)  # i doubt it

        # auth management
        if now.second and now.second % 5 == 0 and last_polled != now.second:
            last_polled = now.second
            poll_auth(now.second)

        # add to request queues
        sample = random.sample(
            constants.ENTITY_NAMES,
            len(constants.ENTITY_NAMES)
        )
        for entity_name in sample:

            # throttling
            if len(pending) >= PROCESSES:
                continue

            entity_index = constants.ENTITY_INT_MAP[entity_name]
            if ENTITY_REQUEST[entity_index] == -1:  # marked as bad
                continue
            result = pool.apply_async(
                cache_passthrough,
                (cache, entity_name, ENTITY_OFFSETS[entity_index]),
            )
            pending.append(result)
            ENTITY_REQUEST[entity_index] += 1  # increment request count for
                                               # this entity type
        first_loop = False
