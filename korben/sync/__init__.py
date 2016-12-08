'Namespace for sync module'
from . import traverse, scrape  # NOQA
from . import odata_initial, django_initial, ch, es_initial

COMMANDS = {
    # should be run in this order
    'scrape': scrape.main,
    'ch': ch.main,
    'django': django_initial.main,
    'es': es_initial.main,
}

__all__ = ('COMMANDS', 'traverse')
