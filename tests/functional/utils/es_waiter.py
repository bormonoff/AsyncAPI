import time

import elasticsearch
import settings

if __name__ == "__main__":
    client = elasticsearch.Elasticsearch(settings.settings.elastic_dsn)
    while True:
        if client.ping():
            break
        time.sleep(5)