import os as __os
import yaml as __yaml

__config_spec = {
    #                                       default
    #                             read from  value
    #   name            required     env     /
    #    |                     \      |     /
    'github_user':           (True, True, None),
    'github_token':          (True, True, None),
    'github_webhook_secret': (True, True, None),
    'buildbot_url':          (True, True, 'http://localhost:8010/change_hook/bmu'),
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
        raise NameError(
            "`{0}` is not a recongised configuration key".format(name)
        )
    value = __config_yaml.get(name)
    if read_env:
        here = __os.path.dirname(__file__)
        try:
            with open(__os.path.join(here, '..', name.upper()), 'r') \
            as __constant_fh:
                value = __constant_fh.read().rstrip('\n')
        except IOError as exc:
            if exc.errno == 2:
                try:
                    value = __os.environ[name.upper()]
                except KeyError:
                    pass
    if not value and required and default:
        value = default
    if value:
        globals()[name] = value
    elif required:
        raise NameError(
            "Configuration key `{0}` is required".format(name)
        )


def populate(path=None):
    if not path:
        try:
            path = __os.environ['BMU_CONF_PATH']
        except KeyError:
            pass
    if path:
        with open(path, 'r') as __config_yaml_fh:
            globals()['__config_yaml'] = __yaml.load(__config_yaml_fh.read())
    else:
        globals()['__config_yaml'] = {}

    for name in __config_spec.keys():
        __set_config(name)

try:
    populate()
except NameError:
    pass
