import redis

import settings
from utils.backoff import backoff


@backoff()
def redis_connect(host, port):
    connection = redis.Redis(host=host, port=port)
    if not connection.ping():
        raise ConnectionError("Can not connect to Elasticsearch")


if __name__ == '__main__':
    redis_connect(host=settings.settings.redis_host, port=settings.settings.redis_port)
