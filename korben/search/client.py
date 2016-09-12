from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from korben import config

try:
    awsauth = AWS4Auth(
        config.es_access,
        config.es_secret,
        config.es_region,
        'es',
    )

    client = Elasticsearch(
        hosts=[{'host': config.es_host, 'port': config.es_port}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
except AttributeError:
    client = Elasticsearch(
        hosts=[{'host': config.es_host, 'port': config.es_port}],
        connection_class=RequestsHttpConnection
    )
