from __future__ import annotations

from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

from .services.pipeline import ExtractionPipeline
from .services.csv_writer import CSVWriter
from .services.validate import ValidationError


app = FastAPI(title="CNE Listas Extraction Service", version="1.0.0")

pipeline = ExtractionPipeline()
csv_writer = CSVWriter()


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Simple health endpoint used for uptime monitoring."""
    return {"status": "ok"}


@app.post("/api/ocr-csv", response_class=PlainTextResponse)
async def ocr_to_csv(
    files: List[UploadFile] | None = File(default=None),
    file: UploadFile | None = File(default=None),
) -> PlainTextResponse:
    """Run the hybrid extraction pipeline over one or more uploaded files."""

    uploads: List[UploadFile] = []
    if files:
        uploads.extend(files)
    if file is not None:
        uploads.append(file)

    if not uploads:
        raise HTTPException(status_code=400, detail="At least one file must be provided")

    rows = []
    for upload in uploads:
        payload = await upload.read()
        try:
            document_rows = pipeline.run(
                payload, filename=upload.filename, content_type=upload.content_type
            )
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        rows.extend(document_rows)

    csv_content = csv_writer.write(rows)

    return PlainTextResponse(content=csv_content, media_type="text/csv; charset=utf-8")


__all__ = ["app"]
