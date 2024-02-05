import logging

import elasticsearch
import fastapi
import uvicorn
from fastapi import responses
from redis import asyncio

from api.v1 import films, genres, persons
from core import config
from core.logger import LOGGING
from db import elastic, redis


app = fastapi.FastAPI(
    title=config.settings.PROJECT_NAME,
    docs_url="/docs/openapi",
    openapi_url="/docs/openapi.json",
    default_response_class=responses.ORJSONResponse,
    )


@app.on_event("startup")
async def startup():
    redis.redis = asyncio.Redis(host=config.settings.REDIS_HOST, port=config.settings.REDIS_PORT)
    elastic.es = elasticsearch.AsyncElasticsearch(config.settings.ELASTIC_DSN)



@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])

if __name__ == "__main__":
    # Use run function to debug an app. Otherwise,
    # launch the server using `uvicorn main:app --host 0.0.0.0 --port 8000`
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )