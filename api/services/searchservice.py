from api.models.searchitem import SearchItem
from datahubapi import settings


def transform_search_result(es_result, term, filters=[]):
    result = {
        "term": term,
        "total": es_result["hits"]["total"],
        "max_score": es_result["hits"]["max_score"],
        "hits": es_result["hits"]["hits"],
        "filters": filters
    }

    facets = {}
    aggregations = es_result["aggregations"]

    for aggregation_key, aggregation_value in aggregations.items():
        facets[aggregation_key] = []
        for aggregation_bucket in aggregation_value["buckets"]:
            facets[aggregation_key].append({"value": aggregation_bucket["key"], "total": aggregation_bucket["doc_count"]})

    result["facets"] = facets
    return result


def search(term, filters=[]):
    data = {
        "query": {
            "query_string": {"query": term},
        },
        "aggregations": {
            "result_type": {
                "terms": {
                    "field": "result_type"
                }
            }
        }
    }

    index_name = SearchItem.Meta.es_index_name
    es_results = settings.ES_CLIENT.search(index=index_name, body=data)
    result = transform_search_result(es_result=es_results, term=term)
    return result
