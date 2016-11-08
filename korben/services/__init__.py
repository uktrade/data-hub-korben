import urllib
from elasticsearch import Elasticsearch
from redis import Redis

from korben import config
from . import db_manager

redis_url = urllib.parse.urlparse(config.redis_url)
redis = Redis(
    url=redis_url.hostname, port=redis_url.port, decode_responses=True
)
db = db_manager.DatabaseManager()
es = Elasticsearch(hosts=[{'host': config.es_host, 'port': config.es_port}])
