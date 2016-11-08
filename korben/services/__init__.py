from elasticsearch import Elasticsearch
from redis import Redis

from korben import config
from . import db_manager

redis_kwargs = {
    'host': config.redis_url.hostname,
    'decode_responses': True,
}
if config.redis_url.port:
    redis_kwargs['port'] = config.redis_url.port
redis = Redis(**redis_kwargs)

db = db_manager.DatabaseManager()

es = Elasticsearch(hosts=[{'host': config.es_host, 'port': config.es_port}])
