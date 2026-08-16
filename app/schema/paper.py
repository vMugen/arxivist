from datetime import datetime
from pydantic import BaseModel

class PaperMetadata(BaseModel):
    arxiv_id: str
    title: str
    authors: list[str]
    summary: str
    pdf_url: str
    published: datetime