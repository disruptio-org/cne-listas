from __future__ import annotations

import sys
from pathlib import Path

import pytest

try:
    from fastapi.testclient import TestClient
except ModuleNotFoundError:  # pragma: no cover - dependency optional in tests
    pytest.skip("FastAPI not available", allow_module_level=True)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.app.main import app, pipeline  # noqa: E402
from api.app.services.validate import ValidationError  # noqa: E402


def test_ocr_csv_returns_422_on_validation_error(monkeypatch):
    client = TestClient(app)

    def _raise_validation_error(payload, *, filename=None, content_type=None):
        raise ValidationError("ORGAO inválido: MOCK")

    monkeypatch.setattr(pipeline, "run", _raise_validation_error)

    response = client.post(
        "/api/ocr-csv",
        files={"file": ("invalid.pdf", b"%PDF-FAKE", "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "ORGAO inválido: MOCK"}
