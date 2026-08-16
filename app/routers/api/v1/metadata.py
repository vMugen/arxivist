import anyio
from fastapi import APIRouter, HTTPException, status
from app.schema.paper import PaperMetadata
from app.services.metadata import fetch_metadata

router = APIRouter(
    prefix="/papers",
    tags=["Metadata"],
)

@router.get("/{arxiv_id}", response_model=PaperMetadata)
async def get_paper(arxiv_id: str):
    try:
        metadata = await anyio.to_thread.run_sync(
            fetch_metadata, arxiv_id,
        )
        return metadata
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )