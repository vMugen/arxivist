import pymupdf

def extract_text(path: str) -> tuple[int, str]:
    with pymupdf.open(path) as doc:
        
        total_pages = len(doc)
        full_text = ""
        pages_text = []

        for page in doc:
            pages_text.append(page.get_text())

        full_text = "\n".join(pages_text)

    return total_pages, full_text