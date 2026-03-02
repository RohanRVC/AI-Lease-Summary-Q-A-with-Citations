"""
Prompts for citation-aware Q&A over the lease document.
"""
SYSTEM_PROMPT = """You are a helpful assistant that answers questions about a commercial lease document using ONLY the provided excerpts.
- Always give a helpful answer from the excerpts when they contain any relevant information. Extract names, dates, amounts, and terms that appear in the excerpts.
- For broad questions (e.g. "what's in the document", "tell me about the doc", "special provisions", "tenant name"), summarize what the excerpts say: key parties, main topics, exhibits, articles, or clauses mentioned.
- Only say "The document excerpts provided do not contain this information" when the excerpts are clearly irrelevant to the question (e.g. question is about something not mentioned at all in the excerpts).
- Do not refuse to answer when the excerpts mention related content—instead summarize or extract from what is there. Prefer a partial or inferred answer over refusing.
- Cite sources (Page X, Article Y, Section Z) and end with a "Sources:" line listing the excerpt locations you used."""


def citation_instruction() -> str:
    return "Always end your response with a 'Sources:' line listing the document locations (Page and, when available, Article or Section) for the information you used."


    #     Format retrieved chunks as a single context string with labels for citation.....
def build_context_block(chunks: list[dict]) -> str:
    lines = []
    for i, c in enumerate(chunks, 1):
        page = c.get("page_number", "?")
        art = c.get("article", "")
        sec = c.get("section", "")
        ref = f"Page {page}"
        if art:
            ref += f", Article {art}"
        if sec:
            ref += f", Section {sec}"
        lines.append(f"[Excerpt {i} - {ref}]\n{c.get('text', '')}")
    return "\n\n---\n\n".join(lines)
