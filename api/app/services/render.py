from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Iterable, List, Optional


try:  # pragma: no cover - optional dependency
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pdfplumber = None

try:  # pragma: no cover - optional dependency
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Image = None


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
            raise RuntimeError(
                "PDF rendering requires pdfplumber; install pdfplumber to enable PDF support"
            )

        pages: List[RenderedPage] = []
        with self._open_pdf(BytesIO(payload)) as pdf:  # pragma: no cover - heavy dependency
            for index, page in enumerate(pdf.pages, start=1):
                text = (page.extract_text() or "").strip()
                if text:
                    payload_bytes = text.encode("utf-8")
                else:
                    payload_bytes = self._page_to_image_bytes(page) or b""

                if not payload_bytes:
                    # fallback to original payload to avoid dropping the page entirely
                    payload_bytes = payload

                pages.append(
                    RenderedPage(
                        page_number=index,
                        payload=payload_bytes,
                        source=f"{source}#page={index}",
                    )
                )
        return pages

    def _open_pdf(self, buffer: BytesIO):  # pragma: no cover - light wrapper for testing
        if pdfplumber is None:
            raise RuntimeError(
                "PDF rendering requires pdfplumber; install pdfplumber to enable PDF support"
            )
        return pdfplumber.open(buffer)

    def _page_to_image_bytes(self, page) -> Optional[bytes]:  # pragma: no cover - heavy dependency
        if Image is None or not hasattr(page, "to_image"):
            return None
        try:
            preview = page.to_image(resolution=200)
            pil_image = preview.original
            buffer = BytesIO()
            pil_image.save(buffer, format="PNG")
            return buffer.getvalue()
        except Exception:
            return None


__all__ = ["DocumentRenderer", "RenderedPage"]
