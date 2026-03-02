import re
from typing import List

from config import CHUNK_SIZE, CHUNK_OVERLAP


def _parse_page_marker(text: str) -> int | None:
    m = re.search(r"(?:--\s*)?(\d+)\s+of\s+\d+(?:\s*--)?", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"page\s+(\d+)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def _parse_article_section(text: str) -> tuple[str | None, str | None]:
    article = None
    section = None
    for m in re.finditer(r"ARTICLE\s+(\d+(?:\.\d+)?)[.\s:]", text, re.IGNORECASE):
        article = m.group(1)
    for m in re.finditer(r"SECTION\s+(\d+(?:\.\d+)?)[.\s]", text, re.IGNORECASE):
        section = m.group(1)
    return article, section


def _split_into_chunks(text: str, chunk_size: int, overlap: int) -> List[str]:
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # Try to break at sentence or newline
        if end < len(text):
            for sep in (". ", "\n\n", "\n", " "):
                last = chunk.rfind(sep)
                if last > chunk_size // 2:
                    chunk = chunk[: last + len(sep)]
                    end = start + len(chunk)
                    break
        chunks.append(chunk.strip())
        start = end - overlap
        if start >= len(text):
            break
    return chunks


def chunk_document(pages: List[dict], chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[dict]:
    result = []
    for page in pages:
        page_num = page["page_number"]
        text = page.get("text", "")
        if not text.strip():
            continue
        # Prefer page marker from content if present
        page_from_text = _parse_page_marker(text)
        use_page = page_from_text if page_from_text is not None else page_num
        sub_chunks = _split_into_chunks(text, chunk_size, overlap)
        running_text = ""
        for i, chunk_text in enumerate(sub_chunks):
            running_text += " " + chunk_text if running_text else chunk_text
            article, section = _parse_article_section(running_text)
            result.append({
                "text": chunk_text,
                "page_number": use_page,
                "article": article,
                "section": section,
            })
    return result
