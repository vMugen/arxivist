from fastapi import APIRouter
from app.routers.api.v1.ingestion import router as ingestion_router
from app.routers.api.v1.metadata import router as metadata_router
from app.routers.api.v1.retrieval import router as retrieval_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(metadata_router)
v1_router.include_router(ingestion_router)
v1_router.include_router(retrieval_router)