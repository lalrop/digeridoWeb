"""Invariantes del dataset de "Informe de Percepciones de Negocios (IPN) agosto 2026" (§7).

"Un dato que no pasa el test no llega al sitio."

Escribí acá lo que TIENE que ser cierto de estos datos, no lo que es cierto hoy.
Un test que solo confirma el output actual no protege de nada; uno que codifica
una regla del dominio atrapa el día que la fuente cambia de formato.
"""

from __future__ import annotations

import json
from itertools import pairwise
from pathlib import Path

import pytest

from pipelines._common.invariantes import (
    en_rango,
    reportar,
    sin_duplicados_en,
    sin_nulos_en,
    total_cuadra,
)

RAIZ = Path(__file__).resolve().parents[3]
SLUG = "informe-de-percepciones-de-negocios-ipn-agosto-2026"
DIR_DATOS = RAIZ / "apps" / "web" / "public" / "data" / SLUG


@pytest.fixture(scope="module")
def inflacion() -> dict:
    ruta = DIR_DATOS / "datos.json"
    if not ruta.exists():
        pytest.skip(f"falta {ruta}; corré el pipeline")
    return json.loads(ruta.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def combustibles() -> dict:
    ruta = DIR_DATOS / "combustibles.json"
    if not ruta.exists():
        pytest.skip(f"falta {ruta}; corré el pipeline")
    return json.loads(ruta.read_text(encoding="utf-8"))


# ── Inflación (gráfico principal) ────────────────────────────────────────────


def test_inflacion_declara_unidad(inflacion: dict) -> None:
    assert inflacion["unidad"] and inflacion["unidad"] != "TODO"


def test_inflacion_llaves_completas(inflacion: dict) -> None:
    llaves = ["horizonte", "periodo", "media", "mediana"]
    reportar(sin_nulos_en(inflacion["filas"], llaves), "datos.json")


def test_inflacion_sin_duplicados(inflacion: dict) -> None:
    reportar(sin_duplicados_en(inflacion["filas"], ["horizonte", "periodo"]), "datos.json")


def test_inflacion_valores_plausibles(inflacion: dict) -> None:
    reportar(en_rango(inflacion["filas"], "mediana", 0, 20), "datos.json")
    reportar(en_rango(inflacion["filas"], "media", 0, 20), "datos.json")


def test_inflacion_horizontes_esperados(inflacion: dict) -> None:
    """Protege contra que una hoja del Excel cambie de nombre entre ediciones."""
    esperados = {"12 meses", "24 meses"}
    encontrados = {f["horizonte"] for f in inflacion["filas"]}
    assert encontrados == esperados, f"horizontes inesperados: {encontrados}"


def test_inflacion_serie_mensual_sin_huecos(inflacion: dict) -> None:
    """Cada horizonte tiene un dato por mes, sin saltos: si el Excel trae una
    fila vacía en el medio, esto lo nota antes que un gráfico con un hueco.
    """
    for horizonte in ("12 meses", "24 meses"):
        periodos = sorted(f["periodo"] for f in inflacion["filas"] if f["horizonte"] == horizonte)
        assert len(periodos) >= 12, f"{horizonte}: muy pocos meses ({len(periodos)})"
        anios_meses = [tuple(int(x) for x in p.split("-")) for p in periodos]
        for (a1, m1), (a2, m2) in pairwise(anios_meses):
            siguiente = (a1, m1 + 1) if m1 < 12 else (a1 + 1, 1)
            assert (a2, m2) == siguiente, f"{horizonte}: salto entre {a1}-{m1:02d} y {a2}-{m2:02d}"


def test_inflacion_trayectoria_24_meses(inflacion: dict) -> None:
    """El hallazgo de esta pieza: la mediana a 24 meses toca su mínimo en
    febrero de 2026 y se recupera hacia junio, sin volver a bajar.
    """
    tramo = {f["periodo"]: f["mediana"] for f in inflacion["filas"] if f["horizonte"] == "24 meses"}
    minimo_real = min(tramo.values())
    assert tramo["2026-02"] == minimo_real, "febrero 2026 debería ser el mínimo de toda la serie"
    assert tramo["2026-05"] > tramo["2026-02"], "mayo no se recuperó respecto del mínimo"
    assert tramo["2026-06"] >= tramo["2026-05"] - 0.01, "junio retrocedió respecto de mayo"


# ── Combustibles (gráfico de apoyo) ──────────────────────────────────────────


def test_combustibles_declara_unidad(combustibles: dict) -> None:
    assert combustibles["unidad"] and combustibles["unidad"] != "TODO"


def test_combustibles_llaves_completas(combustibles: dict) -> None:
    llaves = ["categoria", "porcentajeEmpresas"]
    reportar(sin_nulos_en(combustibles["filas"], llaves), "combustibles.json")


def test_combustibles_sin_duplicados(combustibles: dict) -> None:
    reportar(sin_duplicados_en(combustibles["filas"], ["categoria"]), "combustibles.json")


def test_combustibles_suman_100(combustibles: dict) -> None:
    reportar(
        total_cuadra(combustibles["filas"], "porcentajeEmpresas", 100, tolerancia=1),
        "combustibles.json",
    )
