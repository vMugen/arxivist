from pathlib import Path
import httpx


DOWNLOAD_DIR = Path("./downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def download_pdf(pdf_url: str, arxiv_id: str) -> str:
    pdf_filename = f"{arxiv_id.replace('/', '_')}.pdf"
    pdf_path = DOWNLOAD_DIR / pdf_filename

    if not pdf_path.exists():
        response = httpx.get(
            pdf_url, 
            timeout=30.0,
            follow_redirects=True,
        )
        if response.status_code == 200:
            pdf_path.write_bytes(response.content)
        else:
            raise RuntimeError(f"Failed to download PDF from {pdf_url}")

    return str(pdf_path)