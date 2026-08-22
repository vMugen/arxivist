from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.embedding import Embedding


async def search_similar_chunks(
        session: AsyncSession,
        query_vector: list[float],
        model: str,
        top_k: int,
):
    distance = Embedding.vector.cosine_distance(query_vector)

    result = await session.execute(
        select(
            Chunk.id,
            Chunk.paper_id,
            Chunk.text,
            distance.label("distance"),
        )
        .join(
            Chunk,
            Embedding.chunk_id == Chunk.id,
        )
        .where(
            Embedding.model == model
        )
        .order_by(
            distance
        )
        .limit(
            top_k
        )
    )

    return result.all()