'Namespace for sync module'
from . import poll, traverse, scrape, clean_cache  # NOQA

COMMANDS = {
    'scrape': scrape.main,
    'poll': poll.main,
    'clean': clean_cache.main,
}

__all__ = ('COMMANDS', 'poll', 'traverse', 'scrape')
