from korben import config
from raven import Client

SENTRY_CLIENT = Client(config.korben_sentry_dsn)
