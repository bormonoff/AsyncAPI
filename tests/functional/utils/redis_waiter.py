import time

import settings
from redis import asyncio

if __name__ == '__main__':
    redis = asyncio.Redis(host=settings.settings.redis_host, port=settings.settings.redis_port)
    while True:
        if redis.ping():
            break
        time.sleep(1)