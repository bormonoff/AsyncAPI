from typing import Optional

import elasticsearch

es: Optional[elasticsearch.AsyncElasticsearch] = None


async def get_elastic() -> elasticsearch.AsyncElasticsearch:
    return es
