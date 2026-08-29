from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.pdf_downloader import download_pdf


@pytest.mark.anyio
async def test_existing_pdf_returns_existing_path(tmp_path):
    existing_pdf = tmp_path / "2401.12345.pdf"
    existing_pdf.write_bytes(b"existing pdf")

    with patch(
        "app.services.pdf_downloader.DOWNLOAD_DIR",
        tmp_path,
    ), patch(
        "app.services.pdf_downloader.httpx.AsyncClient"
    ) as client_class:

        result = await download_pdf(
            "https://example.com/test.pdf",
            "2401.12345",
        )

    assert result == str(existing_pdf)
    client_class.assert_not_called()


@pytest.mark.anyio
async def test_successful_download_writes_pdf(tmp_path):
    response = MagicMock()
    response.content = b"%PDF-test-content"
    response.raise_for_status = MagicMock()

    client = MagicMock()
    client.get = AsyncMock(return_value=response)

    client_context = MagicMock()
    client_context.__aenter__ = AsyncMock(return_value=client)
    client_context.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.services.pdf_downloader.DOWNLOAD_DIR",
        tmp_path,
    ), patch(
        "app.services.pdf_downloader.httpx.AsyncClient",
        return_value=client_context,
    ):

        result = await download_pdf(
            "https://example.com/test.pdf",
            "2401.12345",
        )

    expected_path = tmp_path / "2401.12345.pdf"

    assert result == str(expected_path)
    assert expected_path.read_bytes() == b"%PDF-test-content"

    client.get.assert_awaited_once_with(
        "https://example.com/test.pdf",
        timeout=30.0,
        follow_redirects=True,
    )

    response.raise_for_status.assert_called_once()


@pytest.mark.anyio
async def test_http_status_error_raises_runtime_error(tmp_path):
    response = MagicMock()
    response.status_code = 404

    error = httpx.HTTPStatusError(
        "Not Found",
        request=MagicMock(),
        response=response,
    )

    response.raise_for_status.side_effect = error

    client = MagicMock()
    client.get = AsyncMock(return_value=response)

    client_context = MagicMock()
    client_context.__aenter__ = AsyncMock(return_value=client)
    client_context.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.services.pdf_downloader.DOWNLOAD_DIR",
        tmp_path,
    ), patch(
        "app.services.pdf_downloader.httpx.AsyncClient",
        return_value=client_context,
    ):

        with pytest.raises(
            RuntimeError,
            match="HTTP status error 404",
        ):
            await download_pdf(
                "https://example.com/test.pdf",
                "2401.12345",
            )


@pytest.mark.anyio
async def test_request_error_raises_runtime_error(tmp_path):
    error = httpx.RequestError(
        "Connection failed",
        request=MagicMock(),
    )

    client = MagicMock()
    client.get = AsyncMock(side_effect=error)

    client_context = MagicMock()
    client_context.__aenter__ = AsyncMock(return_value=client)
    client_context.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.services.pdf_downloader.DOWNLOAD_DIR",
        tmp_path,
    ), patch(
        "app.services.pdf_downloader.httpx.AsyncClient",
        return_value=client_context,
    ):

        with pytest.raises(
            RuntimeError,
            match="Network request error",
        ):
            await download_pdf(
                "https://example.com/test.pdf",
                "2401.12345",
            )