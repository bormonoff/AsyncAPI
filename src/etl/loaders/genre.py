import elastic_transport
import models
from core.config import settings
from elasticsearch.helpers import bulk
from utils.backoff import backoff
from utils.connectors import elastic_connect


class GenreLoader:
    """Load genres data to Elasticsearch"""

    def __init__(self, index_name: str, chunk_size: int):
        self.index_name = index_name
        self.chunk_size = chunk_size

    def load(self, genres: list[models.Genre]):
        data = [
            {
                "_index": self.index_name,
                "_op_type": "update",
                "_id": genre.id,
                "doc": {
                    "id": genre.id,
                    "name": genre.name,
                },
                "doc_as_upsert": True,
            }
            for genre in genres
        ]

        for chunk in (data[i : i + self.chunk_size] for i in range(0, len(data), self.chunk_size)):
            self._bulk_chunk(chunk)

    @backoff((elastic_transport.ConnectionError, elastic_transport.SerializationError))
    def _bulk_chunk(self, chunk: list):
        with elastic_connect(settings.ELASTIC_DSN) as elk_conn:
            bulk(elk_conn, actions=chunk)
