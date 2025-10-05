#!/usr/bin/env python3
"""Validate the CSV contract requirements for generated files."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict

EXPECTED_HEADERS = [
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


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: scripts/test_csv_contract.py <csv-path>", file=sys.stderr)
        return 1

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as handle:
        reader = csv.reader(handle, delimiter=";")
        rows = list(reader)

    if not rows:
        print("CSV vazio", file=sys.stderr)
        return 1

    header = rows[0]
    if header != EXPECTED_HEADERS:
        print(f"Cabeçalho inválido: {header}", file=sys.stderr)
        return 1

    order_track = defaultdict(lambda: None)
    for index, row in enumerate(rows[1:], start=2):
        if len(row) != 10:
            print(f"Linha {index} com {len(row)} colunas (esperado 10)", file=sys.stderr)
            return 1
        record = dict(zip(EXPECTED_HEADERS, row))
        key = (record["DTMNFR"], record["ORGAO"], record["SIGLA"], record["TIPO"])
        num_ordem = int(record["NUM_ORDEM"])
        last_value = order_track[key]
        if last_value is None:
            if num_ordem != 1:
                print(
                    f"Linha {index}: NUM_ORDEM deve iniciar em 1 para TIPO {record['TIPO']}",
                    file=sys.stderr,
                )
                return 1
        else:
            if num_ordem != last_value + 1:
                print(
                    f"Linha {index}: NUM_ORDEM deve ser sequencial (obtido {num_ordem}, esperado {last_value + 1})",
                    file=sys.stderr,
                )
                return 1
        order_track[key] = num_ordem

    print(f"CSV {path} válido: {len(rows) - 1} linhas verificados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
