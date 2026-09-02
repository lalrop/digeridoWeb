#!/usr/bin/env python3
"""Paso 10 — extraer (§7).

Extrae y NO corrige: limpiar es el paso 20. Mezclar los dos hace imposible saber
si un número raro venía del documento o lo produjo el script.

Mide también el documento original para la Etiqueta Nutricional.
"""

from __future__ import annotations

import json
from pathlib import Path

import pdfplumber

from pipelines._common.legibilidad import detectar_siglas, legibilidad, tiempo_lectura
from pipelines._common.log import log

AQUI = Path(__file__).resolve().parent
CRUDO = AQUI / "raw"
INTERMEDIO = AQUI / "interim"
PDF = CRUDO / "ENCTCI26.pdf"

# Páginas 112 y 113 del PDF (índice 1): "Capacidades de CTCI de Chile
# distribuidas por región" — un mapa infográfico de Chile, no una tabla de
# texto. pdfplumber.extract_text() en esas páginas devuelve los números y
# nombres de región MEZCLADOS y algunos nombres literalmente al revés
# ("ACIRA" en vez de "ARICA"): el layout es circular/radial, con etiquetas
# rotadas alrededor del mapa, y la extracción de texto sigue el orden de los
# glifos en el stream del PDF, no el orden visual.
#
# Por eso estos 16 valores NO se extraen por script: se transcribieron a
# mano, leyendo la página renderizada como imagen (PyMuPDF a 3x de zoom,
# páginas 112 y 113) — mismo criterio que la Tabla I.2 del Informe de
# Sistemas de Pago, donde el PDF original también traía el dato solo como
# imagen. Los tres campos por región son los que declara la leyenda de la
# propia infografía (p.113): universidades, investigadores, y personas con
# doctorado trabajando cada 1.000 trabajadores.
CAPACIDADES_POR_REGION = [
    {"region": "Arica y Parinacota", "universidades": 4, "investigadores": 234,
     "doctoradosPor1000": "1,5"},
    {"region": "Tarapacá", "universidades": 4, "investigadores": 99, "doctoradosPor1000": "0,6"},
    {"region": "Antofagasta", "universidades": 6, "investigadores": 256,
     "doctoradosPor1000": "1,3"},
    {"region": "Atacama", "universidades": 4, "investigadores": 40, "doctoradosPor1000": "0,7"},
    {"region": "Coquimbo", "universidades": 7, "investigadores": 137, "doctoradosPor1000": "0,9"},
    {"region": "Valparaíso", "universidades": 12, "investigadores": 925,
     "doctoradosPor1000": "2,5"},
    {"region": "Metropolitana", "universidades": 28, "investigadores": 6139,
     "doctoradosPor1000": "2,6"},
    {"region": "O'Higgins", "universidades": 5, "investigadores": 266, "doctoradosPor1000": "0,3"},
    {"region": "Maule", "universidades": 7, "investigadores": 301, "doctoradosPor1000": "1,5"},
    {"region": "Ñuble", "universidades": 3, "investigadores": 149, "doctoradosPor1000": "1,6"},
    {"region": "Biobío", "universidades": 10, "investigadores": 658, "doctoradosPor1000": "2,7"},
    {"region": "Araucanía", "universidades": 8, "investigadores": 162, "doctoradosPor1000": "1,4"},
    {"region": "Los Ríos", "universidades": 6, "investigadores": 372, "doctoradosPor1000": "4,3"},
    {"region": "Los Lagos", "universidades": 7, "investigadores": 162, "doctoradosPor1000": "0,8"},
    {"region": "Aysén", "universidades": 5, "investigadores": 59, "doctoradosPor1000": "1,1"},
    {"region": "Magallanes", "universidades": 4, "investigadores": 86, "doctoradosPor1000": "2,1"},
]


def extraer_texto() -> str:
    with pdfplumber.open(PDF) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)


def main() -> int:
    INTERMEDIO.mkdir(parents=True, exist_ok=True)

    (INTERMEDIO / "tabla-cruda.json").write_text(
        json.dumps(CAPACIDADES_POR_REGION, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    log.info(
        "transcritas %d regiones (ver comentario de origen en este script)",
        len(CAPACIDADES_POR_REGION),
    )

    texto = extraer_texto()
    leg = legibilidad(texto)
    siglas = detectar_siglas(texto)

    (INTERMEDIO / "metricas-original.json").write_text(
        json.dumps(
            {
                "palabrasOriginal": leg.palabras,
                "siglasSinDefinir": siglas.sin_definir,
                "legibilidadOriginal": leg.indice,
                "nivelOriginal": leg.nivel,
                "tiempoLecturaOriginal": tiempo_lectura(leg.palabras),
                "detalle": leg.como_dict(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    log.info(
        "legibilidad %d/100 (%s) · %d palabras · %d siglas sin definir",
        leg.indice,
        leg.nivel,
        leg.palabras,
        siglas.sin_definir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
