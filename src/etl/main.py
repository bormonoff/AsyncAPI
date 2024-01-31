import json
from time import sleep

from utils.connectors import elastic_connect, postgres_connect
from utils.logger import logger
from utils.state import JsonFileStorage, State

from core.config import settings
from etl.extractors.film_work import FilmWorkExtractor
from etl.extractors.genre import GenreExtractor
from etl.extractors.person import PersonExtractor
from etl.managers import FilmWorkETLManager

EXTRACTORS_DATA = (
    (FilmWorkExtractor, settings.FILM_WORK_CHUNK_SIZE),
    (GenreExtractor, settings.GENRE_CHUNK_SIZE),
    (PersonExtractor, settings.PERSON_CHUNK_SIZE),
)


def main():
    while True:
        elk_conn = elastic_connect(settings.ELASTIC_DSN)
        if not elk_conn.indices.exists(index=settings.ELASTIC_INDEX):
            with open("es_schema.json", "r") as f:
                data = json.load(f)
            elk_conn.indices.create(index=settings.ELASTIC_INDEX, body=data)
            logger.warning('Index "%s" was created', settings.ELASTIC_INDEX)
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
                    settings.ELASTIC_INDEX,
                    state,
                )
                etl_manager.run()
        except Exception as e:
            logger.exception(e)
            pg_conn.close()

        sleep(settings.SLEEP_TIME)


if __name__ == "__main__":
    main()
