import json
import os
import time

import elasticsearch
import pytest_asyncio
import settings
from elasticsearch import helpers


@pytest_asyncio.fixture(scope="module")
def create_es_indices():
    """Creates elastic indices using jsons stored in the testdata folder."""
    client = elasticsearch.Elasticsearch(settings.settings.elastic_dsn)
    indexes = settings.settings.elastic_indexes.split(",")
    for idx in indexes:
        with open(f"{os.path.dirname(__file__)}/testdata/indices/{idx}.json", "r") as f:
            idx_body = json.load(f)
            if client.indices.exists(index=idx):
                client.indices.delete(index=idx)
            client.indices.create(index=idx, body=idx_body)
    client.close()


@pytest_asyncio.fixture(scope="module")
def fill_elastic(create_es_indices):
    """Fills movie index using the data from the testdata/filler/movies_data.json."""
    client = elasticsearch.Elasticsearch(settings.settings.elastic_dsn)
    for index in ('movies', 'genres', "persons"):
        with open(f"{os.path.dirname(__file__)}/testdata/filler/{index}_data.json", "r") as file:
            data = json.load(file)
        helpers.bulk(client, data)

    # Sleep is needed to let an API reconnect to the elasticsearch indices.
    # Otherwise API will return 404 for the first tests
    time.sleep(1)
