from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from .segment import DocumentSegment

try:  # pragma: no cover - optional dependency
    import spacy  # type: ignore
    from spacy.language import Language  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    spacy = None
    Language = None


@dataclass
class RawCandidate:
    dtmnfr: str
    orgao: str
    tipo: str
    sigla: str
    simbolo: str
    nome_lista: str
    num_ordem: str
    nome_candidato: str
    partido_proponente: str
    independente: str
    anchor: str


class DataExtractor:
    """Extract candidate rows from anchored layout segments."""

    def __init__(self) -> None:
        self._nlp: Optional[Language] = None
        if spacy is not None:
            try:  # pragma: no cover - heavy dependency
                self._nlp = spacy.load("pt_core_news_sm")
            except Exception:
                try:
                    self._nlp = spacy.blank("pt")
                except Exception:
                    self._nlp = None

    def extract(self, segments: Iterable[DocumentSegment]) -> List[RawCandidate]:
        candidates: List[RawCandidate] = []
        context = {
            "DTMNFR": "",
            "ORGAO": "",
            "TIPO": "",
            "SIGLA": "",
            "SIMBOLO": "",
            "NOME_LISTA": "",
            "PARTIDO_PROPONENTE": "",
        }

        for segment in segments:
            for row in segment.rows:
                if len(row.values) >= 10:
                    mapping = row.values[:10]
                else:
                    mapping = self._heuristic_fill(row.values, context)
                    if mapping is None:
                        continue

                context.update(
                    {
                        "DTMNFR": mapping[0] or context["DTMNFR"],
                        "ORGAO": mapping[1] or context["ORGAO"],
                        "TIPO": mapping[2] or context["TIPO"],
                        "SIGLA": mapping[3] or context["SIGLA"],
                        "SIMBOLO": mapping[4] or context["SIMBOLO"],
                        "NOME_LISTA": mapping[5] or context["NOME_LISTA"],
                        "PARTIDO_PROPONENTE": mapping[8] or context["PARTIDO_PROPONENTE"],
                    }
                )

                candidates.append(
                    RawCandidate(
                        dtmnfr=mapping[0] or context["DTMNFR"],
                        orgao=mapping[1] or context["ORGAO"],
                        tipo=mapping[2] or context["TIPO"],
                        sigla=mapping[3] or context["SIGLA"],
                        simbolo=mapping[4] or context["SIMBOLO"],
                        nome_lista=mapping[5] or context["NOME_LISTA"],
                        num_ordem=mapping[6],
                        nome_candidato=mapping[7],
                        partido_proponente=mapping[8] or context["PARTIDO_PROPONENTE"],
                        independente=mapping[9],
                        anchor=segment.anchor,
                    )
                )
        return candidates

    def _heuristic_fill(self, values: List[str], context: dict[str, str]) -> Optional[List[str]]:
        if not values:
            return None
        padded = [""] * 10
        for idx, value in enumerate(values[:10]):
            padded[idx] = value

        # Attempt to guess candidate name when missing using NER
        if not padded[7] and self._nlp is not None:
            doc = self._nlp(" ".join(values))  # pragma: no cover - heavy dependency
            for ent in doc.ents:
                if ent.label_.upper() in {"PER", "PESSOA", "PERSON"}:
                    padded[7] = ent.text
                    break

        if not padded[7]:
            padded[7] = self._guess_name(values)

        if not padded[6]:
            padded[6] = self._guess_order(values)

        if not padded[0]:
            padded[0] = context.get("DTMNFR", "")
        if not padded[1]:
            padded[1] = context.get("ORGAO", "")
        if not padded[2]:
            padded[2] = context.get("TIPO", "")
        if not padded[3]:
            padded[3] = context.get("SIGLA", "")
        if not padded[5]:
            padded[5] = context.get("NOME_LISTA", "")

        if not padded[7]:
            return None

        return padded

    def _guess_name(self, values: List[str]) -> str:
        for value in reversed(values):
            if any(char.isalpha() for char in value) and len(value.split()) >= 2:
                return value
        return ""

    def _guess_order(self, values: List[str]) -> str:
        for value in values:
            digits = "".join(char for char in value if char.isdigit())
            if digits:
                return digits
        return "1"


__all__ = ["DataExtractor", "RawCandidate"]
