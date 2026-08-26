import pytest

from app.services.chunker import chunk_text


def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []


def test_text_shorter_than_chunk_size_returns_one_chunk():
    chunks = chunk_text(
        "abcdefgh",
        chunk_size=10,
        overlap=2,
    )

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].start_char == 0
    assert chunks[0].end_char == 8
    assert chunks[0].text == "abcdefgh"


def test_overlap_preserves_expected_boundaries():
    chunks = chunk_text(
        "abcdefghij",
        chunk_size=6,
        overlap=2,
    )

    assert [chunk.text for chunk in chunks] == [
        "abcdef",
        "efghij",
        "ij",
    ]

    assert [
        (chunk.start_char, chunk.end_char)
        for chunk in chunks
    ] == [
        (0, 6),
        (4, 10),
        (8, 10),
    ]

    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]


def test_invalid_chunk_configuration_raises():

    with pytest.raises(ValueError):
        chunk_text(
            "abcdef",
            chunk_size=4,
            overlap=4,
        )

    with pytest.raises(ValueError):
        chunk_text(
            "abcdef",
            chunk_size=4,
            overlap=5,
        )