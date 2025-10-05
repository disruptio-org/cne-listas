from __future__ import annotations

import csv
from io import StringIO
from typing import Iterable, List

from ..schemas.csv_contract import CandidateRow


class CSVWriter:
    """Produce UTF-8 CSV output that matches the contract."""

    def write(self, rows: Iterable[CandidateRow]) -> str:
        materialised: List[CandidateRow] = list(rows)
        ordered = sorted(
            materialised,
            key=lambda row: (
                row.DTMNFR,
                row.ORGAO,
                row.SIGLA,
                row.NOME_LISTA,
                row.TIPO,
                row.NUM_ORDEM,
            ),
        )

        buffer = StringIO()
        writer = csv.writer(buffer, delimiter=";", lineterminator="\n")
        writer.writerow(CandidateRow.HEADERS)
        for row in ordered:
            writer.writerow(row.as_iterable())
        return buffer.getvalue()


__all__ = ["CSVWriter"]
