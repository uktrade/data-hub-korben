import os
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


ES_HOST = os.getenv("ES_HOST")
ES_PORT = int(os.getenv("ES_PORT"))
ES_ACCESS = os.getenv("ES_ACCESS")
ES_SECRET = os.getenv("ES_SECRET")
ES_REGION = os.getenv("ES_REGION")

if ES_ACCESS is None:
    ES_CLIENT = Elasticsearch(
        hosts=[{'host': ES_HOST, 'port': ES_PORT}],
        connection_class=RequestsHttpConnection
    )
else:
    awsauth = AWS4Auth(ES_ACCESS, ES_SECRET, ES_REGION, 'es')

    ES_CLIENT = Elasticsearch(
        hosts=[{'host': ES_HOST, 'port': ES_PORT}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
