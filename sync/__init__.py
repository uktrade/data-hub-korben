'Namespace for sync module'
from . import poll, traverse, scrape  # NOQA
from . import clean_cache, inspect_xml, populate

COMMANDS = {
    'scrape': scrape.main,
    'poll': poll.main,
    'clean': clean_cache.main,
    'inspect': inspect_xml.main,
    'populate': populate.main,
}

__all__ = ('COMMANDS', 'poll', 'traverse', 'scrape')
