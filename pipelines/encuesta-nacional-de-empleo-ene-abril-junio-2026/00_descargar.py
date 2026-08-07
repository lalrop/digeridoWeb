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
SLUG = "encuesta-nacional-de-empleo-ene-abril-junio-2026"

# TODO: la URL del documento original.
URL = "https://www.ine.gob.cl/docs/default-source/ocupacion-y-desocupacion/boletines/2026/nacional/ene-nacional-333.pdf?sfvrsn=591ec29a_4"


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
