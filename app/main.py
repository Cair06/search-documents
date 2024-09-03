import os.path
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import async_session_maker
from app.models import Document
from app.elastic import get_elasticsearch

import uvicorn

app = FastAPI()


@app.get("/search/")
async def search_documents(query: str):
    async with get_elasticsearch() as es:
        search_body = {"query": {"match": {"text": query}}, "size": 20}

        response = await es.search(index="documents", body=search_body)
        ids = [hit["_source"]["id"] for hit in response["hits"]["hits"]]

        if not ids:
            raise HTTPException(status_code=404, detail="No documents found")

        stmt = (
            select(Document)
            .where(Document.id.in_(ids))
            .order_by(Document.created_date.desc())
        )
        async with async_session_maker() as session:
            result = await session.execute(stmt)
        documents = result.scalars().all()

        return documents


@app.delete("/documents/{document_id}/")
async def delete_document(document_id: int):
    async with async_session_maker() as session:
        stmt = select(Document).where(Document.id == document_id)
        result = await session.execute(stmt)
        document = result.scalar_one_or_none()

        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        await session.delete(document)
        await session.commit()

        async with get_elasticsearch() as es:
            await es.delete(index="documents", id=document_id)

        return {"status": "deleted"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
