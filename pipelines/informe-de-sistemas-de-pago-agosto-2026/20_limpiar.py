#!/usr/bin/env python3
"""Paso 20 — limpiar y validar (§7).

Todo redondeo ocurre acá, nunca en el front. Si las invariantes fallan, no se
escribe nada: un dato que no pasa el test no llega al sitio.
"""

from __future__ import annotations

import json
from pathlib import Path

from pipelines._common.invariantes import en_rango, sin_duplicados_en, sin_nulos_en
from pipelines._common.log import log

AQUI = Path(__file__).resolve().parent
INTERMEDIO = AQUI / "interim"

MONTOS_VALIDOS = {1000, 20000, 50000}


def limpiar_costo_tef() -> list[dict]:
    cruda = INTERMEDIO / "costo-tef-cruda.json"
    if not cruda.exists():
        raise FileNotFoundError(f"falta {cruda.name}. Corré 10_extraer.py primero.")

    filas = json.loads(cruda.read_text(encoding="utf-8"))
    limpias = [
        {
            "entidad": str(f["entidad"]).strip(),
            "monto": int(f["monto"]),
            "porcentaje": round(float(f["porcentaje"]), 1),
        }
        for f in filas
    ]

    problemas: list[str] = []
    problemas += sin_nulos_en(limpias, ["entidad", "monto", "porcentaje"])
    problemas += sin_duplicados_en(limpias, ["entidad", "monto"])
    problemas += en_rango(limpias, "porcentaje", 0, 100)
    montos_vistos = {f["monto"] for f in limpias}
    if montos_vistos != MONTOS_VALIDOS:
        problemas.append(f"montos inesperados: {montos_vistos} (se esperaba {MONTOS_VALIDOS})")

    if problemas:
        raise AssertionError("invariantes de costo TEF fallaron:\n  " + "\n  ".join(problemas[:20]))

    limpias.sort(key=lambda f: (f["entidad"], f["monto"]))
    return limpias


def limpiar_acceso_efectivo() -> list[dict]:
    cruda = INTERMEDIO / "acceso-efectivo-cruda.json"
    if not cruda.exists():
        raise FileNotFoundError(f"falta {cruda.name}. Corré 10_extraer.py primero.")

    filas = json.loads(cruda.read_text(encoding="utf-8"))
    limpias = [
        {
            "canal": str(f["canal"]).strip(),
            "porcentaje": round(float(f["porcentaje"]), 1),
        }
        for f in filas
    ]

    problemas: list[str] = []
    problemas += sin_nulos_en(limpias, ["canal", "porcentaje"])
    problemas += sin_duplicados_en(limpias, ["canal"])
    problemas += en_rango(limpias, "porcentaje", 0, 100)

    if problemas:
        raise AssertionError(
            "invariantes de acceso a efectivo fallaron:\n  " + "\n  ".join(problemas[:20])
        )

    return limpias


def main() -> int:
    try:
        costo_tef = limpiar_costo_tef()
        acceso_efectivo = limpiar_acceso_efectivo()
    except (FileNotFoundError, AssertionError) as e:
        log.error(str(e))
        return 1

    (INTERMEDIO / "costo-tef-limpia.json").write_text(
        json.dumps(costo_tef, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (INTERMEDIO / "acceso-efectivo-limpia.json").write_text(
        json.dumps(acceso_efectivo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    log.info(
        "%d filas de costo TEF, %d canales de acceso a efectivo, invariantes en verde",
        len(costo_tef),
        len(acceso_efectivo),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
