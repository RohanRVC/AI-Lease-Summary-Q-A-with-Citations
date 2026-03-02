import os
from typing import List

from .prompts import SYSTEM_PROMPT, build_context_block


def _call_llm(context: str, question: str, model: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        return "Error: openai package not installed. Install with: pip install openai"
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Error: OPENAI_API_KEY not set. Set it in your environment to enable AI answers."
    client = OpenAI(api_key=api_key)
    user_content = f"""Use the following excerpts from the lease document to answer the question.

Rules:
- Always answer from the excerpts when they contain any relevant content. Do NOT say "do not contain this information" unless the excerpts are truly irrelevant.
- For "tenant name" or "landlord": extract and state any names that appear (e.g. after TENANT:, LANDLORD:).
- For "special provisions": describe exhibits, key articles, or notable clauses mentioned in the excerpts (e.g. Exhibit A–F, subordination, rules).
- For "what's in the document" / "tell me about the doc": summarize the lease from the excerpts—parties, term, rent, main articles, and key obligations.
- Give a direct, helpful answer and end with a single "Sources:" line listing the Page and Article/Section from the excerpts you used.

Document excerpts:
{context}

Question: {question}"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        return resp.choices[0].message.content or "No response."
    except Exception as e:
        return f"Error calling API: {e}"

                 #     Builds a Sources linee from chunk metadata.....
def _format_citations(chunks: List[dict]) -> str:
    seen = set()
    parts = []
    for c in chunks:
        page = c.get("page_number")
        art = c.get("article")
        sec = c.get("section")
        if page is None:
            continue
        ref = f"Page {page}"
        if art:
            ref += f", Article {art}"
        if sec:
            ref += f", Section {sec}"
        if ref not in seen:
            seen.add(ref)
            parts.append(ref)
    if not parts:
        return "Sources: (retrieved excerpts above)"
    return "Sources: " + "; ".join(parts)


def _strip_trailing_sources(text: str) -> str:
    """Remove trailing 'Sources: ...' line(s) from model output so we show one Sources line from retrieved chunks."""
    if not text or "Sources:" not in text:
        return text.strip()
    lines = text.strip().split("\n")
    while lines and ("Sources:" in (lines[-1] or "") or (lines[-1] or "").strip() == ""):
        lines.pop()
    return "\n".join(lines).strip()

    #     Generate an answer form retrieved chunks and return (answer_text, sources_line)...dc...
def answer_with_citations(
    chunks: List[dict],
    question: str,
    model: str | None = None,
) -> tuple[str, str]:
   
    from config import OPENAI_MODEL
    if model is None:
        model = OPENAI_MODEL
    context = build_context_block(chunks)
    answer = _call_llm(context, question, model)
    # One clear Sources line from retrieved chunks (strip model's duplicate/correct it)
    sources_line = _format_citations(chunks)
    answer_clean = _strip_trailing_sources(answer)
    if not answer_clean:
        answer_clean = answer.strip()
    return answer_clean, sources_line
