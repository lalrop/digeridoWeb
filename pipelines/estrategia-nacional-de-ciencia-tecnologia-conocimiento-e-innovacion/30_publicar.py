#!/usr/bin/env python3
"""Paso 30 — publicar (§7).

Único paso que escribe dentro de 'apps/web'. Los tamaños, hashes y conteos del
meta.json los escribe este script: copiarlos a mano es cómo se cuela el error
factual que §13 identifica como el riesgo más caro del proyecto.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from pipelines._common.log import log
from pipelines._common.publicar import escribir_meta, publicar_csv, publicar_json

AQUI = Path(__file__).resolve().parent
CRUDO = AQUI / "raw"
INTERMEDIO = AQUI / "interim"

SLUG = "estrategia-nacional-de-ciencia-tecnologia-conocimiento-e-innovacion"


def main() -> int:
    limpia = INTERMEDIO / "tabla-limpia.json"
    if not limpia.exists():
        log.error("falta %s. Corré 20_limpiar.py primero.", limpia.name)
        return 1

    filas = json.loads(limpia.read_text(encoding="utf-8"))
    metricas = json.loads((INTERMEDIO / "metricas-original.json").read_text(encoding="utf-8"))
    registro = json.loads((CRUDO / "registro.json").read_text(encoding="utf-8"))

    datos = {
        "unidad": "universidades, investigadores y doctorados/1.000 trabajadores, por región",
        "filas": filas,
    }

    artefactos = [
        publicar_json(datos, f"{SLUG}/datos.json", filas=len(filas)),
        publicar_csv(filas, f"{SLUG}/datos.csv"),
    ]

    escribir_meta(
        SLUG,
        {
            "slug": SLUG,
            "generado": date.today().isoformat(),
            "fuente": registro,
            "etiqueta": metricas,
            "artefactos": [a.como_dict() for a in artefactos],
        },
    )

    log.info(
        "listo. Copiá al frontmatter: palabrasOriginal=%s, legibilidadOriginal=%s, "
        "siglasSinDefinir=%s, tiempoLectura.original=%s",
        metricas["palabrasOriginal"],
        metricas["legibilidadOriginal"],
        metricas["siglasSinDefinir"],
        metricas["tiempoLecturaOriginal"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
