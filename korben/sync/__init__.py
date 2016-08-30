'Namespace for sync module'
from . import poll, traverse, scrape  # NOQA

COMMANDS = {
    'scrape': scrape.main,
}

__all__ = ('COMMANDS', 'poll', 'traverse', 'scrape')
