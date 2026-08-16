"""
✅ Metadata Retrieval
✅ PDF Download
✅ PDF Extraction
✅ Text Chunking Pipeline   ← Current milestone
✅ Separate in routers, etc
⬜ Define DB models and Pydantic schema properly and setup sqlalchemy async session.
⬜ PostgreSQL Persistence + pg vector setup for embeddings
⬜ Embeddings
⬜ Semantic Retrieval
⬜ Research Intelligence
⬜ Background Processing
⬜ Research Operating System
"""

from fastapi import FastAPI
from app.routers.api.v1 import v1_router


app = FastAPI(
    title="ArXivist API Engine",
    version="0.1.0",
    description="Ingestion Gateway for arXiv papers",
)

app.include_router(v1_router)

@app.get("/")
async def root():
    return {"message": "ArXivist API Engine is operational..."}