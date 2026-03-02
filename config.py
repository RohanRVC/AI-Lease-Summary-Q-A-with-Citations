"""
Configuration for the lease chat application.
Paths, model names, chunk sizes, and other tunable settings.
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

# PDF / chunking
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
MAX_PAGE_MARKER = 30  # "Page N of 30" style

# OCR for scanned PDFs: if a page has fewer than this many chars of extracted text, run OCR
MIN_TEXT_LENGTH_FOR_OCR = 80
# OCR image scale (higher = better quality, slower). 2 = 2x resolution for better accuracy
OCR_IMAGE_SCALE = 2

# Embeddings (sentence-transformers for local run)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Vector store
TOP_K_RETRIEVAL = 8

# LLM (set via env for flexibility: OPENAI_API_KEY, or use Ollama/local)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Extraction
EXTRACTION_MODEL = OPENAI_MODEL
