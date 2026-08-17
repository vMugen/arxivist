from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk

async def create_chunks(
        session: AsyncSession,
        chunks: list[Chunk],
) -> None:
    session.add_all(chunks)
    await session.flush()


async def count_chunks_for_paper(
        session: AsyncSession,
        paper_id: int,
) -> int:
    result = await session.execute(
        select(
            func.count(Chunk.id)
        ).where(
            Chunk.paper_id == paper_id
        )
    )

    return result.scalar_one()


async def get_chunks_for_paper(
    session: AsyncSession,
    paper_id: int,
) -> list[Chunk]:
    result = await session.execute(
        select(Chunk).where(
            Chunk.paper_id == paper_id
        )
    )

    return list(result.scalars().all())
    