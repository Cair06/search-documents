from elasticsearch import AsyncElasticsearch
from contextlib import asynccontextmanager
from app.config import settings


@asynccontextmanager
async def get_elasticsearch():
    es = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])
    try:
        yield es
    finally:
        await es.close()
