#!/usr/bin/env python3
"""Paso 10 — extraer (§7).

En una digestión real acá viven ``pdfplumber`` y ``camelot``. La regla que
importa, independiente de la herramienta: la extracción es **reproducible** y no
corrige nada. Limpiar es el paso 20; mezclar los dos hace imposible saber si un
número raro vino del documento o del script.

Este paso también mide el documento original para la Etiqueta Nutricional:
palabras, siglas sin definir y legibilidad Fernández-Huerta.
"""

from __future__ import annotations

import json
from pathlib import Path

from pipelines._common.legibilidad import detectar_siglas, legibilidad, tiempo_lectura
from pipelines._common.log import log

AQUI = Path(__file__).resolve().parent
CRUDO = AQUI / "raw"
INTERMEDIO = AQUI / "interim"


def main() -> int:
    fuente = CRUDO / "documento-sintetico.json"
    if not fuente.exists():
        log.error("falta %s. Corré 00_descargar.py primero.", fuente.name)
        return 1

    doc = json.loads(fuente.read_text(encoding="utf-8"))
    INTERMEDIO.mkdir(parents=True, exist_ok=True)

    # ── Tabla cruda, tal como viene ────────────────────────────────────────
    (INTERMEDIO / "tabla-cruda.json").write_text(
        json.dumps(doc["tabla"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    log.info("extraídas %d filas", len(doc["tabla"]))

    # ── Métricas del documento original para la etiqueta (§5) ──────────────
    texto = doc["texto"]
    leg = legibilidad(texto)
    siglas = detectar_siglas(texto)

    metricas = {
        "paginas": doc["paginas"],
        "palabrasOriginal": leg.palabras,
        "siglasSinDefinir": siglas.sin_definir,
        "legibilidadOriginal": leg.indice,
        "nivelOriginal": leg.nivel,
        "tiempoLecturaOriginal": tiempo_lectura(leg.palabras),
        "detalle": {
            "frases": leg.frases,
            "silabasPorPalabra": leg.silabas_por_palabra,
            "palabrasPorFrase": leg.palabras_por_frase,
            "siglas": [s["sigla"] for s in siglas.encontradas if not s["definida"]],
        },
    }

    (INTERMEDIO / "metricas-original.json").write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    log.info(
        "legibilidad del original: %d/100 (%s) · %d palabras · %d siglas sin definir",
        leg.indice,
        leg.nivel,
        leg.palabras,
        siglas.sin_definir,
    )
    log.info("total declarado por el documento: %s", f"{doc['total_declarado']:,}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
