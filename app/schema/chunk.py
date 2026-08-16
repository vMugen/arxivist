from pydantic import BaseModel

class ChunkData(BaseModel):
    chunk_index: int
    start_char: int
    end_char: int
    text: str 