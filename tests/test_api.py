from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from api.app.main import app, pipeline
from api.app.services.validate import ValidationError


def test_ocr_to_csv_returns_422_on_validation_error(monkeypatch):
    client = TestClient(app)

    def fake_run(*args, **kwargs):
        raise ValidationError("invalid data")

    monkeypatch.setattr(pipeline, "run", fake_run)

    response = client.post(
        "/api/ocr-csv",
        files={"file": ("dummy.txt", b"payload", "text/plain")},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "invalid data"
