#!/usr/bin/env python3
"""Paso 10 — extraer (§7).

Extrae y NO corrige: limpiar es el paso 20. Mezclar los dos hace imposible saber
si un número raro venía del documento o lo produjo el script.

Mide también el documento original para la Etiqueta Nutricional.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber

from pipelines._common.legibilidad import detectar_siglas, legibilidad, tiempo_lectura
from pipelines._common.log import log

AQUI = Path(__file__).resolve().parent
CRUDO = AQUI / "raw"
INTERMEDIO = AQUI / "interim"
PDF = CRUDO / "ene-nacional-333.pdf"

# El párrafo de "Actividad económica" (página 3, columna izquierda) es el
# único lugar del boletín donde la variación por sector aparece como TEXTO:
# el gráfico de evolución de la tasa de desocupación es una imagen, no datos
# seleccionables. El layout es a dos columnas; recortar a la mitad izquierda
# de la página evita que pdfplumber intercale el pie del gráfico de la
# derecha en medio de las palabras.
PAGINA_SECTORES = 2
ANCHO_COLUMNA_IZQUIERDA = 0.48  # fracción del ancho de página; ajustado a mano
# para esta edición hasta que ningún carácter de la columna derecha se cuele.
INICIO_PARRAFO = "se fundamentó por"
# Corta antes de "Los hombres ocupados...": esa frase repite "transporte" y
# "salud" con OTROS porcentajes (desglose por sexo, no por sector), y un
# nombre de sector buscado dos veces encontraría el valor equivocado primero.
FIN_PARRAFO = "Los hombres ocupados"

# Los 7 sectores mencionados en esta edición, en el orden en que aparecen.
# Se listan a mano en vez de inferirlos con una regex genérica: el párrafo es
# prosa, no una tabla, y "N palabras antes del paréntesis" no tiene un límite
# fijo ("transporte" vs. "servicios administrativos y de apoyo").
SECTORES = [
    "transporte",
    "servicios administrativos y de apoyo",
    "actividades de salud",
    "actividades profesionales",
    "comunicaciones",
    "minería",
    "administración pública",
]


def extraer_texto() -> str:
    with pdfplumber.open(PDF) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)


def extraer_tablas() -> list[dict]:
    """Variación de personas ocupadas por sector económico, a doce meses.

    No es una tabla del PDF (pdfplumber no encuentra ninguna con estos datos):
    es texto corrido en un párrafo a dos columnas. Se aísla el tramo relevante
    por texto ancla y se busca, para cada sector conocido, el "(±N,N%)" que
    lo sigue.
    """
    with pdfplumber.open(PDF) as pdf:
        pagina = pdf.pages[PAGINA_SECTORES]
        ancho = pagina.width * ANCHO_COLUMNA_IZQUIERDA
        columna_izquierda = pagina.crop((0, 0, ancho, pagina.height))
        texto_pagina = columna_izquierda.extract_text() or ""

    texto = texto_pagina.replace("-\n", "").replace("\n", " ")

    inicio = texto.find(INICIO_PARRAFO)
    fin = texto.find(FIN_PARRAFO)
    if inicio == -1 or fin == -1:
        raise RuntimeError(
            "no encontré el párrafo de variación por sector; el boletín cambió de formato "
            "respecto de la edición sobre la que se escribió este extractor"
        )
    parrafo = texto[inicio:fin]

    filas = []
    for sector in SECTORES:
        m = re.search(rf"{re.escape(sector)}\s*\((-?\d+,\d+)%\)", parrafo, flags=re.IGNORECASE)
        if not m:
            raise RuntimeError(f"no encontré el porcentaje de '{sector}' en: {parrafo!r}")
        filas.append({"sector": sector, "variacion12meses": m.group(1)})

    log.info("párrafo fuente: %s", parrafo)
    for f in filas:
        log.info("  %s: %s%%", f["sector"], f["variacion12meses"])

    return filas


def main() -> int:
    INTERMEDIO.mkdir(parents=True, exist_ok=True)

    filas = extraer_tablas()
    (INTERMEDIO / "tabla-cruda.json").write_text(
        json.dumps(filas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
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
