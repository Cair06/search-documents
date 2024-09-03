import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import os
import asyncio
from app.models import Document
from app.database import async_session_maker

csv_file_path = os.path.join(os.path.dirname(__file__), "..", "posts.csv")
csv_file_path = os.path.abspath(csv_file_path)

df = pd.read_csv(csv_file_path, delimiter=",", parse_dates=["created_date"])

# Преобразуем столбец "rubrics" из строки в список
df["rubrics"] = df["rubrics"].apply(lambda x: eval(x))


async def insert_documents():
    async with async_session_maker() as session:
        async with session.begin():
            for index, row in df.iterrows():
                document = Document(
                    text=row["text"],
                    created_date=row["created_date"],
                    rubrics=row["rubrics"],
                )
                session.add(document)


if __name__ == "__main__":
    asyncio.run(insert_documents())
