from app.schema.chunk import ChunkData

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 100,
) -> list[ChunkData]:

    if chunk_size <= overlap:
        raise ValueError(
            "chunk_size must be strictly greater than overlap."
        )

    chunks = []

    start = 0
    text_length = len(text)
    step = chunk_size - overlap

    while start < text_length:
        end = min(start + chunk_size, text_length)

        chunk = text[start:end]

        if chunk:
            chunks.append(
                ChunkData(
                    chunk_index=len(chunks),
                    start_char=start,
                    end_char=end,
                    text=chunk,
                )
            )

        start += step

    return chunks