from __future__ import annotations

from typing import ClassVar, Iterable, List

from pydantic import BaseModel, Field, validator


class CandidateRow(BaseModel):
    """Representation of a single CSV contract row."""

    HEADERS: ClassVar[List[str]] = [
        "DTMNFR",
        "ORGAO",
        "TIPO",
        "SIGLA",
        "SIMBOLO",
        "NOME_LISTA",
        "NUM_ORDEM",
        "NOME_CANDIDATO",
        "PARTIDO_PROPONENTE",
        "INDEPENDENTE",
    ]

    DTMNFR: str = Field(..., description="Data/mandato de referência")
    ORGAO: str = Field(..., description="Órgão a que respeita a lista")
    TIPO: str = Field(..., description="Tipo de lista")
    SIGLA: str = Field(..., description="Sigla principal")
    SIMBOLO: str = Field(default="", description="Símbolo (apenas GCE)")
    NOME_LISTA: str = Field(default="", description="Designação da lista")
    NUM_ORDEM: int = Field(..., description="Número de ordem do candidato dentro do tipo")
    NOME_CANDIDATO: str = Field(..., description="Nome do candidato")
    PARTIDO_PROPONENTE: str = Field(default="", description="Partido proponente")
    INDEPENDENTE: str = Field(default="", description="Indicador de independência")

    @validator("NUM_ORDEM", pre=True)
    def coerce_num_ordem(cls, value: int | str) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.strip():
            return int(value.strip())
        return 0

    def as_iterable(self) -> Iterable[str]:
        """Return the row in CSV order as an iterable of strings."""

        return [
            self.DTMNFR,
            self.ORGAO,
            self.TIPO,
            self.SIGLA,
            self.SIMBOLO,
            self.NOME_LISTA,
            str(self.NUM_ORDEM),
            self.NOME_CANDIDATO,
            self.PARTIDO_PROPONENTE,
            self.INDEPENDENTE,
        ]


__all__ = ["CandidateRow"]
