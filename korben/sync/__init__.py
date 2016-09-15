'Namespace for sync module'
from . import poll, traverse, scrape  # NOQA
from . import populate, ch, django_initial, es_initial

COMMANDS = {
    'scrape': scrape.main,
    'django-initial': django_initial.main,
    'es-initial': es_initial.main,
    'poll': poll.main,
    'populate': populate.main,
    'ch': ch.main,
}

__all__ = ('COMMANDS', 'poll', 'traverse', 'scrape')
