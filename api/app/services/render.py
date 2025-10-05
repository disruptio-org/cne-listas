from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Iterable, List, Optional


try:  # pragma: no cover - optional dependency
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pdfplumber = None


@dataclass
class RenderedPage:
    """Representation of a rendered page ready for OCR."""

    page_number: int
    payload: bytes
    source: str


class DocumentRenderer:
    """Render arbitrary document payloads into OCR-friendly pages."""

    def render(
        self,
        payload: bytes,
        *,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> List[RenderedPage]:
        if not payload:
            return []

        if self._is_pdf(filename, content_type):
            pages = self._render_pdf(payload, source=filename or "<uploaded>")
            if pages:
                return pages

        return [RenderedPage(page_number=1, payload=payload, source=filename or "<uploaded>")]

    def _is_pdf(self, filename: Optional[str], content_type: Optional[str]) -> bool:
        if content_type and "pdf" in content_type:
            return True
        if filename and filename.lower().endswith(".pdf"):
            return True
        return False

    def _render_pdf(self, payload: bytes, *, source: str) -> List[RenderedPage]:
        if pdfplumber is None:
            return []

        pages: List[RenderedPage] = []
        with pdfplumber.open(BytesIO(payload)) as pdf:  # pragma: no cover - heavy dependency
            for index, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                pages.append(
                    RenderedPage(
                        page_number=index,
                        payload=text.encode("utf-8"),
                        source=f"{source}#page={index}",
                    )
                )
        return pages


__all__ = ["DocumentRenderer", "RenderedPage"]
