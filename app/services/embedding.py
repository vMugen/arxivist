from typing import Protocol

from sentence_transformers import SentenceTransformer

from app.models.chunk import Chunk
from app.models.embedding import Embedding


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingProvider(Protocol):

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        ...


class LocalEmbeddingProvider:

    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def get_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()


def create_chunk_embeddings(
    chunks: list[Chunk],
    provider: EmbeddingProvider,
) -> list[Embedding]:

    texts = [chunk.text for chunk in chunks]

    vectors = provider.embed(texts)

    if len(vectors) != len(chunks):
        raise RuntimeError(
            "Number of embeddings does not match number of chunks."
        )

    dimension = provider.get_dimension()

    return [
        Embedding(
            chunk_id=chunk.id,
            model=MODEL_NAME,
            dimensions=dimension,
            vector=vector,
        )
        for chunk, vector in zip(chunks, vectors)
    ]