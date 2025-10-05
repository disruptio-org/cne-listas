from __future__ import annotations

from collections import defaultdict
from typing import Iterable, List

from ..schemas.csv_contract import CandidateRow
from .master_data import VALID_ORGAOS, VALID_TIPOS


class ValidationError(Exception):
    """Raised when the extracted data violates hard business rules."""


class DataValidator:
    """Apply hard validation rules to the normalised data."""

    def validate(self, rows: Iterable[CandidateRow]) -> None:
        materialised: List[CandidateRow] = list(rows)
        self._check_domains(materialised)
        self._check_sequences(materialised)
        self._check_conditionals(materialised)

    def _check_domains(self, rows: List[CandidateRow]) -> None:
        for row in rows:
            if row.ORGAO.upper() not in VALID_ORGAOS:
                raise ValidationError(f"ORGAO inválido: {row.ORGAO}")
            if row.TIPO.upper() not in VALID_TIPOS:
                raise ValidationError(f"TIPO inválido: {row.TIPO}")
            if not row.DTMNFR:
                raise ValidationError("DTMNFR obrigatório")
            if not row.SIGLA:
                raise ValidationError("SIGLA obrigatória")
            if not row.NOME_CANDIDATO:
                raise ValidationError("NOME_CANDIDATO obrigatório")

    def _check_sequences(self, rows: List[CandidateRow]) -> None:
        grouped = defaultdict(list)
        for row in rows:
            key = (row.DTMNFR, row.ORGAO, row.SIGLA, row.TIPO)
            grouped[key].append(row.NUM_ORDEM)

        for key, numbers in grouped.items():
            expected = 1
            for number in sorted(numbers):
                if number != expected:
                    raise ValidationError(
                        f"NUM_ORDEM inválido para {key}: esperado {expected}, obtido {number}"
                    )
                expected += 1

    def _check_conditionals(self, rows: List[CandidateRow]) -> None:
        for row in rows:
            tipo = row.TIPO.upper()
            if tipo in {"GCE", "COLIGAÇÃO"} and not row.NOME_LISTA:
                raise ValidationError("NOME_LISTA obrigatório para coligações/GCE")
            if tipo == "GCE" and row.SIMBOLO:
                # símbolo representa o próprio GCE, permitir valor "GCE"
                if row.SIMBOLO.upper() not in {"GCE", ""}:
                    raise ValidationError("SIMBOLO inválido para GCE")
            if tipo != "GCE" and row.SIMBOLO:
                raise ValidationError("SIMBOLO apenas permitido para GCE")
            if tipo == "GCE" and row.INDEPENDENTE:
                raise ValidationError("INDEPENDENTE deve ficar vazio para GCE")


__all__ = ["DataValidator", "ValidationError"]
