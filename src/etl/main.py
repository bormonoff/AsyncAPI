"""Startup file fot ETL pipeline"""
import json
import time

from core import config

from etl.extractors.film_work import FilmWorkExtractor
from etl.extractors.genre import GenreExtractor
from etl.extractors.person import PersonExtractor
from etl.managers import FilmWorkETLManager
from etl.utils import logger as etl_logger
from etl.utils.connectors import elastic_connect, postgres_connect
from etl.utils.state import JsonFileStorage, State

EXTRACTORS_DATA = (
    (FilmWorkExtractor, config.settings.FILM_WORK_CHUNK_SIZE),
    (GenreExtractor, config.settings.GENRE_CHUNK_SIZE),
    (PersonExtractor, config.settings.PERSON_CHUNK_SIZE),
)

indexes = config.settings.ELASTIC_INDEXES.split(",")


def main():
    while True:
        elk_conn = elastic_connect(config.settings.ELASTIC_DSN)
        for index in indexes:
            if not elk_conn.indices.exists(index=index):
                with open(f"es_schema/{index}.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                elk_conn.indices.create(index=index, body=data)
                etl_logger.logger.warning('Index "%s" was created', index)
        elk_conn.close()

        state: State = State(JsonFileStorage(config.settings.STATE_PATH))
        pg_conn = postgres_connect(config.settings.POSTGRES_DSN)
        try:
            for extractor_class, extractor_chunk_size in EXTRACTORS_DATA:
                etl_manager = FilmWorkETLManager(
                    pg_conn,
                    extractor_class,
                    extractor_chunk_size,
                    config.settings.LOAD_CHUNK_SIZE,
                    state,
                )
                etl_manager.run()
        except Exception as e:
            etl_logger.logger.exception(e)
            pg_conn.close()

        time.sleep(config.settings.SLEEP_TIME)


if __name__ == "__main__":
    main()
