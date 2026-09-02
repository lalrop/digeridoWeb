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

TOTAL_REGIONES_CHILE = 16


def main() -> int:
    cruda = INTERMEDIO / "tabla-cruda.json"
    if not cruda.exists():
        log.error("falta %s. Corré 10_extraer.py primero.", cruda.name)
        return 1

    filas = json.loads(cruda.read_text(encoding="utf-8"))

    # El documento usa coma decimal ("2,6"); el punto es el único cambio de
    # formato acá, no de valor.
    limpias = [
        {
            "region": f["region"].strip(),
            "universidades": int(f["universidades"]),
            "investigadores": int(f["investigadores"]),
            "doctoradosPor1000": round(float(f["doctoradosPor1000"].replace(",", ".")), 1),
        }
        for f in filas
    ]

    problemas: list[str] = []
    problemas += sin_nulos_en(
        limpias, ["region", "universidades", "investigadores", "doctoradosPor1000"]
    )
    problemas += sin_duplicados_en(limpias, ["region"])
    problemas += en_rango(limpias, "universidades", 0, 100)
    problemas += en_rango(limpias, "investigadores", 0, 50_000)
    problemas += en_rango(limpias, "doctoradosPor1000", 0, 50)

    # Chile tiene 16 regiones: ni una de más (algo mal separado en la
    # transcripción) ni una de menos (una región que se saltó sin querer).
    if len(limpias) != TOTAL_REGIONES_CHILE:
        problemas.append(f"se esperaban {TOTAL_REGIONES_CHILE} regiones, hay {len(limpias)}")

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
