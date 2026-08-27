from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.retrieval import search_similar_chunks
from app.schema.retrieval import RetrievedChunk
from app.services.embedding import LocalEmbeddingProvider

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

embedding_provider = LocalEmbeddingProvider(model_name=EMBEDDING_MODEL)

async def retrieve_chunks(
        session: AsyncSession,
        query: str,
        top9_k: int = 5,
) -> list[RetrievedChunk]:

    query_vector = embedding_provider.embed(
        [query]
    )[0]
 
    results = await search_similar_chunks(
        session=session,
        query_vector=query_vector,
        model=EMBEDDING_MODEL,
        top_k=top_k
    )

    return [
        RetrievedChunk(
            chunk_id=row.id,
            paper_id=row.paper_id,
            text=row.text,
            score= 1 - row.distance,
        )
        for row in results
    ]