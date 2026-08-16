#!/usr/bin/env python3
"""Paso 00 — descargar (§7).

Idempotente y con caché: repetir no vuelve a golpear al organismo emisor.
La salida cruda va a 'raw/', que está gitignored.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

from pipelines._common.descarga import descargar, verificar_hash
from pipelines._common.log import log

AQUI = Path(__file__).resolve().parent
CRUDO = AQUI / "raw"
SLUG = "informe-de-sistemas-de-pago-agosto-2026"

# Informe de Sistemas de Pago (ISP), agosto 2026, Banco Central de Chile.
# La descarga automática está bloqueada por Incapsula (bot-detection) en
# bcentral.cl: este PDF se descargó a mano y se registró con
# pipelines/_common/descarga.py invocado directamente (no vía este script).
URL = "https://www.bcentral.cl/documents/33528/8545313/Informe+de+Sistemas+de+Pago+Agosto+2026.pdf/fd0f320e-be20-7680-a0db-511554d82029?t=1786050167608"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forzar", action="store_true", help="ignora el caché")
    args = parser.parse_args()

    if not URL:
        log.error("definí URL en este script antes de correrlo")
        return 1

    # `URL.rsplit("/", 1)[-1]` se queda con el query string (?sfvrsn=...) pegado
    # al nombre: Windows rechaza el "?" en un nombre de archivo. urlsplit().path
    # descarta query y fragment antes de tomar el último segmento.
    destino = CRUDO / urlsplit(URL).path.rsplit("/", 1)[-1]
    reg = descargar(URL, destino, forzar=args.forzar)

    # Avisa si el organismo reemplazó el documento sin cambiar la URL (§13).
    meta = AQUI.parent.parent / "apps/web/src/content/digestiones" / SLUG / "meta.json"
    if not verificar_hash(meta, URL, reg.sha256):
        return 1

    (CRUDO / "registro.json").write_text(
        json.dumps(reg.como_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    log.info("sha256 %s", reg.sha256)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
