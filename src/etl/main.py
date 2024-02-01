import json
from time import sleep

import psycopg2

from utils.connectors import elastic_connect, postgres_connect
from utils.logger import logger
from utils.state import JsonFileStorage, State

from core.config import settings
from etl.extractors.film_work import FilmWorkExtractor
from etl.extractors.genre import GenreExtractor
from etl.extractors.person import PersonExtractor
from etl.managers import FilmWorkETLManager

from psycopg2.extras import RealDictCursor

EXTRACTORS_DATA = (
    (FilmWorkExtractor, settings.FILM_WORK_CHUNK_SIZE),
    (GenreExtractor, settings.GENRE_CHUNK_SIZE),
    (PersonExtractor, settings.PERSON_CHUNK_SIZE),
)

DSN = {
    'dbname': 'movies_database',
    'user': 'app',
    'password': '123qwe',
    'host': '127.0.0.1',
    'port':  5432,
    # 'options': '-c search_path=content',
}

indexes = settings.ELASTIC_INDEXES.split(',')


def main():
    while True:
        elk_conn = elastic_connect(settings.ELASTIC_DSN)
        for index in indexes:
            if not elk_conn.indices.exists(index=index):
                with open(f"es_schema/{index}.json", "r") as f:
                    data = json.load(f)
                elk_conn.indices.create(index=index, body=data)
                logger.warning('Index "%s" was created', index)
        elk_conn.close()

        state: State = State(JsonFileStorage(settings.STATE_PATH))
        # pg_conn = postgres_connect(settings.POSTGRES_DSN)
        pg_conn = psycopg2.connect(**DSN, cursor_factory=RealDictCursor)
        try:
            for extractor_class, extractor_chunk_size in EXTRACTORS_DATA:
                etl_manager = FilmWorkETLManager(
                    pg_conn,
                    extractor_class,
                    extractor_chunk_size,
                    settings.LOAD_CHUNK_SIZE,
                    indexes[0],
                    state,
                )
                etl_manager.run()
        except Exception as e:
            logger.exception(e)
            pg_conn.close()

        sleep(settings.SLEEP_TIME)


if __name__ == "__main__":
    main()
