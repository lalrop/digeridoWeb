"""Invariantes del dataset de "Encuesta nacional de empleo (ENE) abril - junio 2026" (§7).

"Un dato que no pasa el test no llega al sitio."

Escribí acá lo que TIENE que ser cierto de estos datos, no lo que es cierto hoy.
Un test que solo confirma el output actual no protege de nada; uno que codifica
una regla del dominio atrapa el día que la fuente cambia de formato.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipelines._common.invariantes import (
    en_rango,
    reportar,
    sin_duplicados_en,
    sin_nulos_en,
)

RAIZ = Path(__file__).resolve().parents[3]
SLUG = "encuesta-nacional-de-empleo-ene-abril-junio-2026"
ARTEFACTO = RAIZ / "apps" / "web" / "public" / "data" / SLUG / "datos.json"


@pytest.fixture(scope="module")
def datos() -> dict:
    if not ARTEFACTO.exists():
        pytest.skip(f"falta {ARTEFACTO}; corré el pipeline")
    return json.loads(ARTEFACTO.read_text(encoding="utf-8"))


def test_declara_unidad(datos: dict) -> None:
    """Una cifra sin unidad ni año base no significa nada (§10)."""
    assert datos["unidad"] and datos["unidad"] != "TODO"


def test_llaves_completas(datos: dict) -> None:
    reportar(sin_nulos_en(datos["filas"], ["sector", "variacion12meses"]), "datos.json")


def test_sin_duplicados(datos: dict) -> None:
    reportar(sin_duplicados_en(datos["filas"], ["sector"]), "datos.json")


def test_valores_plausibles(datos: dict) -> None:
    # Variación porcentual interanual: negativa es válida (sectores que
    # perdieron empleo), pero ±100% ya es implausible para este indicador.
    reportar(en_rango(datos["filas"], "variacion12meses", -100, 100), "datos.json")


def test_sectores_esperados(datos: dict) -> None:
    """Protege contra una extracción mal alineada (§13): si el párrafo del
    boletín cambia de redacción y la regex agarra otra frase, esto lo nota
    antes que un lector.
    """
    esperados = {
        "Transporte",
        "Servicios administrativos y de apoyo",
        "Actividades de salud",
        "Actividades profesionales",
        "Comunicaciones",
        "Minería",
        "Administración pública",
    }
    encontrados = {f["sector"] for f in datos["filas"]}
    diferencia = encontrados - esperados or esperados - encontrados
    assert encontrados == esperados, f"sectores inesperados: {diferencia}"
