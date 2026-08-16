#!/usr/bin/env python3
"""Paso 30 — publicar (§7).

Único paso que escribe dentro de 'apps/web'. Los tamaños, hashes y conteos del
meta.json los escribe este script: copiarlos a mano es cómo se cuela el error
factual que §13 identifica como el riesgo más caro del proyecto.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from pipelines._common.log import log
from pipelines._common.publicar import escribir_meta, publicar_csv, publicar_json

AQUI = Path(__file__).resolve().parent
CRUDO = AQUI / "raw"
INTERMEDIO = AQUI / "interim"

SLUG = "informe-de-sistemas-de-pago-agosto-2026"


def main() -> int:
    costo_tef_path = INTERMEDIO / "costo-tef-limpia.json"
    acceso_efectivo_path = INTERMEDIO / "acceso-efectivo-limpia.json"
    if not costo_tef_path.exists() or not acceso_efectivo_path.exists():
        log.error("faltan archivos limpios. Corré 20_limpiar.py primero.")
        return 1

    costo_tef = json.loads(costo_tef_path.read_text(encoding="utf-8"))
    acceso_efectivo = json.loads(acceso_efectivo_path.read_text(encoding="utf-8"))
    metricas = json.loads((INTERMEDIO / "metricas-original.json").read_text(encoding="utf-8"))
    registro = json.loads((CRUDO / "registro.json").read_text(encoding="utf-8"))

    # Costo de aceptar un pago vía TEF, como % del monto, según proveedor y
    # monto pagado (TABLA I.2 del Informe) — es el gráfico principal.
    datos_costo_tef = {"unidad": "% del monto pagado", "filas": costo_tef}

    # Canal principal de obtención de efectivo, % de la población (ENUPE 2025,
    # citada en el RECUADRO I.2) — gráfico de apoyo.
    datos_acceso_efectivo = {"unidad": "% de la población", "filas": acceso_efectivo}

    artefactos = [
        publicar_json(datos_costo_tef, f"{SLUG}/datos.json", filas=len(costo_tef)),
        publicar_csv(costo_tef, f"{SLUG}/datos.csv"),
        publicar_json(
            datos_acceso_efectivo, f"{SLUG}/acceso-efectivo.json", filas=len(acceso_efectivo)
        ),
        publicar_csv(acceso_efectivo, f"{SLUG}/acceso-efectivo.csv"),
    ]

    escribir_meta(
        SLUG,
        {
            "slug": SLUG,
            "generado": date.today().isoformat(),
            "fuente": registro,
            "etiqueta": metricas,
            "artefactos": [a.como_dict() for a in artefactos],
        },
    )

    log.info(
        "listo. Copiá al frontmatter: palabrasOriginal=%s, legibilidadOriginal=%s, "
        "siglasSinDefinir=%s, tiempoLectura.original=%s",
        metricas["palabrasOriginal"],
        metricas["legibilidadOriginal"],
        metricas["siglasSinDefinir"],
        metricas["tiempoLecturaOriginal"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
