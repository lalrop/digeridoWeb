"""Publicación de artefactos al front (§7).

La frontera del monorepo: ``pipelines/`` y ``apps/web/`` se comunican **solo**
por archivos en ``public/data/``. El front nunca lee un Excel ni un PDF, y este
módulo es el único lugar del pipeline que escribe dentro de ``apps/web``.

Reglas que impone:

* JSON minificado para artefactos < 500 KB; sobre eso avisa y sugiere Parquet.
* Redondeo en el pipeline, nunca en el front: ``redondear()`` se aplica antes de
  serializar. No se publican 14 decimales de un porcentaje.
* Cada artefacto escrito devuelve su tamaño, filas y hash, para que
  ``meta.json`` y el frontmatter de la digestión no se escriban a mano.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .log import log

# Raíz del repo: este archivo está en pipelines/_common/.
RAIZ = Path(__file__).resolve().parents[2]
DIR_DATOS = RAIZ / "apps" / "web" / "public" / "data"

LIMITE_JSON_KB = 500


@dataclass(frozen=True)
class Artefacto:
    archivo: str
    bytes: int
    filas: int
    sha256: str

    def como_dict(self) -> dict[str, object]:
        return {
            "archivo": self.archivo,
            "bytes": self.bytes,
            "filas": self.filas,
            "sha256": self.sha256,
        }


def redondear(valor: Any, decimales: int = 1) -> Any:
    """Redondea recursivamente los flotantes de una estructura.

    Un float que sale de pandas trae 14 decimales de ruido de punto flotante.
    Enviarlos al navegador infla el archivo y sugiere una precisión que el dato
    no tiene.
    """
    if isinstance(valor, float):
        redondeado = round(valor, decimales)
        # 4.0 → 4: un entero disfrazado de float pesa más y no dice nada extra.
        return int(redondeado) if redondeado.is_integer() else redondeado
    if isinstance(valor, Mapping):
        return {k: redondear(v, decimales) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [redondear(v, decimales) for v in valor]
    return valor


def publicar_json(
    datos: Any,
    ruta_relativa: str,
    *,
    decimales: int = 1,
    filas: int | None = None,
    minificar: bool = True,
) -> Artefacto:
    """Escribe un artefacto JSON en ``apps/web/public/data/<ruta_relativa>``."""
    destino = DIR_DATOS / ruta_relativa
    destino.parent.mkdir(parents=True, exist_ok=True)

    limpio = redondear(datos, decimales)
    if minificar:
        texto = json.dumps(limpio, ensure_ascii=False, separators=(",", ":"))
    else:
        texto = json.dumps(limpio, ensure_ascii=False, indent=2) + "\n"

    destino.write_text(texto, encoding="utf-8")
    peso = len(texto.encode("utf-8"))

    if peso > LIMITE_JSON_KB * 1024:
        log.warning(
            "%s pesa %.0f KB, sobre el límite de %d KB para JSON. "
            "§7 sugiere Parquet + DuckDB-WASM con filtrado en cliente.",
            ruta_relativa,
            peso / 1024,
            LIMITE_JSON_KB,
        )

    n_filas = filas if filas is not None else _contar_filas(limpio)
    h = hashlib.sha256(texto.encode("utf-8")).hexdigest()

    log.info("publicado %s (%.1f KB, %d filas)", ruta_relativa, peso / 1024, n_filas)
    return Artefacto(archivo=ruta_relativa, bytes=peso, filas=n_filas, sha256=h)


def publicar_csv(
    filas: Sequence[Mapping[str, Any]],
    ruta_relativa: str,
    *,
    columnas: Sequence[str] | None = None,
    decimales: int = 1,
) -> Artefacto:
    """Escribe un CSV. Para que la Despensa ofrezca algo abrible en planilla."""
    import csv
    import io

    destino = DIR_DATOS / ruta_relativa
    destino.parent.mkdir(parents=True, exist_ok=True)

    if not filas:
        raise ValueError(f"{ruta_relativa}: no hay filas para publicar")

    campos = list(columnas) if columnas else list(filas[0].keys())
    buffer = io.StringIO()
    # `lineterminator` explícito: el default de csv usa \r\n y ensucia el diff.
    escritor = csv.DictWriter(buffer, fieldnames=campos, lineterminator="\n")
    escritor.writeheader()
    for fila in filas:
        escritor.writerow({c: redondear(fila.get(c), decimales) for c in campos})

    texto = buffer.getvalue()
    destino.write_text(texto, encoding="utf-8")
    peso = len(texto.encode("utf-8"))
    h = hashlib.sha256(texto.encode("utf-8")).hexdigest()

    log.info("publicado %s (%.1f KB, %d filas)", ruta_relativa, peso / 1024, len(filas))
    return Artefacto(archivo=ruta_relativa, bytes=peso, filas=len(filas), sha256=h)


def escribir_meta(slug: str, contenido: Mapping[str, Any]) -> Path:
    """Escribe el ``meta.json`` de la digestión, junto a su MDX.

    Lo escribe el pipeline y no una persona: las páginas, el hash y los tamaños
    salen de la extracción, y copiarlos a mano es cómo se cuelan los errores que
    §13 llama "un error factual destruye la credibilidad".
    """
    destino = RAIZ / "apps" / "web" / "src" / "content" / "digestiones" / slug / "meta.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(contenido, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    log.info("meta.json actualizado: %s", destino.relative_to(RAIZ))
    return destino


def _contar_filas(datos: Any) -> int:
    """Heurística de conteo: la lista más larga que haya en la estructura."""
    if isinstance(datos, list):
        return len(datos)
    if isinstance(datos, Mapping):
        candidatos: Iterable[int] = (
            _contar_filas(v) for v in datos.values() if isinstance(v, (list, Mapping))
        )
        return max(candidatos, default=0)
    return 0
