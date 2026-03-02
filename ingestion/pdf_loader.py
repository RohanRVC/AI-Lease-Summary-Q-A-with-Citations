import tempfile
from pathlib import Path
from typing import List, Tuple, Union

from config import MIN_TEXT_LENGTH_FOR_OCR, OCR_IMAGE_SCALE

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

    #     Open PDF from path or bytes. ... .
def _open_document(pdf_path_or_bytes: Union[str, Path, bytes]) -> Tuple[object, Path | None]:
   
    if fitz is None:
        raise ImportError("PyMuPDF is required. Install with: pip install pymupdf")

    if isinstance(pdf_path_or_bytes, bytes):
        data = pdf_path_or_bytes
        path = None
    else:
        path = Path(pdf_path_or_bytes)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")
        data = path.read_bytes()

    # Try 1: open from stream (works for most PDFs)
    try:
        doc = fitz.open(stream=data, filetype="pdf")
        return doc, None
    except Exception as e:
        err_msg = str(e).lower() if e else ""
        if "no such group" in err_msg or "group" in err_msg:
            pass  # fall through to temp file
        else:
            raise

    # Try 2: open from file path (some PDFs with OCGs/form issues need this)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        tmp.write(data)
        tmp.close()
        doc = fitz.open(tmp.name)
        return doc, Path(tmp.name)
    except Exception:
        Path(tmp.name).unlink(missing_ok=True)
        raise


def _page_to_image_bytes(page, scale: float = 2.0) -> bytes:
    """Render a PyMuPDF page to PNG bytes for OCR."""
    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    return pix.tobytes("png")


def load_pdf_pages(pdf_path_or_bytes: Union[str, Path, bytes]) -> List[dict]:
    """
    Load a PDF and return a list of page dicts with keys: page_number (1-based), text.
    - If the PDF has embedded text, it is extracted directly.
    - If a page has very little text (scanned page), OCR is run when Tesseract is available.
    Accepts file path (str or Path) or raw PDF bytes (e.g. from upload).
    """
    if fitz is None:
        raise ImportError("PyMuPDF is required. Install with: pip install pymupdf")

    doc, temp_path = _open_document(pdf_path_or_bytes)
    pages = []
    try:
        from .ocr import ocr_image_to_text, is_ocr_available
        use_ocr = is_ocr_available()
        for i in range(len(doc)):
            text = ""
            try:
                page = doc.load_page(i)
                text = page.get_text()
                text = (text or "").strip()
                # If page looks scanned (too little text), try OCR
                if use_ocr and len(text) < MIN_TEXT_LENGTH_FOR_OCR:
                    try:
                        img_bytes = _page_to_image_bytes(page, scale=OCR_IMAGE_SCALE)
                        ocr_text = ocr_image_to_text(img_bytes)
                        if ocr_text:
                            text = ocr_text
                    except Exception:
                        pass
            except Exception:
                # "no such group" or other per-page errors: keep this page with empty text
                pass
            pages.append({
                "page_number": i + 1,
                "text": text,
            })
    finally:
        doc.close()
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    return pages
