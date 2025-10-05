from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
from typing import Dict, Iterable, List


MASTER_SIGLA: Dict[str, List[str]] = {
    "PS": ["ps", "partido socialista"],
    "PSD": ["psd", "partido social democrata"],
    "CDS-PP": ["cds", "cds-pp", "centro democrático"],
    "PCP": ["pcp", "partido comunista"],
    "BE": ["bloco de esquerda", "be"],
    "IL": ["iniciativa liberal", "il"],
    "PAN": ["pan", "pessoas animais"],
    "LIVRE": ["livre"],
    "CHEGA": ["chega"],
}

VALID_ORGAOS = {"ASSEMBLEIA", "CAMARA", "FREGUESIA"}
VALID_TIPOS = {"EFETIVOS", "SUPLENTES", "GCE", "COLIGAÇÃO"}


@dataclass(frozen=True)
class SiglaResolution:
    canonical: str
    matched: str
    confidence: float


def resolve_sigla(sigla: str) -> SiglaResolution:
    sigla_norm = (sigla or "").strip().upper()
    if sigla_norm in MASTER_SIGLA:
        return SiglaResolution(canonical=sigla_norm, matched=sigla_norm, confidence=1.0)

    for canonical, aliases in MASTER_SIGLA.items():
        if sigla_norm == canonical:
            return SiglaResolution(canonical=canonical, matched=canonical, confidence=1.0)
        candidates = [canonical, *aliases]
        matches = get_close_matches(sigla_norm.lower(), [alias.lower() for alias in candidates], n=1, cutoff=0.6)
        if matches:
            return SiglaResolution(canonical=canonical, matched=matches[0], confidence=0.8)

    return SiglaResolution(canonical=sigla_norm or "INDEPENDENTE", matched=sigla_norm, confidence=0.0)


__all__ = ["MASTER_SIGLA", "VALID_ORGAOS", "VALID_TIPOS", "SiglaResolution", "resolve_sigla"]
