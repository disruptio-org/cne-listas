from __future__ import annotations

import unicodedata
from typing import Iterable, List

from .extract import RawCandidate
from .master_data import VALID_ORGAOS, VALID_TIPOS, resolve_sigla
from ..schemas.csv_contract import CandidateRow


class DataNormalizer:
    """Normalise extracted data to fit the CSV contract."""

    def normalize(self, candidates: Iterable[RawCandidate]) -> List[CandidateRow]:
        normalised: List[CandidateRow] = []
        for candidate in candidates:
            row = self._normalize_candidate(candidate)
            normalised.append(row)
        return normalised

    def _normalize_candidate(self, candidate: RawCandidate) -> CandidateRow:
        dtmnfr = self._clean(candidate.dtmnfr)
        orgao = self._normalise_orgao(candidate.orgao, candidate.anchor)
        tipo = self._normalise_tipo(candidate.tipo, candidate.anchor)
        sigla_resolution = resolve_sigla(candidate.sigla)
        simbolo = self._clean(candidate.simbolo)
        nome_lista = self._clean(candidate.nome_lista)
        num_ordem = self._to_int(candidate.num_ordem)
        nome_candidato = self._title_case(candidate.nome_candidato)
        partido = self._clean(candidate.partido_proponente)
        independente = self._normalise_independente(candidate.independente, tipo)

        if tipo == "GCE":
            simbolo = simbolo or "GCE"
            independente = ""
            if not nome_lista:
                nome_lista = "GCE"
        elif tipo != "GCE" and simbolo:
            simbolo = ""

        if tipo in {"GCE", "COLIGAÇÃO"} and not nome_lista:
            nome_lista = sigla_resolution.canonical

        return CandidateRow(
            DTMNFR=dtmnfr or "",
            ORGAO=orgao,
            TIPO=tipo,
            SIGLA=sigla_resolution.canonical,
            SIMBOLO=simbolo,
            NOME_LISTA=nome_lista,
            NUM_ORDEM=num_ordem,
            NOME_CANDIDATO=nome_candidato,
            PARTIDO_PROPONENTE=partido,
            INDEPENDENTE=independente,
        )

    def _clean(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            return ""
        value = unicodedata.normalize("NFKC", value)
        return value

    def _title_case(self, value: str) -> str:
        clean = self._clean(value)
        return clean.title()

    def _normalise_orgao(self, value: str, anchor: str) -> str:
        cleaned = self._clean(value).upper()
        if cleaned in VALID_ORGAOS:
            return cleaned
        anchor_upper = anchor.upper()
        for domain in VALID_ORGAOS:
            if domain in cleaned or domain in anchor_upper:
                return domain
        return cleaned or "ASSEMBLEIA"

    def _normalise_tipo(self, value: str, anchor: str) -> str:
        cleaned = self._clean(value).upper()
        if cleaned in VALID_TIPOS:
            return cleaned
        anchor_upper = anchor.upper()
        if "SUPLENTE" in anchor_upper:
            return "SUPLENTES"
        if "EFET" in anchor_upper:
            return "EFETIVOS"
        return cleaned or "EFETIVOS"

    def _to_int(self, value: str) -> int:
        cleaned = self._clean(value)
        digits = "".join(ch for ch in cleaned if ch.isdigit())
        if digits:
            return int(digits)
        return 0

    def _normalise_independente(self, value: str, tipo: str) -> str:
        cleaned = self._clean(value)
        if tipo == "GCE":
            return ""
        if cleaned.lower() in {"sim", "s", "yes", "true"}:
            return "SIM"
        if cleaned.lower() in {"não", "nao", "n", "no", "false"}:
            return "NAO"
        return cleaned.upper()


__all__ = ["DataNormalizer"]
