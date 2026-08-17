from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.db import Base

class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    chunk_id: Mapped[int] = mapped_column(
        ForeignKey("chunks.id"),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    dimensions: Mapped[int] = mapped_column(
        nullable=False,
    )

    vector: Mapped[list[float]] = mapped_column(
        Vector(384),
        nullable=False,
    )

    chunk: Mapped["Chunk"] = relationship(
        back_populates="embeddings",
    )

    __table_args__ = (
        UniqueConstraint(
            "chunk_id",
            "model",
            name="uq_embedding_chunk_model",
        ),
    )