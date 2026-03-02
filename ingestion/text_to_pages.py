import re
from typing import List


    #     Parse pasted text into pages. ... .   
def pasted_text_to_pages(text: str) -> List[dict]:
    if not (text or "").strip():
        return []

    pattern = re.compile(
        r"(?:^|\n)\s*(?:--\s*)?(\d+)\s+of\s+(\d+)(?:\s*--)?\s*(?=\n|$)",
        re.IGNORECASE | re.MULTILINE,
    )
    parts = pattern.split(text)
    if len(parts) <= 1:
        return [{"page_number": 1, "text": text.strip()}]

    pages = []
    if parts[0].strip():
        pages.append({"page_number": 1, "text": parts[0].strip()})
    i = 1
    while i + 2 < len(parts):
        page_num = int(parts[i])
        _total = parts[i + 1]
        block = parts[i + 2].strip() if (i + 2) < len(parts) else ""
        if block:
            pages.append({"page_number": page_num, "text": block})
        i += 3
    if not pages:
        return [{"page_number": 1, "text": text.strip()}]
    return pages
