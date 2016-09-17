'Namespace for sync module'
from . import poll, traverse, scrape  # NOQA
from . import odata_initial, django_initial, ch, es_initial

COMMANDS = {
    'scrape': scrape.main,
    'odata-initial': odata_initial.main,
    'django-initial': django_initial.main,
    'ch': ch.main,
    'es-initial': es_initial.main,
    'poll': poll.main,
}

__all__ = ('COMMANDS', 'poll', 'traverse')
