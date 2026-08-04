#!/usr/bin/env python3
"""Paso 30 — publicar (§7).

Único paso que escribe dentro de ``apps/web``. Produce:

* ``public/data/ejemplo/partidas.json`` — el artefacto que consumen los gráficos
* ``src/content/digestiones/ejemplo-partidas/meta.json`` — trazabilidad

Los tamaños, hashes y conteos del ``meta.json`` los escribe este script, no una
persona: copiarlos a mano es exactamente cómo se cuela el error factual que §13
identifica como el riesgo más caro del proyecto.
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

SLUG = "ejemplo-partidas"


def main() -> int:
    limpia = INTERMEDIO / "tabla-limpia.json"
    if not limpia.exists():
        log.error("falta %s. Corré 20_limpiar.py primero.", limpia.name)
        return 1

    filas = json.loads(limpia.read_text(encoding="utf-8"))
    metricas = json.loads((INTERMEDIO / "metricas-original.json").read_text(encoding="utf-8"))
    registro = json.loads((CRUDO / "registro.json").read_text(encoding="utf-8"))

    # ── Artefactos para el front ───────────────────────────────────────────
    datos = {
        "_aviso": (
            "DATOS SINTÉTICOS. Generados para probar el sistema de diseño de "
            "digerido. No describen ningún documento real y no deben citarse."
        ),
        "unidad": "MM$ de 2026",
        "partidas": filas,
        "total": sum(f["monto"] for f in filas),
    }

    # `minificar=False` solo en esta pieza de andamiaje: el archivo se lee a mano
    # al revisar el esqueleto. Una digestión real publica minificado.
    json_art = publicar_json(datos, "ejemplo/partidas.json", minificar=False, filas=len(filas))
    csv_art = publicar_csv(filas, "ejemplo/partidas.csv", decimales=1)

    # ── meta.json: trazabilidad ────────────────────────────────────────────
    escribir_meta(
        SLUG,
        {
            "_aviso": (
                "Pieza de andamiaje. Todas las cifras son sintéticas y el "
                "documento original no existe."
            ),
            "slug": SLUG,
            "pipeline": SLUG,
            "generado": date.today().isoformat(),
            "fuente": {
                "titulo": "Documento sintético de prueba (no es un documento real)",
                "organismo": "ORGANISMO DE EJEMPLO",
                "url": registro["url"],
                "sha256": registro["sha256"],
                "bytes": registro["bytes"],
                "paginas": metricas["paginas"],
                "fechaDescarga": registro["fecha_descarga"],
                "nota": (
                    "El sha256 es del documento sintético generado por "
                    "00_descargar.py, que es lo único que existe realmente."
                ),
            },
            "etiqueta": {
                "palabrasOriginal": metricas["palabrasOriginal"],
                "siglasSinDefinir": metricas["siglasSinDefinir"],
                "legibilidadOriginal": metricas["legibilidadOriginal"],
                "nivelOriginal": metricas["nivelOriginal"],
                "tiempoLecturaOriginal": metricas["tiempoLecturaOriginal"],
                "siglasNoDefinidas": metricas["detalle"]["siglas"],
            },
            "artefactos": [json_art.como_dict(), csv_art.como_dict()],
            "invariantes": {
                "total_cuadra": True,
                "sin_nulos_en_llaves": True,
                "sin_duplicados": True,
                "nota": "Verificadas en 20_limpiar.py y en tests/test_invariantes.py.",
            },
        },
    )

    log.info(
        "listo. Copiá al frontmatter: legibilidadOriginal=%d, palabrasOriginal=%d, "
        "siglasSinDefinir=%d, tiempoLectura.original=%d",
        metricas["legibilidadOriginal"],
        metricas["palabrasOriginal"],
        metricas["siglasSinDefinir"],
        metricas["tiempoLecturaOriginal"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
