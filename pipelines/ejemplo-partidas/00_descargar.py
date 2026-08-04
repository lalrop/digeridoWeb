#!/usr/bin/env python3
"""Paso 00 — descargar (§7).

Pipeline de andamiaje. En una digestión real este script baja el documento
original y registra su hash; acá **genera** un documento sintético, porque el
esqueleto no debe traer un PDF de un organismo real ni afirmar un hash que no
verificó nadie.

La estructura y las convenciones son las de un pipeline de verdad:

* idempotente: no regenera si el archivo ya está
* la salida cruda va a ``raw/``, que está gitignored
* devuelve un registro con sha256, bytes y fecha
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import date
from pathlib import Path

from pipelines._common.descarga import sha256_de
from pipelines._common.log import log

AQUI = Path(__file__).resolve().parent
CRUDO = AQUI / "raw"

# Semilla fija: el "documento" sintético debe ser el mismo en cada corrida, o
# los tests de invariantes no significan nada.
SEMILLA = 20260804

# Un informe de 412 páginas ronda las 180 mil palabras. El documento sintético
# apunta a ese volumen para que el tiempo de lectura y la legibilidad que salen
# del paso 10 sean del orden de los de un documento real.
PALABRAS_OBJETIVO = 180_000

PARTIDAS = [
    "Salud",
    "Educación",
    "Trabajo y Previsión",
    "Obras Públicas",
    "Interior",
    "Vivienda",
    "Justicia",
    "Agricultura",
]


def generar_documento_sintetico() -> dict[str, object]:
    """Simula el texto y las tablas que saldrían de un PDF real.

    Incluye a propósito la basura típica de un documento oficial: siglas sin
    definir, frases largas, cifras con separador de miles. Es lo que hace que la
    métrica de legibilidad del paso 10 tenga algo real que medir.
    """
    rng = random.Random(SEMILLA)

    montos = [4820, 3910, 3140, 1980, 1520, 1310, 870, 540]
    variaciones = [31.4, 10.2, 8.7, -4.1, 6.3, 12.8, -2.4, 1.9]

    # Volumen realista: un informe de 412 páginas ronda las 180 mil palabras.
    # Importa que el documento sintético tenga el tamaño de uno real, porque de
    # ahí salen las cifras de la Etiqueta Nutricional; con un texto de tres
    # párrafos, el "tiempo de lectura original" sería de un minuto y la
    # comparación con el digerido no demostraría nada.
    cuerpo = (
        "No obstante lo precedentemente expuesto, la individualización de las "
        "asignaciones consignadas en el presente instrumento se entenderá "
        "supeditada a la verificación de la concurrencia copulativa de los "
        "requisitos establecidos reglamentariamente en la normativa "
        "presupuestaria vigente, sin perjuicio de las facultades "
        "interpretativas que corresponden a la DIPRES en el ejercicio de sus "
        "atribuciones legales.\n\n"
        "La SUBDERE informará trimestralmente al FNDR respecto del avance "
        "físico y financiero de las iniciativas de inversión, conforme a lo "
        "instruido mediante el PMU y el PMB, debiendo remitir los antecedentes "
        "de respaldo a la DIPRES dentro de los plazos que al efecto se "
        "establezcan.\n\n"
    )
    detalle = ""
    for p, m, v in zip(PARTIDAS, montos, variaciones, strict=True):
        detalle += (
            f"Partida {p}: la asignación asciende a MM$ {m:,}".replace(",", ".")
            + f", lo que representa una variación de {v} por ciento "
            "respecto del ejercicio inmediatamente anterior.\n"
        )

    # Se repite el bloque hasta alcanzar el volumen objetivo, con un encabezado
    # en mayúsculas por capítulo — que es justamente lo que el detector de siglas
    # tiene que aprender a ignorar.
    bloque = cuerpo + detalle + "\n"
    palabras_por_bloque = len(bloque.split())
    repeticiones = max(1, round(PALABRAS_OBJETIVO / palabras_por_bloque))

    partes = ["INFORME DE EJECUCIÓN PRESUPUESTARIA SINTÉTICO\n\n"]
    for i in range(repeticiones):
        partes.append(f"CAPÍTULO {i + 1} - ANTECEDENTES GENERALES\n\n")
        partes.append(bloque)
    texto = "".join(partes)

    return {
        "_aviso": (
            "DOCUMENTO SINTÉTICO. Generado por 00_descargar.py para probar el "
            "pipeline. No corresponde a ningún documento real."
        ),
        "paginas": 412,
        "texto": texto,
        "tabla": [
            {"partida": p, "monto": m, "variacion": v, "destacado": p == "Salud"}
            for p, m, v in zip(PARTIDAS, montos, variaciones, strict=True)
        ],
        # El total que "declara el documento": el paso 20 lo verifica contra la
        # suma de las partes. Acá cuadra; en un documento real, a veces no.
        "total_declarado": sum(montos),
        "ruido": rng.random(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forzar", action="store_true", help="regenera aunque exista")
    args = parser.parse_args()

    CRUDO.mkdir(parents=True, exist_ok=True)
    destino = CRUDO / "documento-sintetico.json"

    if destino.exists() and not args.forzar:
        log.info("cache: %s (usá --forzar para regenerar)", destino.name)
    else:
        doc = generar_documento_sintetico()
        destino.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        log.info("generado documento sintético: %s", destino.name)

    registro = {
        "url": "https://example.org/documento-sintetico-de-prueba.pdf",
        "ruta": str(destino.relative_to(AQUI)),
        "sha256": sha256_de(destino),
        "bytes": destino.stat().st_size,
        "fecha_descarga": date.today().isoformat(),
        "sintetico": True,
    }
    (CRUDO / "registro.json").write_text(
        json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    log.info("sha256 %s…", registro["sha256"][:16])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
