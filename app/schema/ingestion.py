from pydantic import BaseModel, Field

class IngestionResponse(BaseModel):
    total_pages: int
    extracted_text_preview: str = Field(max_length=500)
    total_chunks: int