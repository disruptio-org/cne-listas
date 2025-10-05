from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

_render_path = PROJECT_ROOT / "api" / "app" / "services" / "render.py"
module_name = "api.app.services.render"
spec = importlib.util.spec_from_file_location(module_name, _render_path)
assert spec and spec.loader is not None

for package_name in ("api", "api.app", "api.app.services"):
    if package_name not in sys.modules:
        package_module = types.ModuleType(package_name)
        package_module.__path__ = []  # type: ignore[attr-defined]
        sys.modules[package_name] = package_module

render = importlib.util.module_from_spec(spec)
sys.modules[module_name] = render
spec.loader.exec_module(render)


class _FakeOriginalImage:
    def save(self, buffer, format="PNG"):
        buffer.write(b"fake-image-bytes")


class _FakePageImage:
    def __init__(self):
        self.original = _FakeOriginalImage()


class _FakePage:
    def extract_text(self):
        return ""

    def to_image(self, resolution=200):
        assert resolution == 200
        return _FakePageImage()


class _FakePDF:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _fake_open(_):
    return _FakePDF([_FakePage()])


def test_render_pdf_without_text_rasterizes_to_image(monkeypatch):
    fake_pdfplumber = types.SimpleNamespace(open=_fake_open)
    monkeypatch.setattr(render, "pdfplumber", fake_pdfplumber)

    renderer = render.DocumentRenderer()
    pages = renderer.render(b"%PDF-FAKE", filename="mock.pdf")

    assert len(pages) == 1
    page = pages[0]
    assert page.page_number == 1
    assert page.source == "mock.pdf#page=1"
    assert page.payload == b"fake-image-bytes"


def test_render_pdf_raises_when_pdfplumber_missing(monkeypatch):
    monkeypatch.setattr(render, "pdfplumber", None)

    renderer = render.DocumentRenderer()

    with pytest.raises(RuntimeError, match="pdfplumber is required"):
        renderer.render(b"%PDF-1.4", filename="missing.pdf")
