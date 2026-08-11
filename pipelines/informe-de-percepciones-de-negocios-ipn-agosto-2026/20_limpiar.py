#!/usr/bin/env python3
"""Paso 20 — limpiar y validar (§7).

Todo redondeo ocurre acá, nunca en el front. Si las invariantes fallan, no se
escribe nada: un dato que no pasa el test no llega al sitio.
"""

from __future__ import annotations

import json
from pathlib import Path

from pipelines._common.invariantes import (
    en_rango,
    sin_duplicados_en,
    sin_nulos_en,
    total_cuadra,
)
from pipelines._common.log import log

AQUI = Path(__file__).resolve().parent
INTERMEDIO = AQUI / "interim"

# Etiquetas cortas para eje/leyenda, tal como el propio Excel del Banco
# Central las declara (solo se acorta "Estará…del nivel actual" para que
# entre en un eje; el sentido no cambia).
ETIQUETAS_COMBUSTIBLE = {
    "Estará muy por debajo del nivel actual": "Muy por debajo",
    "Estará levemente por debajo del nivel actual": "Levemente por debajo",
    "Se mantendrá similar al nivel actual": "Similar al actual",
    "Estará levemente por encima del nivel actual": "Levemente por encima",
    "Estará muy por encima del nivel actual": "Muy por encima",
    "No cuenta con supuesto definido / no es relevante para sus decisiones de negocio": (
        "No tiene un supuesto definido"
    ),
}
ORDEN_COMBUSTIBLE = list(ETIQUETAS_COMBUSTIBLE.values())


def limpiar_inflacion() -> list[dict]:
    cruda = INTERMEDIO / "inflacion-cruda.json"
    if not cruda.exists():
        raise FileNotFoundError(f"falta {cruda.name}. Corré 10_extraer.py primero.")

    filas = json.loads(cruda.read_text(encoding="utf-8"))
    limpias = [
        {
            "horizonte": f["horizonte"],
            "periodo": f["periodo"],
            "media": round(float(f["media"]), 1),
            "mediana": round(float(f["mediana"]), 1),
        }
        for f in filas
    ]

    problemas: list[str] = []
    problemas += sin_nulos_en(limpias, ["horizonte", "periodo", "media", "mediana"])
    problemas += sin_duplicados_en(limpias, ["horizonte", "periodo"])
    # Expectativa de inflación en %: 0 a 20 es generoso para Chile y detecta
    # una fila que agarró el eje del gráfico en vez del valor real.
    problemas += en_rango(limpias, "media", 0, 20)
    problemas += en_rango(limpias, "mediana", 0, 20)

    if problemas:
        raise AssertionError("invariantes de inflación fallaron:\n  " + "\n  ".join(problemas[:20]))

    return limpias


def limpiar_combustibles() -> list[dict]:
    cruda = INTERMEDIO / "combustibles-cruda.json"
    if not cruda.exists():
        raise FileNotFoundError(f"falta {cruda.name}. Corré 10_extraer.py primero.")

    filas = json.loads(cruda.read_text(encoding="utf-8"))
    limpias = [
        {
            "categoria": ETIQUETAS_COMBUSTIBLE.get(f["categoria"], f["categoria"]),
            "porcentajeEmpresas": round(float(f["porcentajeEmpresas"]), 1),
        }
        for f in filas
    ]
    limpias.sort(key=lambda f: ORDEN_COMBUSTIBLE.index(f["categoria"]))

    problemas: list[str] = []
    problemas += sin_nulos_en(limpias, ["categoria", "porcentajeEmpresas"])
    problemas += sin_duplicados_en(limpias, ["categoria"])
    problemas += en_rango(limpias, "porcentajeEmpresas", 0, 100)
    # Es una distribución de respuestas de una sola pregunta: las categorías
    # tienen que sumar ~100% (tolerancia por redondeo de la propia encuesta).
    problemas += total_cuadra(limpias, "porcentajeEmpresas", 100, tolerancia=1)

    if problemas:
        raise AssertionError(
            "invariantes de combustibles fallaron:\n  " + "\n  ".join(problemas[:20])
        )

    return limpias


def main() -> int:
    try:
        inflacion = limpiar_inflacion()
        combustibles = limpiar_combustibles()
    except (FileNotFoundError, AssertionError) as e:
        log.error(str(e))
        return 1

    (INTERMEDIO / "inflacion-limpia.json").write_text(
        json.dumps(inflacion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (INTERMEDIO / "combustibles-limpia.json").write_text(
        json.dumps(combustibles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    log.info(
        "%d filas de inflación, %d categorías de combustible, invariantes en verde",
        len(inflacion),
        len(combustibles),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
