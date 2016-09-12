from elasticsearch import Elasticsearch
from korben import config

client = Elasticsearch(
    hosts=[{'host': config.es_host, 'port': config.es_port}]
)
