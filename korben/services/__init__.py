from elasticsearch import Elasticsearch
from redis import Redis

from korben import config
from . import db_manager

redis = Redis(host=config.redis_host, decode_responses=True)
db = db_manager.DatabaseManager()
es = Elasticsearch(hosts=[{'host': config.es_host, 'port': config.es_port}])
