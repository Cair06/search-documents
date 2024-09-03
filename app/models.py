from sqlalchemy import (
    Computed,
    Integer,
    String,
    Date,
    ARRAY,
    Text,
    Index,
    text as sa_text,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from app.database import Base
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rubrics: Mapped[list[str]] = mapped_column(ARRAY(String))
    text: Mapped[str] = mapped_column(Text)
    created_date: Mapped[date] = mapped_column(Date)

    __table_args__ = (
        Index(
            "ix_documents_text_md5",
            sa_text("md5(text::text)"),
            postgresql_using="btree",
        ),
    )
