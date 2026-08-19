from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.db import get_db
from app.schema.retrieval import RetrievedChunk
from app.services.retrieval import retrieve_chunks


router = APIRouter(
    prefix="/retrieval",
    tags=["Retrieval"],
)


@router.get(
    "/search",
    response_model=list[RetrievedChunk]
)
async def search_chunks(
    query: str,
    top_k: int,
    session: Annotated[AsyncSession, Depends(get_db)] = None,
):
    return await retrieve_chunks(
        session=session,
        query=query,
        top_k=top_k,
    )