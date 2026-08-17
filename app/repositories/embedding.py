from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.embedding import Embedding


async def create_embedding(
        session: AsyncSession,
        embedding: Embedding,
) -> Embedding:
    session.add(embedding)
    await session.flush()

    return embedding

async def create_embeddings(
        session: AsyncSession,
        embeddings: list[Embedding]
) -> None:
    session.add_all(embeddings)
    await session.flush()


async def get_embeddings_for_chunks(
        session: AsyncSession,
        chunk_ids: list[int],
        model: str
) -> list[Embedding]:
    
    result = await session.execute(
        select(Embedding).where(
            Embedding.chunk_id.in_(chunk_ids),
            Embedding.model == model,
        )
    )

    return list(result.scalars().all())