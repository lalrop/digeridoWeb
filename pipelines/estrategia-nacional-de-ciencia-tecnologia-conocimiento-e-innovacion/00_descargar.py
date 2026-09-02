#!/usr/bin/env python3
"""Paso 00 — descargar (§7).

Idempotente y con caché: repetir no vuelve a golpear al organismo emisor.
La salida cruda va a 'raw/', que está gitignored.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipelines._common.descarga import descargar, verificar_hash
from pipelines._common.log import log

AQUI = Path(__file__).resolve().parent
CRUDO = AQUI / "raw"
SLUG = "estrategia-nacional-de-ciencia-tecnologia-conocimiento-e-innovacion"

# El propio documento se cita a sí mismo como "Disponible en versión digital
# https://estrategia.consejoctci.cl" (portada, p.1) — esa es la URL
# declarada. A la fecha en que se escribió este script, ese subdominio no
# resuelve (DNS) y `docs.consejoctci.cl` respondió con un certificado TLS
# vencido: no se pudo verificar en vivo desde esta sesión. El PDF llegó
# subido a mano por el usuario, no descargado por este script — igual que
# pasó con bcentral.cl en la pieza del ISP, pero acá la causa es que el
# sitio 2026 del Consejo CTCI todavía no está completamente publicado, no
# un bloqueo de bot.
#
# `destino` se fija a mano (no se deriva de la URL con urlsplit, como en el
# resto de los pipelines): la URL es solo el dominio, sin ruta de archivo, y
# derivar el nombre desde ahí daría un destino vacío.
URL = "https://estrategia.consejoctci.cl"
NOMBRE_ARCHIVO = "ENCTCI26.pdf"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forzar", action="store_true", help="ignora el caché")
    args = parser.parse_args()

    destino = CRUDO / NOMBRE_ARCHIVO
    if not destino.exists():
        log.error(
            "falta %s. Este documento no se pudo verificar por descarga automática "
            "(ver comentario de URL arriba) — subilo a mano a esa ruta.",
            destino,
        )
        return 1

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
