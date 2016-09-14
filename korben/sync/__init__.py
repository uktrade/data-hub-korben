'Namespace for sync module'
from . import poll, traverse, scrape  # NOQA
from . import clean_cache, populate, ch

COMMANDS = {
    'scrape': scrape.main,
    'poll': poll.main,
    'populate': populate.main,
    'ch': ch.main,
}

__all__ = ('COMMANDS', 'poll', 'traverse', 'scrape')
