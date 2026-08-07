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


def main() -> int:
    cruda = INTERMEDIO / "tabla-cruda.json"
    if not cruda.exists():
        log.error("falta %s. Corré 10_extraer.py primero.", cruda.name)
        return 1

    filas = json.loads(cruda.read_text(encoding="utf-8"))

    # El documento usa coma decimal ("6,8"); el punto es el único cambio de
    # formato acá, no de valor. La primera letra en mayúscula es cosmética
    # (para el eje del gráfico), el resto del texto queda tal como lo declara
    # el boletín.
    limpias = [
        {
            "sector": f["sector"].strip().capitalize(),
            "variacion12meses": round(float(f["variacion12meses"].replace(",", ".")), 1),
        }
        for f in filas
    ]

    # Es variación porcentual interanual por sector, no puede superar ±100%
    # de forma plausible (no hay "sin dato" en este dataset: los 7 sectores
    # vienen siempre completos de la misma frase del boletín).
    problemas: list[str] = []
    problemas += sin_nulos_en(limpias, ["sector", "variacion12meses"])
    problemas += sin_duplicados_en(limpias, ["sector"])
    problemas += en_rango(limpias, "variacion12meses", -100, 100)

    if problemas:
        log.error("las invariantes fallaron; no se escribe nada:")
        for p in problemas[:20]:
            log.error("  %s", p)
        return 1

    (INTERMEDIO / "tabla-limpia.json").write_text(
        json.dumps(limpias, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    log.info("%d filas limpias, invariantes en verde", len(limpias))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
