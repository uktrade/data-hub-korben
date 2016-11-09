from elasticsearch import Elasticsearch
from redis import Redis

from korben import config
from . import db_manager

redis_kwargs = {
    'host': config.redis_url.hostname,
    'decode_responses': True,
}

for name in ('port', 'password'):
    value = getattr(config.redis_url, name)
    if value is not None:
        redis_kwargs[name] = value
redis = Redis(**redis_kwargs)

db = db_manager.DatabaseManager()

es = Elasticsearch(hosts=[{'host': config.es_host, 'port': config.es_port}])
