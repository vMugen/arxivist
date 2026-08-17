from pydantic import BaseModel

class EmbeddingData(BaseModel):
    chunk_id: int
    model: str
    dimension: int
    vector: list[float]