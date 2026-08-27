import arxiv
from app.schema.paper import PaperMetadata

def fetch_metadata(arxiv_id: str) -> PaperMetadata:
    client = arxiv.Client(
        delay_seconds=3.0,
        num_retries=3,
    )
    search = arxiv.Search(
        id_list=[arxiv_id]
    )

    try:
        paper = next(client.results(search))
    except StopIteration:
        raise ValueError(f"Paper with arXiv ID '{arxiv_id}' not found.")

    return PaperMetadata(
        arxiv_id=arxiv_id,
        title=paper.title,
        authors=[a.name for a in paper.authors],
        summary=paper.summary,
        pdf_url=paper.pdf_url,
        published=paper.published
    )