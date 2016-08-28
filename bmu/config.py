import os as __os
import yaml as __yaml
import constants as __constants

class ConfigError(Exception):
    pass

__config_spec = {
    #                                       default
    #                             read from  value
    #   name            required     env     /
    #    |                     \      |     /
    'github_user':           (True, True, None),
    'github_token':          (True, True, None),
    'github_webhook_secret': (True, True, None),
    'buildbot_url':          (True, True, 'http://localhost:8010'),
    'buildbot_auth':         (True, True, None),
    'repos':                 (True, False, None),
    'namespace':             (True, False, 'bmu'),
    'developers':            (False, False, None),
    'mergers':               (True, False, None),
}


def __set_config(name, value=None):
    '''
    Get a config value from a file in the repo root, or from an evironment
    variable with a matching name
    '''
    try:
        required, read_env, default = __config_spec[name]
    except KeyError:
        raise ConfigError(
            "`{0}` is not a recognised configuration key".format(name)
        )
    value = __config_yaml.get(name)
    if read_env:
        env_name = "BMU_{0}".format(name.upper())
        try:
            value = __os.environ[env_name]
            print('Actually got env var value for {0}'.format(env_name))
        except KeyError:
            here = __os.path.dirname(__file__)
            try:
                constant_filename = __os.path.join(here, '..', env_name)
                with open(constant_filename, 'r') as constant_fh:
                    value = constant_fh.read().rstrip('\n')
            except IOError as exc:
                if exc.errno == 2:
                    pass
                else:
                    raise
    if not value and required and default:
        value = default
    if value:
        globals()[name] = value
    elif required:
        raise ConfigError(
            "Configuration key `{0}` is required".format(name)
        )


def populate(path=None):
    if not path:
        try:
            path = __os.environ[__constants.CONF_PATH]
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
            pass

    else:
        globals()['__config_yaml'] = {}

    for name in __config_spec.keys():
        __set_config(name)

try:
    populate()
except ConfigError:
    pass
