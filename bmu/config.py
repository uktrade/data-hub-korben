import yaml

with open('config.yaml', 'r') as config_fh:
    for name, value in yaml.load(config_fh.read()).items():
        locals()[name] = value
