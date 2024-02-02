import elastic_transport
from elasticsearch.helpers import bulk

from core.config import settings
from etl.models import ExtendedPerson
from etl.utils.backoff import backoff
from etl.utils.connectors import elastic_connect


class PersonLoader:
    """Загружает данные кинопроизведений в Elasticsearch"""

    def __init__(self, index_name: str, chunk_size: int):
        self.index_name = index_name
        self.chunk_size = chunk_size

    def load(self, persons: list[ExtendedPerson]):
        data = [
            {
                "_index": self.index_name,
                "_op_type": "update",
                "_id": person.id,
                "doc": {
                    "id": person.id,
                    "fullname": person.name,
                    "films": [dict(film) for film in person.films],
                },
                "doc_as_upsert": True,
            }
            for person in persons
        ]
        for chunk in (data[i : i + self.chunk_size] for i in range(0, len(data), self.chunk_size)):
            self._bulk_chunk(chunk)

    @backoff((elastic_transport.ConnectionError, elastic_transport.SerializationError))
    def _bulk_chunk(self, chunk: list):
        with elastic_connect(settings.ELASTIC_DSN) as elk_conn:
            bulk(elk_conn, actions=chunk)
