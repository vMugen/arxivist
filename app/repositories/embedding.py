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