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


def test_text_equal_to_chunk_size_returns_one_chunk():
    text = "abcdefghij"

    chunks = chunk_text(
        text,
        chunk_size=10,
        overlap=2,
    )

    assert len(chunks) == 1
    assert chunks[0].text == text
    assert chunks[0].start_char == 0
    assert chunks[0].end_char == 10


def test_text_just_over_chunk_size_creates_next_chunk():
    text = "abcdefghijk"

    chunks = chunk_text(
        text,
        chunk_size=10,
        overlap=2,
    )

    assert [chunk.text for chunk in chunks] == [
        "abcdefghij",
        "ijk",
    ]

    assert [
        (chunk.start_char, chunk.end_char)
        for chunk in chunks
    ] == [
        (0, 10),
        (8, 11),
    ]


def test_overlap_preserves_expected_boundaries():
    chunks = chunk_text(
        "abcdefghij",
        chunk_size=6,
        overlap=2,
    )

    assert [chunk.text for chunk in chunks] == [
        "abcdef",
        "efghij",
    ]

    assert [
        (chunk.start_char, chunk.end_char)
        for chunk in chunks
    ] == [
        (0, 6),
        (4, 10),
    ]

    assert [chunk.chunk_index for chunk in chunks] == [0, 1]


def test_zero_overlap_creates_non_overlapping_chunks():
    chunks = chunk_text(
        "abcdefghij",
        chunk_size=5,
        overlap=0,
    )

    assert [chunk.text for chunk in chunks] == [
        "abcde",
        "fghij",
    ]


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [
        (4, 4),
        (4, 5),
        (0, 0),
        (-1, 0),
    ],
)
def test_invalid_chunk_configuration_raises(
    chunk_size,
    overlap,
):
    with pytest.raises(ValueError):
        chunk_text(
            "abcdef",
            chunk_size=chunk_size,
            overlap=overlap,
        )