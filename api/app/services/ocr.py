from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


try:  # pragma: no cover - optional dependency
    from paddleocr import PaddleOCR  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    PaddleOCR = None

try:  # pragma: no cover - optional dependency
    import pytesseract  # type: ignore
    from PIL import Image  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    pytesseract = None
    Image = None
    np = None


@dataclass
class OCRPage:
    page_number: int
    source: str
    text: str


class OCREngine:
    """OCR abstraction with PaddleOCR preference and Tesseract fallback."""

    def __init__(self) -> None:
        self._paddle: Optional[PaddleOCR] = None
        if PaddleOCR is not None:
            try:  # pragma: no cover - heavy dependency
                self._paddle = PaddleOCR(use_angle_cls=True, lang="pt")
            except Exception:
                self._paddle = None

    def run(self, pages: List["RenderedPage"]) -> List[OCRPage]:
        from .render import RenderedPage  # local import to avoid cycles

        results: List[OCRPage] = []
        for page in pages:
            text = self._run_single(page)
            results.append(OCRPage(page_number=page.page_number, source=page.source, text=text))
        return results

    def _run_single(self, page: "RenderedPage") -> str:
        if self._paddle is not None:
            try:  # pragma: no cover - heavy dependency
                image_array = self._ensure_image(page.payload)
                if image_array is not None:
                    ocr_result = self._paddle.ocr(image_array, cls=True)
                    return "\n".join(
                        " ".join(token[1][0] for token in line if token)
                        if isinstance(line, list)
                        else ""
                        for line in ocr_result
                    ).strip()
            except Exception:
                pass

        if pytesseract is not None and Image is not None and np is not None:
            try:  # pragma: no cover - heavy dependency
                image_array = self._ensure_image(page.payload)
                if image_array is not None:
                    return pytesseract.image_to_string(image_array, lang="por")
            except Exception:
                pass

        try:
            return page.payload.decode("utf-8")
        except UnicodeDecodeError:
            return page.payload.decode("latin-1", errors="ignore")

    def _ensure_image(self, payload: bytes):  # pragma: no cover - heavy dependency
        if np is None or Image is None:
            return None
        try:
            from io import BytesIO

            with Image.open(BytesIO(payload)) as img:
                return np.array(img.convert("RGB"))
        except Exception:
            return None


__all__ = ["OCREngine", "OCRPage"]
