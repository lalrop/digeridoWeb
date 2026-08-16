"""Invariantes del dataset de "Informe de Sistemas de Pago (ISP) agosto 2026" (§7).

"Un dato que no pasa el test no llega al sitio."

Escribí acá lo que TIENE que ser cierto de estos datos, no lo que es cierto hoy.
Un test que solo confirma el output actual no protege de nada; uno que codifica
una regla del dominio atrapa el día que la fuente cambia de formato.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipelines._common.invariantes import en_rango, reportar, sin_duplicados_en, sin_nulos_en

RAIZ = Path(__file__).resolve().parents[3]
SLUG = "informe-de-sistemas-de-pago-agosto-2026"
DIR_DATOS = RAIZ / "apps" / "web" / "public" / "data" / SLUG


@pytest.fixture(scope="module")
def costo_tef() -> dict:
    ruta = DIR_DATOS / "datos.json"
    if not ruta.exists():
        pytest.skip(f"falta {ruta}; corré el pipeline")
    return json.loads(ruta.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def acceso_efectivo() -> dict:
    ruta = DIR_DATOS / "acceso-efectivo.json"
    if not ruta.exists():
        pytest.skip(f"falta {ruta}; corré el pipeline")
    return json.loads(ruta.read_text(encoding="utf-8"))


# ── Costo TEF (gráfico principal) ────────────────────────────────────────────


def test_costo_tef_declara_unidad(costo_tef: dict) -> None:
    assert costo_tef["unidad"] and costo_tef["unidad"] != "TODO"


def test_costo_tef_llaves_completas(costo_tef: dict) -> None:
    reportar(sin_nulos_en(costo_tef["filas"], ["entidad", "monto", "porcentaje"]), "datos.json")


def test_costo_tef_sin_duplicados(costo_tef: dict) -> None:
    reportar(sin_duplicados_en(costo_tef["filas"], ["entidad", "monto"]), "datos.json")


def test_costo_tef_valores_plausibles(costo_tef: dict) -> None:
    reportar(en_rango(costo_tef["filas"], "porcentaje", 0, 100), "datos.json")


def test_costo_tef_cinco_entidades_tres_montos(costo_tef: dict) -> None:
    """Protege contra una transcripción incompleta de la TABLA I.2."""
    entidades = {f["entidad"] for f in costo_tef["filas"]}
    montos = {f["monto"] for f in costo_tef["filas"]}
    assert len(entidades) == 5, f"se esperaban 5 entidades, hay {len(entidades)}"
    assert montos == {1000, 20000, 50000}, f"montos inesperados: {montos}"
    assert len(costo_tef["filas"]) == 15


def test_costo_tef_hallazgo_iniciador_1_es_el_mas_caro(costo_tef: dict) -> None:
    """El hallazgo de esta pieza: aceptar un pago chico ($1.000) por TEF puede
    costar hasta 42,1% del monto — el máximo de todo el dataset.
    """
    fila_maxima = max(costo_tef["filas"], key=lambda f: f["porcentaje"])
    assert fila_maxima["entidad"] == "Iniciador de Pagos 1"
    assert fila_maxima["monto"] == 1000
    assert fila_maxima["porcentaje"] == 42.1


def test_costo_tef_banco_1_es_plano(costo_tef: dict) -> None:
    """Contraste del hallazgo: el proveedor más barato cobra lo mismo sin
    importar el monto — evidencia de que la variación no es un límite técnico.
    """
    valores = {f["porcentaje"] for f in costo_tef["filas"] if f["entidad"] == "Banco 1"}
    assert valores == {1.0}


# ── Acceso a efectivo (gráfico de apoyo) ─────────────────────────────────────


def test_acceso_efectivo_declara_unidad(acceso_efectivo: dict) -> None:
    assert acceso_efectivo["unidad"] and acceso_efectivo["unidad"] != "TODO"


def test_acceso_efectivo_llaves_completas(acceso_efectivo: dict) -> None:
    reportar(
        sin_nulos_en(acceso_efectivo["filas"], ["canal", "porcentaje"]), "acceso-efectivo.json"
    )


def test_acceso_efectivo_sin_duplicados(acceso_efectivo: dict) -> None:
    reportar(sin_duplicados_en(acceso_efectivo["filas"], ["canal"]), "acceso-efectivo.json")


def test_acceso_efectivo_dos_canales(acceso_efectivo: dict) -> None:
    canales = {f["canal"] for f in acceso_efectivo["filas"]}
    assert canales == {"Cajeros automáticos", "Cajas Vecinas"}
