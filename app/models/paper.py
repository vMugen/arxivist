from datetime import datetime

from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.db import Base

class Paper(Base):
    __tablename__ = "papers"


    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    arxiv_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    authors: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    pdf_url: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
    )

    published: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="paper"
    )