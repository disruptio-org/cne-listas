from __future__ import annotations

import pytest

pytest.importorskip("pydantic")

from api.app.services.render import DocumentRenderer, RenderedPage


class _FakeImage:
    def save(self, buffer, format="PNG") -> None:
        # minimal PNG header followed by placeholder data
        buffer.write(b"\x89PNG\r\n\x1a\nFAKE")


class DummyPreview:
    def __init__(self, image) -> None:
        self.original = image


def _build_dummy_pdf(pages):
    class DummyPDF:
        def __init__(self, pdf_pages):
            self.pages = pdf_pages

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    return DummyPDF(pages)


class DummyPage:
    def __init__(self) -> None:
        self._image = _FakeImage()

    def extract_text(self):
        return ""

    def to_image(self, resolution: int = 200):  # pragma: no cover - simple stub
        return DummyPreview(self._image)


def test_render_pdf_without_text_returns_image_bytes(monkeypatch):
    renderer = DocumentRenderer()
    dummy_page = DummyPage()
    dummy_pdf = _build_dummy_pdf([dummy_page])

    monkeypatch.setattr(renderer, "_open_pdf", lambda buffer: dummy_pdf)

    pages = renderer._render_pdf(b"%PDF-1.4", source="dummy.pdf")

    assert len(pages) == 1
    page: RenderedPage = pages[0]
    assert page.payload, "Expected payload to contain rasterized image bytes"
    assert page.payload.startswith(b"\x89PNG")
