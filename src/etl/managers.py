from typing import Type

from psycopg2.extensions import connection as pg_connection
from utils.logger import logger
from utils.state import State

from etl.extractors.base import BaseExtractor
from etl.loaders.film_work import FilmWorkLoader
from etl.transformers.film_work import FilmWorkTransformer


class FilmWorkETLManager:
    """Менеджер, который запускает ETL для одной из таблиц"""

    def __init__(
        self,
        pg_conn: pg_connection,
        extractor_class: Type[BaseExtractor],
        extract_chunk_size: int,
        load_chunk_size: int,
        index_name: str,
        state: State,
    ):
        self._pg_conn = pg_conn
        self.extractor_class = extractor_class
        self.extract_chunk_size = extract_chunk_size
        self.load_chunk_size = load_chunk_size
        self.index_name = index_name
        self.state = state

    def run(self):
        logger.info("Start ETL for %s", self.extractor_class.TABLE_NAME)
        state_key = f"{self.extractor_class.TABLE_NAME}_updated_at"
        updated_at = self.state.get(state_key)

        extractor = self.extractor_class(self._pg_conn, self.extract_chunk_size, updated_at)
        data, last_updated_at = extractor.extract()

        if data:
            transformer = FilmWorkTransformer()
            data = transformer.transform(data)

            loader = FilmWorkLoader(self.index_name, self.load_chunk_size)
            loader.load(data)
            self.state.set(state_key, last_updated_at)

        logger.info(
            "ETL for %s successfully finished.\nTotal: %d",
            extractor.TABLE_NAME,
            len(data),
        )
