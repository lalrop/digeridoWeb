#!/usr/bin/env python3
"""Revalida el hash de cada fuente registrada (§13).

    python3 scripts/revalidar_fuentes.py [--formato github]

Recorre ``apps/web/src/content/fuentes/*.json``, descarga cada documento y
compara su sha256 contra la última revisión registrada.

Lo que NO hace, a propósito:

* no republica ni regenera datos — los datos publicados no dependen de una
  descarga en vivo, y una fuente que cambió requiere criterio editorial, no un
  script;
* no actualiza el hash registrado — hacerlo automáticamente borraría la
  evidencia de que el documento cambió, que es justamente lo que se quiere ver.

Sale con código 0 aunque haya cambios: el workflow decide qué hacer con ellos.
Solo falla si no pudo hacer el chequeo.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipelines._common.descarga import descargar
from pipelines._common.log import log

RAIZ = Path(__file__).resolve().parents[1]
DIR_FUENTES = RAIZ / "apps" / "web" / "src" / "content" / "fuentes"

# Las fuentes de ejemplo apuntan a URLs inexistentes a propósito: la pieza de
# andamiaje no tiene documento real que revalidar.
DOMINIOS_IGNORADOS = ("example.org", "example.com")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--formato",
        choices=["texto", "github"],
        default="texto",
        help="github escribe cambios.txt y el output para el workflow",
    )
    args = parser.parse_args()

    if not DIR_FUENTES.exists():
        log.warning("no hay %s; nada que revalidar", DIR_FUENTES.relative_to(RAIZ))
        return 0

    cambios: list[str] = []
    revisadas = 0
    errores = 0

    with tempfile.TemporaryDirectory(prefix="digerido-revalidar-") as tmp:
        for archivo in sorted(DIR_FUENTES.glob("*.json")):
            datos = json.loads(archivo.read_text(encoding="utf-8"))
            url = datos["url"]

            if any(d in url for d in DOMINIOS_IGNORADOS):
                log.info("omitida (fuente de ejemplo): %s", archivo.name)
                continue

            revisiones = datos.get("revisiones", [])
            if not revisiones:
                log.warning("%s no tiene revisiones registradas", archivo.name)
                continue

            # La última revisión es la referencia; el historial se conserva.
            esperado = max(revisiones, key=lambda r: str(r["fechaDescarga"]))["sha256"]

            try:
                reg = descargar(url, Path(tmp) / archivo.stem, forzar=True)
            except Exception as e:
                errores += 1
                log.error("no se pudo descargar %s: %s", url, e)
                cambios.append(f"[ERROR] {datos['organismo']} — {url}\n         {e}")
                continue

            revisadas += 1
            if reg.sha256 == esperado:
                log.info("sin cambios: %s (%s)", datos["titulo"], archivo.name)
            else:
                log.error("CAMBIÓ: %s", datos["titulo"])
                cambios.append(
                    f"[CAMBIÓ] {datos['organismo']} — {datos['titulo']}\n"
                    f"         {url}\n"
                    f"         registrado: {esperado}\n"
                    f"         ahora:      {reg.sha256}"
                )

    log.info(
        "%d fuente(s) revisada(s), %d cambio(s), %d error(es)", revisadas, len(cambios), errores
    )

    if args.formato == "github":
        (RAIZ / "cambios.txt").write_text(
            "\n\n".join(cambios) if cambios else "sin cambios\n", encoding="utf-8"
        )
        salida = os.environ.get("GITHUB_OUTPUT")
        if salida:
            with open(salida, "a", encoding="utf-8") as f:
                f.write(f"cambios={len(cambios)}\n")
                f.write(f"errores={errores}\n")
    elif cambios:
        print("\n\n".join(cambios))

    # Solo falla si no se pudo revalidar nada teniendo fuentes que revalidar.
    return 1 if errores > 0 and revisadas == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
