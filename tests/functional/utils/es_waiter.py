import time
import settings
import elasticsearch

if __name__ == "__main__":
    client = elasticsearch.Elasticsearch(settings.settings.elastic_dsn)
    while True:
        if client.ping():
            break
        time.sleep(5)