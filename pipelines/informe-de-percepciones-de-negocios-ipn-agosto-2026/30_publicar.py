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

SLUG = "informe-de-percepciones-de-negocios-ipn-agosto-2026"


def main() -> int:
    inflacion_path = INTERMEDIO / "inflacion-limpia.json"
    combustibles_path = INTERMEDIO / "combustibles-limpia.json"
    if not inflacion_path.exists() or not combustibles_path.exists():
        log.error("faltan archivos limpios. Corré 20_limpiar.py primero.")
        return 1

    inflacion = json.loads(inflacion_path.read_text(encoding="utf-8"))
    combustibles = json.loads(combustibles_path.read_text(encoding="utf-8"))
    metricas = json.loads((INTERMEDIO / "metricas-original.json").read_text(encoding="utf-8"))
    registro = json.loads((CRUDO / "registro.json").read_text(encoding="utf-8"))

    # Mediana y media de expectativas de inflación EDEP, a 12 y a 24 meses,
    # serie mensual completa (2023-2026), tal como la publica el Banco
    # Central en el Excel adjunto al IPN — es el gráfico principal.
    datos_inflacion = {"unidad": "% (EDEP, mensual)", "filas": inflacion}

    # Distribución de qué esperan las empresas para el precio de los
    # combustibles en los próximos 6 meses — gráfico de apoyo.
    datos_combustibles = {"unidad": "% de empresas", "filas": combustibles}

    artefactos = [
        publicar_json(datos_inflacion, f"{SLUG}/datos.json", filas=len(inflacion)),
        publicar_csv(inflacion, f"{SLUG}/datos.csv"),
        publicar_json(datos_combustibles, f"{SLUG}/combustibles.json", filas=len(combustibles)),
        publicar_csv(combustibles, f"{SLUG}/combustibles.csv"),
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
