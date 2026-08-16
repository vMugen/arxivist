from sqlalchemy import ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.db import Base

class Chunk(Base):
    __tablename__ = "chunks"

    __table_args__ = (
        UniqueConstraint(
            "paper_id",
            "chunk_index",
            name="uq_chunk_paper_index",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        nullable=False,

    )

    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.id"),
    )

    chunk_index: Mapped[int] = mapped_column(
        nullable=False
    )

    start_char: Mapped[int] = mapped_column(
        nullable=False
    )

    end_char: Mapped[int] = mapped_column(
        nullable=False
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    paper: Mapped["Paper"] = relationship(
        back_populates="chunks"
    )