from pydantic import BaseModel


class RetrievalRequest(BaseModel):
    query: str
    top_k: int = 5


class RetrievedChunk(BaseModel):
    chunk_id: int
    paper_id: int
    text: str
    score: float