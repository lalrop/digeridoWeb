#!/usr/bin/env python3
"""Paso 10 — extraer (§7).

Extrae y NO corrige: limpiar es el paso 20. Mezclar los dos hace imposible saber
si un número raro venía del documento o lo produjo el script.

Mide también el documento original para la Etiqueta Nutricional.

Los gráficos del PDF son imágenes (igual que en el IPN antes de recibir el
Excel de apoyo): `pdfplumber.extract_tables()` no los recupera. Pero este
informe SÍ trae dos tablas de texto plano, extraíbles sin ambigüedad:

  * TABLA I.2 "Costo directo de aceptar pagos con TEF" — página 21 del PDF.
  * Los dos porcentajes de canal de acceso a efectivo del RECUADRO I.2
    "Distribución del Efectivo" — página 22 del PDF.

Ambas se transcriben a mano acá porque `extract_tables()` las devuelve rotas
(celdas vacías, columnas fusionadas): la tabla de acceso a efectivo no es ni
siquiera una tabla en el PDF, son dos cifras dentro de un párrafo. La
transcripción se verificó línea por línea contra el texto ya extraído en
`interim/texto-completo.txt`.
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
PDF = CRUDO / "informe-sistemas-de-pago-agosto-2026.pdf"

# TABLA I.2, página 21 del PDF: costo de aceptar un pago vía TEF (Transferencia
# Electrónica de Fondos), como % del monto, según el proveedor y el monto pagado.
COSTO_TEF = [
    {"entidad": "Iniciador de Pagos 1", "monto": 1000, "porcentaje": 42.1},
    {"entidad": "Iniciador de Pagos 1", "monto": 20000, "porcentaje": 2.8},
    {"entidad": "Iniciador de Pagos 1", "monto": 50000, "porcentaje": 1.5},
    {"entidad": "Iniciador de Pagos 2", "monto": 1000, "porcentaje": 15.5},
    {"entidad": "Iniciador de Pagos 2", "monto": 20000, "porcentaje": 1.7},
    {"entidad": "Iniciador de Pagos 2", "monto": 50000, "porcentaje": 1.3},
    {"entidad": "Iniciador de Pagos 3", "monto": 1000, "porcentaje": 3.2},
    {"entidad": "Iniciador de Pagos 3", "monto": 20000, "porcentaje": 3.2},
    {"entidad": "Iniciador de Pagos 3", "monto": 50000, "porcentaje": 3.2},
    {"entidad": "SAG 1", "monto": 1000, "porcentaje": 8.7},
    {"entidad": "SAG 1", "monto": 20000, "porcentaje": 1.3},
    {"entidad": "SAG 1", "monto": 50000, "porcentaje": 0.8},
    {"entidad": "Banco 1", "monto": 1000, "porcentaje": 1.0},
    {"entidad": "Banco 1", "monto": 20000, "porcentaje": 1.0},
    {"entidad": "Banco 1", "monto": 50000, "porcentaje": 1.0},
]

# RECUADRO I.2, página 22 del PDF: canal principal de obtención de efectivo,
# % de la población que lo usa (ENUPE 2025).
ACCESO_EFECTIVO = [
    {"canal": "Cajeros automáticos", "porcentaje": 77.0},
    {"canal": "Cajas Vecinas", "porcentaje": 47.0},
]


def extraer_texto() -> str:
    with pdfplumber.open(PDF) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)


def extraer_costo_tef() -> list[dict]:
    return COSTO_TEF


def extraer_acceso_efectivo() -> list[dict]:
    return ACCESO_EFECTIVO


def main() -> int:
    INTERMEDIO.mkdir(parents=True, exist_ok=True)

    (INTERMEDIO / "costo-tef-cruda.json").write_text(
        json.dumps(extraer_costo_tef(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (INTERMEDIO / "acceso-efectivo-cruda.json").write_text(
        json.dumps(extraer_acceso_efectivo(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
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
