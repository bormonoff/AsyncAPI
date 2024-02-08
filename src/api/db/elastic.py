import elasticsearch

es: elasticsearch.AsyncElasticsearch | None = None


async def get_elastic() -> elasticsearch.AsyncElasticsearch:
    return es
