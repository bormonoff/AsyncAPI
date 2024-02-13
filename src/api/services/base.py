from db.search_engine import AsyncSearchEngine


class BaseService:
    def __init__(self, search_engine: AsyncSearchEngine):
        self.search_engine = search_engine

    async def get_by_id(self, index: str, _id: str) -> dict | None:
        obj = await self.search_engine.get_by_id(index, _id)
        return obj

    async def search(
        self, index: str, query: dict, page_size: int | None = None, page_number: int = 1
    ) -> list[dict] | None:
        obj_list = await self.search_engine.search(index, query, page_size, page_number)
        return obj_list
