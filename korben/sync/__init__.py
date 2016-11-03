'Namespace for sync module'
from . import traverse, scrape  # NOQA
from . import odata_initial, django_initial, ch, es_initial, cdms_initial

COMMANDS = {
    'scrape': scrape.main,
    'odata': odata_initial.main,
    'django': django_initial.main,
    'ch': ch.main,
    'es': es_initial.main,
    'cdms': cdms_initial.main,
}

__all__ = ('COMMANDS', 'traverse')
