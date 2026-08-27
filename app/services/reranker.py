from sentence_transformers import CrossEncoder


RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"


class Reranker:

    def __init__(self, model_name: str):
        self.model = CrossEncoder(model_name)

    
    def rerank(
        self,
        query: str,
        documents: list[str],
    ):
        pairs = [
            [query, document]
            for document in documents
        ]

        scores = self.model.predict(pairs)

        return scores.tolist()