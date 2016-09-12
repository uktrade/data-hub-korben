import logging
import os

from lxml import etree

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
