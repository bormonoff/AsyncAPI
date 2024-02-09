import pytest_asyncio
import elasticsearch
from elasticsearch import helpers
import asyncio
import settings
import os
import json
import uuid

@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name='es_create_idxs')
def create_es_indices():
    client = elasticsearch.Elasticsearch(settings.settings.elastic_dsn)
    indexes = settings.settings.elastic_indexes.split(",")
    for idx in indexes:
        with open(f"{os.path.dirname(__file__)}/testdata/{idx}.json", "r") as f:
            idx_body = json.load(f)
            if client.indices.exists(index=idx):
                client.indices.delete(index=idx)
            client.indices.create(index=idx, body=idx_body)
    client.close()

@pytest_asyncio.fixture(name='fill_movies')
def fill_movies():
    client = elasticsearch.Elasticsearch(settings.settings.elastic_dsn)
    data = list()
    for i in range(50):
        film_body = {
            "id": str(uuid.uuid4()),
            "imdb_rating": 8.9,
            "title": "The star",
            "description": "A film about a star",
            "type": "movie",
            "genres_names": ["action", "drama"],
            "directors_names": ["Angela Turner"],
            "actors_names": ["Gilby Clarke", "Barbara Church"],
            "writers_names": ["Bernard Baur"],
            "genres": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "action"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "drama"
                }
            ],
            "directors": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Angela Turner"
                }
            ],
            "actors": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Gilby Clarke"
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Barbara Church"
                }
            ],
            "writers": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Bernard Baur"
                },
            ]
        }

        film_doc = {
            "_index": "movies",
            "_id": film_body["id"],
            "_source": film_body
        }
        data.append(film_doc)
    helpers.bulk(client, data)

@pytest_asyncio.fixture(name='es_create_idxs')
def init_es_db(create_es_indices, fill_movies):
    print("a")
    pass
