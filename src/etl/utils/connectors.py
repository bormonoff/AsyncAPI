import psycopg2
from elasticsearch import Elasticsearch
from psycopg2.extensions import connection as pg_connection
from psycopg2.extras import RealDictCursor

from etl.utils import backoff as etl_backoff


@etl_backoff.backoff()
def postgres_connect(dsn) -> pg_connection:
    """Контекстный менеджер для соединения с Postgres"""

    return psycopg2.connect(dsn=dsn, cursor_factory=RealDictCursor)


@etl_backoff.backoff()
def elastic_connect(dsn) -> Elasticsearch:
    """Контекстный менеджер для соединения с ElasticSearch"""

    connection = Elasticsearch(dsn)
    if not connection.ping():
        raise ConnectionError("Can not connect to Elasticsearch")
    return connection
