from __future__ import annotations

from typing import List, Optional

from ..schemas.csv_contract import CandidateRow
from .extract import DataExtractor
from .layout import LayoutAnalyzer
from .normalize import DataNormalizer
from .ocr import OCREngine
from .render import DocumentRenderer
from .segment import AnchorDetector
from .validate import DataValidator


class ExtractionPipeline:
    """Coordinate the hybrid extraction pipeline."""

    def __init__(self) -> None:
        self.renderer = DocumentRenderer()
        self.ocr = OCREngine()
        self.layout = LayoutAnalyzer()
        self.anchor_detector = AnchorDetector()
        self.extractor = DataExtractor()
        self.normalizer = DataNormalizer()
        self.validator = DataValidator()

    def run(
        self,
        payload: bytes,
        *,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> List[CandidateRow]:
        rendered = self.renderer.render(payload, filename=filename, content_type=content_type)
        ocr_pages = self.ocr.run(rendered)
        layout_pages = self.layout.analyze(ocr_pages)
        segments = self.anchor_detector.locate(layout_pages)
        raw_candidates = self.extractor.extract(segments)
        normalised_rows = self.normalizer.normalize(raw_candidates)
        self.validator.validate(normalised_rows)
        return normalised_rows


__all__ = ["ExtractionPipeline"]
