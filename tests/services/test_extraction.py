from unittest.mock import MagicMock, patch

from app.services.extraction import extract_text


def test_extract_text_returns_page_count_and_combined_text():
    page_one = MagicMock()
    page_one.get_text.return_value = "Page one"

    page_two = MagicMock()
    page_two.get_text.return_value = "Page two"

    document = MagicMock()
    document.__enter__.return_value = document
    document.__len__.return_value = 2
    document.__iter__.return_value = iter(
        [page_one, page_two]
    )

    with patch(
        "app.services.extraction.pymupdf.open",
        return_value=document,
    ) as pdf_open:
        pages, text = extract_text("paper.pdf")

    pdf_open.assert_called_once_with("paper.pdf")

    assert pages == 2
    assert text == "Page one\nPage two"


def test_extract_text_handles_empty_pdf():
    document = MagicMock()
    document.__enter__.return_value = document
    document.__len__.return_value = 0
    document.__iter__.return_value = iter([])

    with patch(
        "app.services.extraction.pymupdf.open",
        return_value=document,
    ):
        pages, text = extract_text("empty.pdf")

    assert pages == 0
    assert text == ""