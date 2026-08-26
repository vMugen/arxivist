from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.services.ingestion import ingestion


@pytest.fixture
def session():
    session = AsyncMock()

    # AsyncSession.begin() returns an async context manager.
    transaction = AsyncMock()
    session.begin = MagicMock(return_value=transaction)

    return session


@pytest.fixture
def paper():
    return SimpleNamespace(
        id=1,
        arxiv_id="2401.12345",
        title="Test Paper",
        authors=["Alice", "Bob"],
        summary="Test summary",
        pdf_url="https://example.com/test.pdf",
        published=None,
    )


@pytest.fixture
def chunk():
    return SimpleNamespace(
        id=10,
        paper_id=1,
        chunk_index=0,
        start_char=0,
        end_char=100,
        text="This is a test chunk.",
    )


@pytest.mark.anyio
async def test_existing_paper_skips_ingestion_pipeline(
    session,
    paper,
    chunk,
):
    with (
        patch(
            "app.services.ingestion.get_paper_by_id",
            new=AsyncMock(return_value=paper),
        ) as get_paper,
        patch(
            "app.services.ingestion.get_chunks_for_paper",
            new=AsyncMock(return_value=[chunk]),
        ) as get_chunks,
        patch("app.services.ingestion.fetch_metadata") as fetch_metadata,
        patch("app.services.ingestion.download_pdf") as download_pdf,
        patch("app.services.ingestion.extract_text") as extract_text,
        patch("app.services.ingestion.chunk_text") as chunk_text,
        patch(
            "app.services.ingestion.get_embeddings_for_chunks",
            new=AsyncMock(return_value=[]),
        ),
        patch(
            "app.services.ingestion.create_chunk_embeddings",
            return_value=[],
        ),
        patch(
            "app.services.ingestion.create_embeddings",
            new=AsyncMock(),
        ),
    ):
        response = await ingestion(session, "2401.12345")

    get_paper.assert_awaited_once_with(
        session,
        "2401.12345",
    )

    get_chunks.assert_awaited_once_with(
        session,
        paper.id,
    )

    fetch_metadata.assert_not_called()
    download_pdf.assert_not_called()
    extract_text.assert_not_called()
    chunk_text.assert_not_called()

    assert response.total_pages == 0
    assert response.extracted_text_preview == ""
    assert response.total_chunks == 1


@pytest.mark.anyio
async def test_new_paper_runs_ingestion_pipeline(session):
    metadata = SimpleNamespace(
        arxiv_id="2401.12345",
        title="Test Paper",
        authors=["Alice"],
        summary="Test summary",
        pdf_url="https://example.com/test.pdf",
        published=None,
    )

    chunk_data = [
        SimpleNamespace(
            chunk_index=0,
            start_char=0,
            end_char=100,
            text="This is a test chunk.",
        )
    ]

    pages = 5
    extracted_text = "A" * 600

    with (
        patch(
            "app.services.ingestion.get_paper_by_id",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "app.services.ingestion.fetch_metadata",
            return_value=metadata,
        ) as fetch_metadata,
        patch(
            "app.services.ingestion.download_pdf",
            return_value="test.pdf",
        ) as download_pdf,
        patch(
            "app.services.ingestion.extract_text",
            return_value=(pages, extracted_text),
        ) as extract_text,
        patch(
            "app.services.ingestion.chunk_text",
            return_value=chunk_data,
        ) as chunk_text,
        patch(
            "app.services.ingestion.create_paper",
            new=AsyncMock(),
        ) as create_paper,
        patch(
            "app.services.ingestion.create_chunks",
            new=AsyncMock(),
        ) as create_chunks,
        patch(
            "app.services.ingestion.get_embeddings_for_chunks",
            new=AsyncMock(return_value=[]),
        ),
        patch(
            "app.services.ingestion.create_chunk_embeddings",
            return_value=[],
        ),
        patch(
            "app.services.ingestion.create_embeddings",
            new=AsyncMock(),
        ),
    ):

        async def assign_paper_id(session, paper):
            paper.id = 1

        create_paper.side_effect = assign_paper_id

        response = await ingestion(
            session,
            "2401.12345",
        )

    fetch_metadata.assert_called_once_with(
        "2401.12345",
    )

    download_pdf.assert_called_once_with(
        metadata.pdf_url,
        "2401.12345",
    )

    extract_text.assert_called_once_with(
        "test.pdf",
    )

    chunk_text.assert_called_once_with(
        extracted_text,
    )

    create_paper.assert_awaited_once()
    create_chunks.assert_awaited_once()

    assert response.total_pages == 5
    assert response.extracted_text_preview == extracted_text[:500]
    assert response.total_chunks == 1


@pytest.mark.anyio
async def test_new_paper_with_no_chunks_raises(session):
    metadata = SimpleNamespace(
        arxiv_id="2401.12345",
        title="Test Paper",
        authors=["Alice"],
        summary="Test summary",
        pdf_url="https://example.com/test.pdf",
        published=None,
    )

    with (
        patch(
            "app.services.ingestion.get_paper_by_id",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "app.services.ingestion.fetch_metadata",
            return_value=metadata,
        ),
        patch(
            "app.services.ingestion.download_pdf",
            return_value="test.pdf",
        ),
        patch(
            "app.services.ingestion.extract_text",
            return_value=(5, "Some text"),
        ),
        patch(
            "app.services.ingestion.chunk_text",
            return_value=[],
        ),
    ):
        with pytest.raises(
            RuntimeError,
            match="Paper 2401.12345 produced no chunks",
        ):
            await ingestion(
                session,
                "2401.12345",
            )


@pytest.mark.anyio
async def test_existing_embeddings_are_not_recreated(
    session,
    paper,
    chunk,
):
    existing_embedding = SimpleNamespace(
        chunk_id=chunk.id,
    )

    with (
        patch(
            "app.services.ingestion.get_paper_by_id",
            new=AsyncMock(return_value=paper),
        ),
        patch(
            "app.services.ingestion.get_chunks_for_paper",
            new=AsyncMock(return_value=[chunk]),
        ),
        patch(
            "app.services.ingestion.get_embeddings_for_chunks",
            new=AsyncMock(return_value=[existing_embedding]),
        ),
        patch(
            "app.services.ingestion.create_chunk_embeddings",
            return_value=[],
        ) as create_chunk_embeddings,
        patch(
            "app.services.ingestion.create_embeddings",
            new=AsyncMock(),
        ) as create_embeddings,
    ):
        response = await ingestion(
            session,
            "2401.12345",
        )

    create_chunk_embeddings.assert_not_called()
    create_embeddings.assert_not_awaited()

    assert response.total_pages == 0
    assert response.extracted_text_preview == ""
    assert response.total_chunks == 1