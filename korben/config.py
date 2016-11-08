from urllib.parse import urlparse as __urlparse
from contextlib import contextmanager as __ctxmgr
import os as __os
import yaml as __yaml
import logging as __logging
__logger = __logging.getLogger('korben.config')

class ConfigError(Exception):
    pass

__to_bytes = lambda x: bytes(x, 'utf8')
__noop = lambda x: x

__config_spec = {
    #                                            default
    #                                  read from  value    cast
    #   name                 required     env     /      function
    #    |                          \      |     /       /
    'cdms_cookie_path':            (True, True, None, __noop),
    'cdms_cookie_key':             (True, True, None, __to_bytes),
    'cdms_base_url':               (True, True, None, __noop),
    'cdms_username':               (True, True, None, __noop),
    'cdms_password':               (True, True, None, __noop),
    'cdms_adfs_url':               (True, True, None, __noop),
    'odata_entity_container_key':  (True, True, None, __noop),
    'database_odata_url':          (True, True, None, __noop),
    'database_url':                (True, True, None, __noop),
    'es_host':                     (True, True, 'es', __noop),
    'es_port':                     (True, True, 9200, __noop),
    'redis_url':                   (True, True, 'tcp://redis', __urlparse),
    'korben_sentry_dsn':           (True, True, None, __noop),
    'datahub_secret':              (True, True, None, __to_bytes),
    'leeloo_url':                  (True, True, 'http://leeloo:8000/korben', __noop),
}


def __set_config(name, value=None):
    '''
    Get a config value from a file in the repo root, or from an evironment
    variable with a matching name
    '''
    try:
        required, read_env, default, cast = __config_spec[name]
    except KeyError:
        raise ConfigError(
            "`{0}` is not a recognised configuration key".format(name)
        )
    if value:  # value was passed directly
        globals()[name] = cast(value)
        return
    value = __config_yaml.get(name)
    if read_env:
        try:
            value = __os.environ[name.upper()]
            __logger.debug("Reading {0} from envronment".format(name.upper()))
        except KeyError:
            here = __os.path.dirname(__file__)
            try:
                constant_filename = __os.path.join(here, '..', name.upper())
                with open(constant_filename, 'r') as constant_fh:
                    value = constant_fh.read().rstrip('\n')
            except IOError as exc:
                if exc.errno == 2:
                    pass
                else:
                    raise
    if not value and required and default:
        value = cast(default)
    if value:
        globals()[name] = cast(value)
    elif required:
        raise ConfigError(
            "Configuration key `{0}` is required".format(name)
        )


def populate(path=None, ignore=True):
    if not path:
        try:
            path = __os.environ['KORBEN_CONF_PATH']
        except KeyError:
            pass
    if path:
        with open(path, 'r') as __config_yaml_fh:
            try:
                globals()['__config_yaml'] = __yaml.load(__config_yaml_fh.read())
            except Exception as exc:
                msg = 'Could not parse config YAML ({0})'
                raise ConfigError(msg.format(exc))
            if not __config_yaml:
                raise ConfigError('Named config YAML was empty')

    else:
        globals()['__config_yaml'] = {}

    for name in __config_spec.keys():
        try:
            __set_config(name)
        except ConfigError as exc:
            if not ignore:
                raise
            __logger.info('Ignoring config exception:')
            __logger.info(exc)
    pass


@__ctxmgr
def temporarily(**changes):
    proper = {}
    for name, value in changes.items():
        proper[name] = globals().get(name)
        __set_config(name, value)
    yield
    for name, value in proper.items():
        globals()[name] = value


populate(ignore=True)
