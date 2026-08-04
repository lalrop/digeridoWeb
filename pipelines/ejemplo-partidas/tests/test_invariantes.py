"""Invariantes del pipeline (§7): "Un dato que no pasa el test no llega al sitio."

Dos grupos de pruebas:

1. Las invariantes genéricas de ``_common/invariantes.py``, con casos que
   comprueban que **detectan** los problemas. Una invariante que nunca falla no
   protege nada, así que cada una se prueba con un dataset malo a propósito.
2. Las invariantes de ESTE dataset, sobre el artefacto realmente publicado.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipelines._common.invariantes import (
    codigos_comuna_validos,
    en_rango,
    fechas_en_ventana,
    reportar,
    sin_duplicados_en,
    sin_nulos_en,
    total_cuadra,
)

RAIZ = Path(__file__).resolve().parents[3]
ARTEFACTO = RAIZ / "apps" / "web" / "public" / "data" / "ejemplo" / "partidas.json"


# ───────────────────────── invariantes genéricas ──────────────────────────


def test_sin_nulos_detecta_vacios() -> None:
    filas = [{"a": 1, "b": "x"}, {"a": None, "b": "y"}, {"b": "z"}]
    problemas = sin_nulos_en(filas, ["a", "b"])
    assert len(problemas) == 2
    assert "fila 1" in problemas[0]
    assert "falta la llave" in problemas[1]


def test_sin_nulos_pasa_con_datos_completos() -> None:
    assert sin_nulos_en([{"a": 1}, {"a": 2}], ["a"]) == []


def test_total_cuadra_detecta_descuadre() -> None:
    filas = [{"m": 10}, {"m": 20}]
    assert total_cuadra(filas, "m", 30) == []
    problemas = total_cuadra(filas, "m", 45)
    assert len(problemas) == 1
    assert "no cuadra" in problemas[0]


def test_total_cuadra_tolera_redondeo() -> None:
    # Los documentos oficiales redondean cada línea; el total no siempre es la
    # suma exacta de lo publicado. Esa diferencia chica no es un error.
    assert total_cuadra([{"m": 10.3}, {"m": 20.2}], "m", 30.0, tolerancia=0.5) == []


def test_duplicados_detectados() -> None:
    filas = [{"k": "a"}, {"k": "b"}, {"k": "a"}]
    problemas = sin_duplicados_en(filas, ["k"])
    assert len(problemas) == 1
    assert "duplica la fila 0" in problemas[0]


def test_en_rango_detecta_fuera_y_no_numerico() -> None:
    filas = [{"v": 5}, {"v": 150}, {"v": "hola"}]
    problemas = en_rango(filas, "v", 0, 100)
    assert len(problemas) == 2


def test_codigos_comuna() -> None:
    filas = [
        {"c": "13101"},  # Santiago: válido
        {"c": "05101"},  # Valparaíso: válido
        {"c": "1310"},  # 4 dígitos
        {"c": "99101"},  # región 99 inexistente
        {"c": None},
    ]
    problemas = codigos_comuna_validos(filas, "c")
    assert len(problemas) == 3


def test_codigo_comuna_region_16_es_valida() -> None:
    # Ñuble se creó en 2018. Un rango codificado con 15 regiones la rechaza, y
    # es el error más común en validadores territoriales chilenos.
    assert codigos_comuna_validos([{"c": "16101"}], "c") == []


def test_fechas_en_ventana() -> None:
    filas = [{"f": "2026-05-01"}, {"f": "1900-01-01"}, {"f": "2202-01-01"}]
    problemas = fechas_en_ventana(filas, "f", "2020-01-01", "2030-12-31")
    assert len(problemas) == 2


def test_reportar_lanza_con_problemas() -> None:
    with pytest.raises(AssertionError, match="2 problema"):
        reportar(["uno", "dos"], "prueba")


def test_reportar_calla_sin_problemas() -> None:
    reportar([], "prueba")  # no lanza


def test_reportar_acota_la_muestra() -> None:
    with pytest.raises(AssertionError, match="y 5 más"):
        reportar([f"p{i}" for i in range(25)])


# ──────────────────── invariantes del dataset publicado ────────────────────


@pytest.fixture(scope="module")
def datos() -> dict:
    if not ARTEFACTO.exists():
        pytest.skip(f"falta {ARTEFACTO}; corré el pipeline (just todo)")
    return json.loads(ARTEFACTO.read_text(encoding="utf-8"))


def test_artefacto_declara_ser_sintetico(datos: dict) -> None:
    """El aviso no es cosmético: es lo que impide que alguien cite estos datos."""
    assert "SINTÉTICOS" in datos["_aviso"]


def test_artefacto_declara_unidad(datos: dict) -> None:
    # Una cifra fiscal sin unidad ni año base no significa nada (§10).
    assert datos["unidad"] == "MM$ de 2026"


def test_llaves_completas(datos: dict) -> None:
    reportar(
        sin_nulos_en(datos["partidas"], ["partida", "monto", "variacion"]),
        "partidas.json",
    )


def test_una_partida_por_fila(datos: dict) -> None:
    reportar(sin_duplicados_en(datos["partidas"], ["partida"]), "partidas.json")


def test_total_cuadra_con_las_partes(datos: dict) -> None:
    reportar(total_cuadra(datos["partidas"], "monto", datos["total"]), "partidas.json")


def test_variaciones_plausibles(datos: dict) -> None:
    reportar(en_rango(datos["partidas"], "variacion", -100, 100), "partidas.json")


def test_montos_positivos(datos: dict) -> None:
    reportar(en_rango(datos["partidas"], "monto", 0, 10_000_000), "partidas.json")


def test_un_solo_destacado(datos: dict) -> None:
    """Regla editorial de §2.2: un gráfico tiene UN destacado, no varios."""
    destacados = [p for p in datos["partidas"] if p.get("destacado")]
    assert len(destacados) == 1, f"hay {len(destacados)} partidas destacadas"


def test_orden_estable_por_monto(datos: dict) -> None:
    """El artefacto viene ordenado: el gráfico no debería tener que ordenar."""
    montos = [p["monto"] for p in datos["partidas"]]
    assert montos == sorted(montos, reverse=True)


def test_sin_decimales_de_ruido(datos: dict) -> None:
    """§7: redondear en el pipeline. Ningún valor con más de 1 decimal."""
    problemas = []
    for i, p in enumerate(datos["partidas"]):
        v = p["variacion"]
        if isinstance(v, float) and round(v, 1) != v:
            problemas.append(f"fila {i}: variacion={v} tiene más de 1 decimal")
    reportar(problemas, "partidas.json")
