from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.paper import Paper

async def create_paper(
        session: AsyncSession,
        paper: Paper,
) -> Paper:

    session.add(paper)
    await session.flush()

    return paper

async def get_paper_by_id(
        session: AsyncSession,
        arxiv_id: str,
) -> Paper | None:
    result = await session.execute(
        select(Paper).where(
            Paper.arxiv_id == arxiv_id,
        )
    )

    return result.scalar_one_or_none()