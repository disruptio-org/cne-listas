from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class LayoutRow:
    values: List[str]


@dataclass
class LayoutPage:
    page_number: int
    source: str
    rows: List[LayoutRow]


class LayoutAnalyzer:
    """Heuristic layout analyser for semi-structured electoral lists."""

    def analyze(self, pages: Iterable["OCRPage"]) -> List[LayoutPage]:
        from .ocr import OCRPage  # local import to avoid cycles

        analysed: List[LayoutPage] = []
        for page in pages:
            rows = self._split_rows(page.text)
            analysed.append(LayoutPage(page_number=page.page_number, source=page.source, rows=rows))
        return analysed

    def _split_rows(self, text: str) -> List[LayoutRow]:
        if not text:
            return []

        rows: List[LayoutRow] = []
        for raw_line in text.splitlines():
            clean_line = " ".join(raw_line.strip().split())
            if not clean_line:
                continue
            if ";" in clean_line:
                values = [value.strip() for value in clean_line.split(";")]
            elif "," in clean_line and clean_line.count(",") >= 9:
                values = [value.strip() for value in clean_line.split(",")]
            else:
                values = [value.strip() for value in clean_line.split("  ") if value.strip()]
                if len(values) < 10:
                    values = clean_line.split()
            rows.append(LayoutRow(values=values))
        return rows


__all__ = ["LayoutAnalyzer", "LayoutPage", "LayoutRow"]
