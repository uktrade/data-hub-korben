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
    'repos':                 (True, False, None),
    'namespace':             (True, False, 'bmu'),
}


with open('conf.yaml', 'r') as __config_yaml_fh:
    __config_yaml = __yaml.load(__config_yaml_fh.read())


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
                value = __os.environ[name.upper()]
    if not value and required and default:
        value = default
    if value:
        globals()[name] = value
    elif required:
        raise NameError(
            "Configuration key `{0}` is required".format(name)
        )

for name in __config_spec.keys():
    __set_config(name)
