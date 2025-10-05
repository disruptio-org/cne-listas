from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from .layout import LayoutPage, LayoutRow

ANCHOR_KEYWORDS: Dict[str, List[str]] = {
    "EFETIVOS": ["candidatos efetivos", "efetivos"],
    "SUPLENTES": ["candidatos suplentes", "suplentes"],
    "ASSEMBLEIA": ["assembleia", "assembleia municipal"],
    "CAMARA": ["câmara", "câmara municipal"],
    "FREGUESIA": ["freguesia", "assembleia de freguesia"],
}


@dataclass
class DocumentSegment:
    anchor: str
    rows: List[LayoutRow] = field(default_factory=list)
    page_numbers: List[int] = field(default_factory=list)


class AnchorDetector:
    """Detect anchor sections in the layout to contextualise extraction."""

    def locate(self, pages: Iterable[LayoutPage]) -> List[DocumentSegment]:
        segments: List[DocumentSegment] = []
        current: Optional[DocumentSegment] = None

        for page in pages:
            for row in page.rows:
                anchor = self._match_anchor(row)
                if anchor is not None:
                    current = DocumentSegment(anchor=anchor, rows=[], page_numbers=[page.page_number])
                    segments.append(current)
                    continue
                if current is None:
                    current = DocumentSegment(anchor="DESCONHECIDO", rows=[], page_numbers=[page.page_number])
                    segments.append(current)
                current.rows.append(row)
                if page.page_number not in current.page_numbers:
                    current.page_numbers.append(page.page_number)

        return segments

    def _match_anchor(self, row: LayoutRow) -> Optional[str]:
        joined = " ".join(value.lower() for value in row.values)
        for anchor, keywords in ANCHOR_KEYWORDS.items():
            if any(keyword in joined for keyword in keywords):
                return anchor
        return None


__all__ = ["AnchorDetector", "DocumentSegment"]
