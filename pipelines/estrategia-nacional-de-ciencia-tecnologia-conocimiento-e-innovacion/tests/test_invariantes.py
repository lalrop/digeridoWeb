"""Invariantes del dataset de "Estrategia Nacional de CTCI 2026" (§7).

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
SLUG = "estrategia-nacional-de-ciencia-tecnologia-conocimiento-e-innovacion"
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
    reportar(
        sin_nulos_en(
            datos["filas"], ["region", "universidades", "investigadores", "doctoradosPor1000"]
        ),
        "datos.json",
    )


def test_sin_duplicados(datos: dict) -> None:
    reportar(sin_duplicados_en(datos["filas"], ["region"]), "datos.json")


def test_valores_plausibles(datos: dict) -> None:
    reportar(en_rango(datos["filas"], "universidades", 0, 100), "datos.json")
    reportar(en_rango(datos["filas"], "investigadores", 0, 50_000), "datos.json")
    reportar(en_rango(datos["filas"], "doctoradosPor1000", 0, 50), "datos.json")


def test_las_16_regiones_de_chile(datos: dict) -> None:
    """Protege contra una transcripción incompleta o duplicada (§13): estos
    16 valores se transcribieron a mano desde una infografía, no se
    extrajeron por script — el riesgo real acá es un nombre mal tipeado o
    una región salteada, no un cambio de formato del documento.
    """
    esperadas = {
        "Arica y Parinacota", "Tarapacá", "Antofagasta", "Atacama", "Coquimbo",
        "Valparaíso", "Metropolitana", "O'Higgins", "Maule", "Ñuble", "Biobío",
        "Araucanía", "Los Ríos", "Los Lagos", "Aysén", "Magallanes",
    }
    encontradas = {f["region"] for f in datos["filas"]}
    diferencia = encontradas - esperadas or esperadas - encontradas
    assert encontradas == esperadas, f"regiones inesperadas: {diferencia}"


def test_metropolitana_concentra_mas_investigadores(datos: dict) -> None:
    """La Región Metropolitana tiene, por lejos, más investigadores que
    cualquier otra — si este test falla, algo se transcribió mal (invirtió
    dos valores, por ejemplo), no es un cambio real y silencioso del
    ecosistema científico chileno.
    """
    por_investigadores = sorted(datos["filas"], key=lambda f: f["investigadores"], reverse=True)
    assert por_investigadores[0]["region"] == "Metropolitana"
