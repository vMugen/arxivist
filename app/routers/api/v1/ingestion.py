from typing import Annotated
from fastapi import (
    APIRouter, 
    HTTPException, 
    status, 
    Depends
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ingestion import ingestion
from app.schema.ingestion import IngestionResponse
from app.config.db import get_db

router = APIRouter(
    prefix="/papers",
    tags=["Ingestion"],
)

@router.post(
    "/{arxiv_id}/ingest", 
    response_model=IngestionResponse, 
    status_code=status.HTTP_200_OK,
)
async def ingest_paper(
        session: Annotated[AsyncSession, Depends(get_db)],
        arxiv_id: str
):
    try:
        response = await ingestion(
            session,
            arxiv_id
        )

        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong...",
        )