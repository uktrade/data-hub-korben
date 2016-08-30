'Namespace for sync module'
from . import poll, traverse, scrape  # NOQA

COMMANDS = {
    'scrape': scrape.main,
    'poll': poll.main,
}

__all__ = ('COMMANDS', 'poll', 'traverse', 'scrape')
