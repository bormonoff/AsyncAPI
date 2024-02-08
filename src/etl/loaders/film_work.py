import elastic_transport
from core import config
from elasticsearch.helpers import bulk

from etl import models
from etl.utils import backoff as etl_backoff
from etl.utils.connectors import elastic_connect


class FilmWorkLoader:
    """load film works data to Elasticsearch"""

    def __init__(self, index_name: str, chunk_size: int):
        self.index_name = index_name
        self.chunk_size = chunk_size

    def load(self, film_works: list[models.FilmWork]):
        data = [
            {
                "_index": self.index_name,
                "_op_type": "update",
                "_id": film_work.id,
                "doc": {
                    "id": film_work.id,
                    "imdb_rating": film_work.rating,
                    "title": film_work.title,
                    "description": film_work.description,
                    "type": film_work.type,
                    "genres_names": film_work.genres_names,
                    "genres": [dict(genre) for genre in film_work.genres],
                    "directors_names": film_work.directors_names,
                    "actors_names": film_work.actors_names,
                    "writers_names": film_work.writers_names,
                    "directors": [dict(director) for director in film_work.directors],
                    "actors": [dict(actor) for actor in film_work.actors],
                    "writers": [dict(writer) for writer in film_work.writers],
                    # На всякий случай добавил эти поля, чтобы все тесты проходили успешно.
                    "director": film_work.directors_names,
                    "genre": film_work.genres_names,
                },
                "doc_as_upsert": True,
            }
            for film_work in film_works
        ]

        for chunk in (data[i : i + self.chunk_size] for i in range(0, len(data), self.chunk_size)):
            self._bulk_chunk(chunk)

    @etl_backoff.backoff((elastic_transport.ConnectionError, elastic_transport.SerializationError))
    def _bulk_chunk(self, chunk: list):
        with elastic_connect(config.settings.ELASTIC_DSN) as elk_conn:
            bulk(elk_conn, actions=chunk)
