import asyncio
import sys
import os
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import sys
import os
from datetime import date
from sqlalchemy.future import select
from app.main import app
from app.database import async_session_maker
from app.models import Document
from app.elastic import get_elasticsearch

import pytest
from httpx import ASGITransport, AsyncClient


# Фикстура для создания нового цикла событий для тестов
@pytest.fixture(scope="session")
def event_loop():
    """
    Создает новый цикл событий для каждого сеанса тестирования.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_search_documents():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/search/", params={"query": "тест"})
        assert response.status_code == 200
        assert (
            len(response.json()) <= 20
        )  # Проверяем, что возвращено не более 20 документов


@pytest.mark.asyncio
async def test_delete_document():
    # Шаг 1: Создаем документ в базе данных
    async with async_session_maker() as session:
        new_doc = Document(
            text="Документ для удаления",
            created_date=date(2024, 9, 3),
            rubrics=["тест"],
        )
        session.add(new_doc)
        await session.flush()
        doc_id = new_doc.id

        await session.commit()

    # Шаг 2: Индексируем документ в Elasticsearch вручную
    async with get_elasticsearch() as es:
        await es.index(
            index="documents",
            id=doc_id,
            document={
                "text": new_doc.text,
                "created_date": str(new_doc.created_date),
                "rubrics": new_doc.rubrics,
            },
        )

        doc_in_es = await es.exists(index="documents", id=doc_id)
        assert doc_in_es, "Документ не найден в Elasticsearch перед удалением."

    # Шаг 3: Удаляем документ через API
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        delete_response = await ac.delete(f"/documents/{doc_id}/")
        assert delete_response.status_code == 200

    # Шаг 4: Проверяем, что документ действительно удалён из базы
    async with async_session_maker() as session:
        stmt = select(Document).where(Document.id == doc_id)
        result = await session.execute(stmt)
        document = result.scalars().first()

        assert document is None

    # Шаг 5: Проверяем, что документ удалён из Elasticsearch
    async with get_elasticsearch() as es:
        doc_in_es_after_deletion = await es.exists(index="documents", id=doc_id)
        assert not doc_in_es_after_deletion, "Документ не был удален из Elasticsearch."
