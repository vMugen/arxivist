import anyio

from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.ingestion import IngestionResponse

from app.services.metadata import fetch_metadata
from app.services.pdf_downloader import download_pdf
from app.services.extraction import extract_text
from app.services.chunker import chunk_text
from app.services.embedding import (
    LocalEmbeddingProvider,
    create_chunk_embeddings,
    MODEL_NAME,
)

from app.models.paper import Paper
from app.models.chunk import Chunk

from app.repositories.paper import (
    create_paper,
    get_paper_by_id,
)

from app.repositories.chunk import (
    create_chunks,
    get_chunks_for_paper,
)

from app.repositories.embedding import (
    create_embeddings,
    get_embeddings_for_chunks,
)
 

async def ingestion(
    session: AsyncSession,
    arxiv_id: str,
) -> IngestionResponse:

    async with session.begin():

        paper = await get_paper_by_id(
            session,
            arxiv_id,
        )

        if paper is not None:
            paper_id = paper.id

            chunks = await get_chunks_for_paper(
                session,
                paper_id,
            )
        else:
            paper_id = None
            chunks = []


    if paper is None:

        metadata = await anyio.to_thread.run_sync(
            fetch_metadata,
            arxiv_id,
        )

        pdf_path = await download_pdf(
            metadata.pdf_url,
            arxiv_id,
        )

        pages, text = await anyio.to_thread.run_sync(
            extract_text,
            pdf_path,
        )

        chunk_data = await anyio.to_thread.run_sync(
            chunk_text,
            text,
        )

        if not chunk_data:
            raise RuntimeError(
                f"Paper {arxiv_id} produced no chunks."
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
                for chunk in chunk_data
            ]

            await create_chunks(
                session,
                db_chunks,
            )

        chunks = db_chunks
        pages = pages
        extracted_text = text

    else:

        pages = 0
        extracted_text = ""


    if not chunks:
        raise RuntimeError(
            f"Paper {arxiv_id} has no chunks."
        )

    chunk_ids = [
        chunk.id
        for chunk in chunks
    ]

    async with session.begin():

        existing_embeddings = await get_embeddings_for_chunks(
            session,
            chunk_ids,
            MODEL_NAME,
        )


    existing_chunk_ids = {
        embedding.chunk_id
        for embedding in existing_embeddings
    }


    chunks_to_embed = [
        chunk
        for chunk in chunks
        if chunk.id not in existing_chunk_ids
    ]


    if chunks_to_embed:

        provider = LocalEmbeddingProvider(
            MODEL_NAME,
        )

        db_embeddings = await anyio.to_thread.run_sync(
            create_chunk_embeddings,
            chunks_to_embed,
            provider,
        )

        async with session.begin():

            await create_embeddings(
                session,
                db_embeddings,
            )


    return IngestionResponse(
        total_pages=pages,
        extracted_text_preview=extracted_text[:500],
        total_chunks=len(chunks),
    )