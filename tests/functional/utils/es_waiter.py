import elasticsearch
import settings
from utils.backoff import backoff


@backoff()
def es_connect(es_dsn):
    connection = elasticsearch.Elasticsearch(es_dsn)
    if not connection.ping():
        raise ConnectionError("Can not connect to Elasticsearch")


if __name__ == "__main__":
    es_connect(settings.settings.elastic_dsn)
