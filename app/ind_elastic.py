import asyncio
import warnings
from elasticsearch import ElasticsearchWarning
from sqlalchemy.future import select
from tqdm import tqdm
from .elastic import get_elasticsearch
from .database import async_session_maker
from .models import Document

# Отключаем предупреждения Elasticsearch
warnings.filterwarnings("ignore", category=ElasticsearchWarning)


async def index_documents():
    async with async_session_maker() as session:
        stmt = select(Document)
        result = await session.execute(stmt)
        documents = result.scalars().all()

        total_documents = len(documents)
        print(f"\nFound {total_documents} documents. Starting indexing...\n")

        with tqdm(total=total_documents, desc="Indexing Documents") as pbar:
            async with get_elasticsearch() as es:
                for document in documents:
                    doc_body = {
                        "id": document.id,
                        "text": document.text,
                        "created_date": str(document.created_date),
                    }
                    await es.index(index="documents", id=document.id, document=doc_body)
                    pbar.update(1)  # Обновляем прогресс-бар на один шаг

        print("\nIndexing completed!")


if __name__ == "__main__":
    asyncio.run(index_documents())
