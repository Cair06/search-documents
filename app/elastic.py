from elasticsearch import AsyncElasticsearch
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_elasticsearch():
    es = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])
    try:
        yield es
    finally:
        await es.close()
