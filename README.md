# Lease Chat App — AI-Powered Chat with Source Citation

Document-aware AI chat: upload a lease PDF, view a structured summary, and ask questions with answers tied to document sources (page and section).
<img width="1919" height="979" alt="image" src="https://github.com/user-attachments/assets/69e3521e-0c39-433b-80e0-20b46a6a79b8" />
<img width="1919" height="981" alt="image" src="https://github.com/user-attachments/assets/0ce63b37-90ea-4650-bd03-731adaee4d2d" />

## Quick start

1. **Install dependencies** (from repo root or from `lease_chat_app`):

   ```bash
   pip install -r lease_chat_app/requirements.txt
   ```

2. **Run the app:**

   ```bash
   streamlit run lease_chat_app/app.py
   ```

   Or from inside `lease_chat_app`:

   ```bash
   cd lease_chat_app
   pip install -r requirements.txt
   streamlit run app.py
   ```

3. **Optional — AI extraction and answers:** Add your OpenAI API key so extraction and chat use the LLM. Either:

   - **Using .env (recommended):** Copy `lease_chat_app/.env.example` to `lease_chat_app/.env`, then open `.env` and paste your key after `OPENAI_API_KEY=` (no quotes).
   - **Or set in terminal:** `set OPENAI_API_KEY=sk-...` (Windows) before running the app.

   Without a key, the app still runs: extraction uses rule-based parsing, and chat will show a message asking you to set the key for AI answers.

## Scanned PDFs (OCR)

The app supports **both digital and scanned PDFs**. When you upload a PDF:

- Pages with embedded text are read directly.
- Pages with little or no text (e.g. scanned images) are run through **OCR** (Tesseract) automatically so they can be summarized and queried.

**For OCR to work**, install Tesseract on your machine and ensure it’s on your PATH:

- **Windows:** Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki) and add the install folder to PATH.
- **macOS:** `brew install tesseract`
- **Linux:** `sudo apt install tesseract-ocr` (or equivalent).

If Tesseract is not installed, the app still works for digital PDFs; scanned pages will have no text unless you add an OCR API (e.g. Google Cloud Vision) later.

## Deploying live (Vercel vs Streamlit)

- **Streamlit does not run on Vercel.** Vercel is for Node/Next.js (or serverless functions with strict limits). This app is a Streamlit Python app.
- **Recommended for going live:** Use **[Streamlit Community Cloud](https://share.streamlit.io)** (free): connect your GitHub repo, set `lease_chat_app/app.py` as the main file, add `OPENAI_API_KEY` in Secrets, and deploy. OCR (Tesseract) is not available on Streamlit Cloud; only digital PDFs will have full text unless you switch to an OCR API.
- **Alternative:** Deploy on **Railway**, **Render**, or **Fly.io** (all support Python and can install Tesseract for scanned PDFs). Set `OPENAI_API_KEY` in the environment.
- If you need **Vercel**: you’d build a separate front (e.g. Next.js) that talks to a Python backend hosted elsewhere (e.g. Railway) that runs this same logic.

## Project layout

- `app.py` — Streamlit entrypoint.
- `config.py` — Chunk size, embedding model, top-k, LLM model.
- `ingestion/` — PDF load and chunking (page/section metadata).
- `extraction/` — Lease summary schema and extractor (LLM or rule-based).
- `retrieval/` — Embeddings, FAISS store, retriever.
- `chat/` — Prompts and QA chain with citations.
- `ui/` — Summary display and chat UI.

## Pipeline overview and assumptions

**Flow:** PDF or pasted text → **Ingestion** (load, optional OCR for scanned pages, chunk by page/section with metadata) → **Extraction** (LLM or rule-based fill of lease summary schema) and **Retrieval** (embed chunks, build FAISS index) → **Chat** (user question → top-k retrieval → LLM answer with "Page X, Section Y" citations).

- **Single document:** One lease at a time; no multi-document comparison.
- **No auth:** App is open to whoever runs it; no user accounts or API keys required for rule-based mode.
- **LLM optional:** With `OPENAI_API_KEY`, extraction and chat use the configured model (e.g. gpt-4o-mini); without it, extraction uses regex/rule-based parsing and chat prompts for a key.
- **Embeddings:** Local sentence-transformers (`all-MiniLM-L6-v2`) for retrieval; no extra API for embeddings.
- **OCR:** Tesseract must be on PATH for scanned PDFs; if missing, only digital PDFs (or pasted text) have full text.

## Edge case analysis

The system is designed to handle:

| Edge case | Mitigation |
|-----------|------------|
| **Ambiguous or missing fields** | Derive where possible (e.g. "Fifth full lease year" from commencement date); use "See Exhibit X" when value lives in an exhibit; use "Not specified" when truly absent; never invent. |
| **Conflicting clauses** | Extraction can list multiple mentions; chat retrieves all relevant chunks and the prompt asks the model to state conflicts and cite each source (e.g. "Section X says …; Section Y says …"). |
| **Complex or nested clauses** | Chunk by section so one chunk ≈ one section; use overlap for context; prompt LLM to summarize in one sentence and still cite the section. |
| **Queries with multiple answers** | Use top-k retrieval; prompt: "If multiple provisions apply, list each with its citation." |
| **Very long sections** | Split long articles into sub-chunks with same `article`/`section` metadata; citation can be "Page 10–11, Article 17." |
| **Exhibits not in PDF text** | Extraction uses "See Exhibit C" or "Per Section 1.1 K"; chat answers from main lease text and states that exact figures are in the exhibit. |

## Limitations and trade-offs

- **Accuracy:** Extraction and answers depend on LLM quality and retrieval; always verify critical terms against the original document.
- **Cost and rate limits:** LLM calls (extraction + each chat turn) use your OpenAI key; long documents and many questions increase usage.
- **OCR quality:** Scanned PDFs depend on Tesseract; poor scans or handwriting can yield wrong or missing text.
- **Single session:** Vector store and summary live in Streamlit session state; refreshing the page or closing the tab loses the document context until you re-upload or re-paste.
- **Deployment:** Streamlit Cloud does not support Tesseract, so hosted apps typically support only digital PDFs (or paste) unless you add a cloud OCR API.
- **Citation granularity:** Citations are at page/section level from chunk metadata; exact line or paragraph numbers are not tracked.

## Evaluation alignment

- **Pipeline:** Modular ingestion → extraction and ingestion → retrieval → chat; single entrypoint; assumptions documented.
- **Structured output:** Schema enforces required fields; extraction targets Section 1.1, exhibits, and termination/renewal.
- **Chat + citations:** Answers tied to retrieved chunks; consistent "Page X, Section Y" citations; optional multi-turn.
- **Edge cases:** Six cases documented with concrete mitigations in code and prompts.
