#!/usr/bin/env python3
"""Paso 20 — limpiar y validar (§7).

Acá van las correcciones y las normalizaciones, separadas de la extracción para
que se pueda auditar qué cambió el script y qué venía en el documento.

Todo redondeo ocurre en este paso, nunca en el front: "Nunca enviar 14 decimales
de un porcentaje."

Este paso también corre las invariantes. Si alguna falla, no escribe nada: un
dato que no pasa los tests no llega al sitio.
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
CRUDO = AQUI / "raw"
INTERMEDIO = AQUI / "interim"


def main() -> int:
    cruda = INTERMEDIO / "tabla-cruda.json"
    if not cruda.exists():
        log.error("falta %s. Corré 10_extraer.py primero.", cruda.name)
        return 1

    filas = json.loads(cruda.read_text(encoding="utf-8"))
    doc = json.loads((CRUDO / "documento-sintetico.json").read_text(encoding="utf-8"))

    # ── Normalización ──────────────────────────────────────────────────────
    limpias = []
    for fila in filas:
        limpias.append(
            {
                # Nombres sin espacios sobrantes: un PDF los trae con frecuencia.
                "partida": str(fila["partida"]).strip(),
                "monto": int(fila["monto"]),
                # Redondeo acá y no en el front (§7).
                "variacion": round(float(fila["variacion"]), 1),
                "destacado": bool(fila["destacado"]),
            }
        )

    # Orden estable por monto: el gráfico no debería tener que ordenar, y un
    # orden fijo hace que el diff del artefacto sea legible entre corridas.
    limpias.sort(key=lambda f: -f["monto"])

    # ── Invariantes (§7) ───────────────────────────────────────────────────
    problemas: list[str] = []
    problemas += sin_nulos_en(limpias, ["partida", "monto", "variacion"])
    problemas += sin_duplicados_en(limpias, ["partida"])
    problemas += en_rango(limpias, "monto", 0, 10_000_000)
    # Una variación fuera de ±100 % en un presupuesto suele ser una columna mal
    # mapeada, no un dato real.
    problemas += en_rango(limpias, "variacion", -100, 100)
    problemas += total_cuadra(limpias, "monto", doc["total_declarado"], tolerancia=0.5)

    if problemas:
        log.error("las invariantes fallaron; no se escribe nada:")
        for p in problemas[:20]:
            log.error("  %s", p)
        return 1

    destino = INTERMEDIO / "tabla-limpia.json"
    destino.write_text(
        json.dumps(limpias, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    log.info("%d filas limpias, invariantes en verde", len(limpias))
    log.info("total: %s (cuadra con el documento)", f"{sum(f['monto'] for f in limpias):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
