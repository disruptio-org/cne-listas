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
            raise RuntimeError(
                "pdfplumber is required to render PDF documents. Install the optional "
                "dependency or provide a non-PDF payload."
            )

        pages: List[RenderedPage] = []
        with pdfplumber.open(BytesIO(payload)) as pdf:  # pragma: no cover - heavy dependency
            for index, page in enumerate(pdf.pages, start=1):
                try:
                    text = page.extract_text()
                except Exception:  # pragma: no cover - defensive path
                    text = None

                if isinstance(text, str) and text.strip():
                    payload_bytes = text.encode("utf-8")
                else:
                    payload_bytes = self._rasterize_page(
                        page, page_number=index, source=source
                    )

                pages.append(
                    RenderedPage(
                        page_number=index,
                        payload=payload_bytes,
                        source=f"{source}#page={index}",
                    )
                )
        return pages

    def _rasterize_page(self, page: "pdfplumber.page.Page", *, page_number: int, source: str) -> bytes:
        try:  # pragma: no cover - relies on pillow/pdfplumber internals
            page_image = page.to_image(resolution=200)
            image = getattr(page_image, "original", None)
            if image is None:
                raise AttributeError("PageImage missing original image")
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            data = buffer.getvalue()
        except Exception as exc:  # pragma: no cover - defensive path
            raise RuntimeError(
                f"Unable to rasterize PDF page {page_number} from {source}: {exc}"
            ) from exc

        if not data:
            raise RuntimeError(
                f"Rasterization produced empty payload for page {page_number} from {source}"
            )

        return data


__all__ = ["DocumentRenderer", "RenderedPage"]
