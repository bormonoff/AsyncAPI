"""ETL managers"""
from typing import Type

from core.logger import logger
from extractors.base import BaseExtractor
from loaders.film_work import FilmWorkLoader
from loaders.genre import GenreLoader
from loaders.person import PersonLoader
from psycopg2.extensions import connection as pg_connection
from transformers.film_work import FilmWorkTransformer
from transformers.genre import GenreTransformer
from transformers.person import PersonTransformer
from utils.state import State

TABLES = ("film_work", "genre", "person")

HANDLERS = {
    "film_work_transformer": FilmWorkTransformer,
    "genre_transformer": GenreTransformer,
    "person_transformer": PersonTransformer,
    "film_work_loader": FilmWorkLoader,
    "genre_loader": GenreLoader,
    "person_loader": PersonLoader,
    "film_work_idx": "movies",
    "genre_idx": "genres",
    "person_idx": "persons",
}


class FilmWorkETLManager:
    """Менеджер, который запускает ETL для одной из таблиц"""

    def __init__(
        self,
        pg_conn: pg_connection,
        extractor_class: Type[BaseExtractor],
        extract_chunk_size: int,
        load_chunk_size: int,
        state: State,
    ):
        self._pg_conn = pg_conn
        self.extractor_class = extractor_class
        self.extract_chunk_size = extract_chunk_size
        self.load_chunk_size = load_chunk_size
        self.state = state

    def run(self):
        logger.info("Start ETL for %s", self.extractor_class.TABLE_NAME)
        state_key = f"{self.extractor_class.TABLE_NAME}_updated_at"
        updated_at = self.state.get(state_key)

        extractor = self.extractor_class(self._pg_conn, self.extract_chunk_size, updated_at)
        data, last_updated_at = extractor.extract()

        if data:
            for table in TABLES:
                if data.get(table):
                    transformer = HANDLERS[f"{table}_transformer"]()
                    data[table] = transformer.transform(data[table])
                    loader = HANDLERS[f"{table}_loader"](HANDLERS[f"{table}_idx"], self.load_chunk_size)
                    loader.load(data[table])
                    if table == "film_work":
                        self.state.set(state_key, last_updated_at)
                logger.info(
                    "ETL for %s successfully finished.\nTotal: %d",
                    table,
                    len(data.get(table, [])),
                )
        else:
            logger.info("No changes in data for ETL")
