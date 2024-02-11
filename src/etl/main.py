"""Startup file fot ETL pipeline"""
import json
import time

from core.config import settings
from core.logger import logger
from extractors.film_work import FilmWorkExtractor
from extractors.genre import GenreExtractor
from extractors.person import PersonExtractor
from managers import FilmWorkETLManager
from utils.connectors import elastic_connect, postgres_connect
from utils.state import JsonFileStorage, State

EXTRACTORS_DATA = (
    (FilmWorkExtractor, settings.FILM_WORK_CHUNK_SIZE),
    (GenreExtractor, settings.GENRE_CHUNK_SIZE),
    (PersonExtractor, settings.PERSON_CHUNK_SIZE),
)

indexes = settings.ELASTIC_INDEXES.split(",")


def main():
    while True:
        elk_conn = elastic_connect(settings.ELASTIC_DSN)
        for index in indexes:
            if not elk_conn.indices.exists(index=index):
                with open(f"es_schema/{index}.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                elk_conn.indices.create(index=index, body=data)
                logger.warning('Index "%s" was created', index)
        elk_conn.close()

        state: State = State(JsonFileStorage(settings.STATE_PATH))
        pg_conn = postgres_connect(settings.POSTGRES_DSN)
        try:
            for extractor_class, extractor_chunk_size in EXTRACTORS_DATA:
                etl_manager = FilmWorkETLManager(
                    pg_conn,
                    extractor_class,
                    extractor_chunk_size,
                    settings.LOAD_CHUNK_SIZE,
                    state,
                )
                etl_manager.run()
        except Exception as e:
            logger.exception(e)
            pg_conn.close()

        time.sleep(settings.SLEEP_TIME)


if __name__ == "__main__":
    main()
