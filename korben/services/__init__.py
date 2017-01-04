from elasticsearch import Elasticsearch
from redis import Redis

from korben import config
from . import db_manager

redis_kwargs = {
    'host': config.redis_url.hostname,
}

for name in ('port', 'password'):
    value = getattr(config.redis_url, name)
    if value is not None:
        redis_kwargs[name] = value

redis = Redis(decode_responses=True, **redis_kwargs)
redis_bytes = Redis(**redis_kwargs)

db = db_manager.DatabaseManager()

es = Elasticsearch(hosts=[{'host': config.es_host, 'port': config.es_port}])
