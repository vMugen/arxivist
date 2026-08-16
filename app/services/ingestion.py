import anyio
from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.ingestion import IngestionResponse
from app.services.metadata import fetch_metadata
from app.services.pdf_downloader import download_pdf
from app.services.extraction import extract_text
from app.services.chunker import chunk_text
from app.models.paper import Paper
from app.models.chunk import Chunk
from app.repositories.paper import create_paper, get_paper_by_id
from app.repositories.chunk import (
    create_chunks,
    count_chunks_for_paper,
)

async def ingestion(
        session: AsyncSession,
        arxiv_id: str,
):
    existing_paper = await get_paper_by_id(
        session,
        arxiv_id,
    )

    if existing_paper is not None:
        chunk_count = await count_chunks_for_paper(
            session,
            existing_paper.id,
        )

        return IngestionResponse(
            total_pages=0,
            extracted_text_preview="",
            total_chunks=chunk_count,
        )

    await session.rollback()
    
    metadata = await anyio.to_thread.run_sync(
        fetch_metadata, arxiv_id
    )

    pdf_path = await anyio.to_thread.run_sync(
        download_pdf,
        metadata.pdf_url,
        arxiv_id,
    )

    pages, text = await anyio.to_thread.run_sync(
        extract_text,
        pdf_path,
    )

    chunks = await anyio.to_thread.run_sync(
        chunk_text,
        text
    )

    async with session.begin():
        paper = Paper(
                arxiv_id=metadata.arxiv_id,
                title=metadata.title,
                authors=metadata.authors,
                summary=metadata.summary,
                pdf_url=metadata.pdf_url,
                published=metadata.published,
            )
    
        await create_paper(
            session,
            paper,
        )

        db_chunks = [
            Chunk(
                paper_id=paper.id,
                chunk_index=chunk.chunk_index,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                text=chunk.text,
            )
            for chunk in chunks
        ]

        await create_chunks(
            session,
            db_chunks,
        )

    return IngestionResponse(
        total_pages=pages,
        extracted_text_preview=text[:500],
        total_chunks=len(chunks)
    )
