# Lease Chat App — AI-Powered Chat with Source Citation

Document-aware AI chat: upload a lease PDF, view a structured summary, and ask questions with answers tied to document sources (page and section).

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

See `docs/PIPELINE_OVERVIEW.md` for the pipeline and assumptions, and `docs/EDGE_CASES.md` for edge-case analysis and mitigations.

## Edge cases (summary)

The system is designed to handle:

- Ambiguous or missing fields (derive or "See Exhibit X"; never invent).
- Conflicting clauses (cite multiple sections).
- Complex clauses (section-level chunks; summarize with citation).
- Queries with multiple answers (list each with citation).
- Very long sections (sub-chunks with same article/section; cite page range).
- Exhibits not in text (reference main lease text only).

Details and strategies are in `docs/EDGE_CASES.md`.

## Evaluation alignment

- **Pipeline:** Modular ingestion → extraction and ingestion → retrieval → chat; single entrypoint; assumptions documented.
- **Structured output:** Schema enforces required fields; extraction targets Section 1.1, exhibits, and termination/renewal.
- **Chat + citations:** Answers tied to retrieved chunks; consistent "Page X, Section Y" citations; optional multi-turn.
- **Edge cases:** Six cases documented with concrete mitigations in code and prompts.
