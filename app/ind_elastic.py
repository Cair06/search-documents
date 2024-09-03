import asyncio
from sqlalchemy.future import select
from .database import async_session_maker
from .models import Document
from .elasticsearch_my import get_elasticsearch


async def index_documents():

    async with async_session_maker() as session:
        stmt = select(Document)
        result = await session.execute(stmt)
        documents = result.scalars().all()

        for document in documents:
            doc_body = {
                "id": document.id,
                "text": document.text,
                "created_date": str(document.created_date),
            }
            async with get_elasticsearch() as es:
                await es.index(index="documents", id=document.id, document=doc_body)
                print("End successfully")


if __name__ == "__main__":
    asyncio.run(index_documents())
