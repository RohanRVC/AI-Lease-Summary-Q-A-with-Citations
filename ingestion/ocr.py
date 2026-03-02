from typing import Optional

_ocr_available: Optional[bool] = None


def _check_ocr_available() -> bool:
    global _ocr_available
    if _ocr_available is not None:
        return _ocr_available
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        _ocr_available = True
    except Exception:
        _ocr_available = False
    return _ocr_available


def ocr_image_to_text(image_bytes: bytes) -> Optional[str]:
    if not _check_ocr_available():
        return None
    try:
        from PIL import Image
        import io
        import pytesseract
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img)
        return text.strip() if text else None
    except Exception:
        return None


def is_ocr_available() -> bool:
    return _check_ocr_available()
