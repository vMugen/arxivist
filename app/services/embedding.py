from typing import Protocol

from sentence_transformers import SentenceTransformer

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