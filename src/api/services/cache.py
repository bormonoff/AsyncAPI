from typing import Optional

from models import film as film_model
from models import genre as genre_model
from models import person as person_model
from redis import asyncio

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 min

ENTITIES = {
    "base_film": film_model.FilmBase,
    "film": film_model.Film,
    "genre": genre_model.Genre,
    "person": person_model.Person,
}


class CacheService:
    def __init__(self, redis: asyncio.Redis):
        self.redis = redis

    async def put_list_to_cache(
        self,
        entity_name: str,
        field_to_filter: str,
        field_to_sort: str,
        page_size: int,
        page_number: int,
        entity_list: list[film_model.FilmBase | genre_model.Genre | person_model.Person]
    ) -> None:
        cache_key = f'{entity_name}s:filter_{field_to_filter}:sort_{field_to_sort}:{page_size}:{page_number}'
        await self.redis.rpush(cache_key, *[entity.model_dump_json(by_alias=True) for entity in entity_list])
        await self.redis.expire(cache_key, CACHE_EXPIRE_IN_SECONDS)

    async def get_list_from_cache(
        self,
        entity_name: str,
        field_to_filter: str,
        field_to_sort: str,
        page_size: int,
        page_number: int,
    ) -> Optional[list[film_model.Film | genre_model.Genre | person_model.Person]]:
        cache_key = f'{entity_name}s:filter_{field_to_filter}:sort_{field_to_sort}:{page_size}:{page_number}'
        data = await self.redis.lrange(cache_key, 0, page_size)
        if not data:
            return None
        result = [ENTITIES[entity_name].model_validate_json(el) for el in data]
        return result

    async def put_entity_to_cache(self, entity_name, entity: film_model.Film | genre_model.Genre | person_model.Person):
        await self.redis.set(f'{entity_name}:{entity.uuid}',
                             entity.model_dump_json(by_alias=True),
                             CACHE_EXPIRE_IN_SECONDS,
                             )

    async def get_entity_from_cache(
        self,
        entity_name: str,
        entity_id: str,
    ) -> Optional[film_model.Film | genre_model.Genre | person_model.Person]:
        data = await self.redis.get(f'{entity_name}:{entity_id}')
        if not data:
            return None
        entity = ENTITIES[entity_name].model_validate_json(data)
        return entity
