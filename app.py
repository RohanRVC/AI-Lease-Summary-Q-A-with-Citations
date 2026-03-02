"""
Streamlit entrypoint: file upload, lease summary, and chat with source citations.
"""
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

import streamlit as st

from ingestion.pdf_loader import load_pdf_pages
from ingestion.chunker import chunk_document
from ingestion.text_to_pages import pasted_text_to_pages
from extraction.extractor import extract_lease_summary
from retrieval.store import VectorStore
from ui.summary_display import render_lease_summary
from ui.chat_ui import render_chat


st.set_page_config(page_title="Lease Chat", page_icon="📄", layout="wide")
st.title("AI-Powered Lease Chat with Source Citation")
st.markdown("Upload a PDF or paste document text. View the extracted summary and ask questions with source citations.")
#st.caption("Supports both digital and scanned PDFs (OCR when needed), or paste text copied from any PDF.")

# Session state for processed document
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "lease_summary" not in st.session_state:
    st.session_state.lease_summary = None
if "last_processed_file" not in st.session_state:
    st.session_state.last_processed_file = None
if "input_method" not in st.session_state:
    st.session_state.input_method = None  # "upload" | "paste"


def process_uploaded_file(uploaded_file) -> tuple[VectorStore | None, object]:
    """Load PDF, chunk, extract summary, build vector store. Returns (store, summary) or (None, None) on error."""
    if uploaded_file is None:
        return None, None
    try:
        pdf_bytes = uploaded_file.getvalue()
        pages = load_pdf_pages(pdf_bytes)
        if not pages:
            st.error("No text could be extracted from the PDF.")
            return None, None
        chunks = chunk_document(pages)
        summary = extract_lease_summary(pages)
        store = VectorStore()
        store.add_chunks(chunks)
        return store, summary
    except Exception as e:
        st.error(f"Error processing document: {e}")
        return None, None


def process_pasted_text(text: str) -> tuple[VectorStore | None, object]:
    """Convert pasted text to pages, then chunk, extract, and build vector store. Returns (store, summary) or (None, None)."""
    if not (text or "").strip():
        return None, None
    try:
        pages = pasted_text_to_pages(text.strip())
        if not pages:
            st.error("No content to process.")
            return None, None
        chunks = chunk_document(pages)
        summary = extract_lease_summary(pages)
        store = VectorStore()
        store.add_chunks(chunks)
        return store, summary
    except Exception as e:
        st.error(f"Error processing pasted text: {e}")
        return None, None


input_method = st.radio(
    "How do you want to provide the lease?",
    options=["Upload PDF", "Paste text"],
    horizontal=True,
    key="input_radio",
)

if input_method == "Upload PDF":
    uploaded = st.file_uploader("Upload lease PDF", type=["pdf"], key="lease_upload")
    if uploaded:
        process_key = ("upload", getattr(uploaded, "file_id", id(uploaded)))
        if (
            st.session_state.vector_store is None
            or st.session_state.last_processed_file != process_key
        ):
            with st.spinner("Loading document (text + OCR if scanned), extracting summary, and building search index..."):
                store, summary = process_uploaded_file(uploaded)
                st.session_state.vector_store = store
                st.session_state.lease_summary = summary
                st.session_state.last_processed_file = process_key
                st.session_state.input_method = "upload"
                if store is not None:
                    st.session_state.messages = []

        if st.session_state.lease_summary is not None:
            render_lease_summary(st.session_state.lease_summary)
        if st.session_state.vector_store is not None:
            st.divider()
            st.subheader("Ask about the lease")
            render_chat(st.session_state.vector_store)
    else:
        st.info("Upload a PDF lease (digital or scanned), or switch to **Paste text** to paste content copied from a PDF.")
else:
    st.markdown("Paste the full text of the lease below (e.g. copy from your PDF). If the text has page markers like `-- 1 of 30 --`, they will be used for source citations.")
    pasted = st.text_area(
        "Paste lease text here",
        height=280,
        placeholder="Paste the document text here...",
        key="pasted_text",
    )
    if st.button("Use this text", type="primary", key="use_pasted_btn"):
        if not (pasted or "").strip():
            st.warning("Please paste some text first.")
        else:
            with st.spinner("Extracting summary and building search index..."):
                store, summary = process_pasted_text(pasted)
                if store is not None and summary is not None:
                    st.session_state.vector_store = store
                    st.session_state.lease_summary = summary
                    st.session_state.last_processed_file = ("paste", hash(pasted.strip()))
                    st.session_state.input_method = "paste"
                    st.session_state.messages = []
                    st.success("Text processed. Summary and chat are below.")
                    try:
                        st.rerun()
                    except AttributeError:
                        st.experimental_rerun()

    if st.session_state.lease_summary is not None and st.session_state.vector_store is not None:
        st.divider()
        render_lease_summary(st.session_state.lease_summary)
        st.divider()
        st.subheader("Ask about the lease")
        render_chat(st.session_state.vector_store)
