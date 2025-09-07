from __future__ import annotations

import io
from typing import Optional

def _extract_pdf_text_pdfplumber(file_like: io.BytesIO) -> Optional[str]:
    try:
        import pdfplumber  # type: ignore
        text_parts = []
        with pdfplumber.open(file_like) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts).strip()
    except Exception:
        return None


def _extract_pdf_text_pymupdf(file_like: io.BytesIO) -> Optional[str]:
    try:
        import fitz  # PyMuPDF
        text_parts = []
        with fitz.open(stream=file_like.getvalue(), filetype="pdf") as doc:
            for page in doc:
                text_parts.append(page.get_text() or "")
        return "\n".join(text_parts).strip()
    except Exception:
        return None


def _extract_pdf_text_pdfminer(file_like: io.BytesIO) -> Optional[str]:
    try:
        from pdfminer.high_level import extract_text
        file_like.seek(0)
        return (extract_text(file_like) or "").strip()
    except Exception:
        return None


def extract_text_from_pdf(file_like: io.BytesIO) -> str:
    for fn in (_extract_pdf_text_pdfplumber, _extract_pdf_text_pymupdf, _extract_pdf_text_pdfminer):
        text = fn(file_like)
        if text and len(text.strip()) > 0:
            return text
        file_like.seek(0)
    return ""


def extract_text_from_any(file_like: io.BytesIO, mime_or_name: str) -> str:
    lowered = (mime_or_name or "").lower()
    if lowered.endswith(".pdf") or "pdf" in lowered:
        return extract_text_from_pdf(file_like)
    else:
        try:
            return file_like.read().decode("utf-8", errors="ignore")
        except Exception:
            return ""



