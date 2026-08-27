from pathlib import Path
import httpx

DOWNLOAD_DIR = Path("./downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def download_pdf(
        pdf_url: str,
        arxiv_id: str,
) -> str:
    pdf_filename = f"{arxiv_id.replace('/', '_')}.pdf"
    pdf_path = DOWNLOAD_DIR / pdf_filename

    if pdf_path.exists():
        return str(pdf_path)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                pdf_url,
                timeout=30.0,
                follow_redirects=True,
            )

            response.raise_for_status()

            pdf_path.write_bytes(response.content)

        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"HTTP status error {e.response.status_code} while fetching {pdf_url}"
            ) from e
        except httpx.RequestError as e:
            raise RuntimeError(
                f"Network request error while fetching {pdf_url}: {e}"
            ) from e

    return str(pdf_path)
        

