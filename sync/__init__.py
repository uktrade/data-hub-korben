'Namespace for sync module'
from . import poll, traverse, scrape, clean_cache, inspect_xml  # NOQA

COMMANDS = {
    'scrape': scrape.main,
    'poll': poll.main,
    'clean': clean_cache.main,
    'inspect': inspect_xml.main,
}

__all__ = ('COMMANDS', 'poll', 'traverse', 'scrape')
