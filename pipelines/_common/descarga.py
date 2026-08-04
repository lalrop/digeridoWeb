"""Descarga con caché y registro de hash (§7).

Convenciones que impone este módulo:

* Todo script es **idempotente**: descargar dos veces no vuelve a pedir el
  archivo si el cache está fresco.
* La descarga cruda se guarda en ``pipelines/<slug>/raw/`` (gitignored,
  respaldado aparte).
* El ``sha256`` queda registrado. Cuando un organismo reemplaza un PDF sin aviso
  —pasa seguido— el cambio se detecta comparando contra el hash anterior en vez
  de descubrirlo cuando las cifras del artículo dejan de cuadrar.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

from .log import log

UA = "digerido/0.1 (+https://digerido.cl) pipeline de datos públicos"
TIEMPO_ESPERA = 60
REINTENTOS = 4


@dataclass(frozen=True)
class Descarga:
    """Registro de una descarga. Se serializa a ``meta.json``."""

    url: str
    ruta: str
    sha256: str
    bytes: int
    fecha_descarga: str
    desde_cache: bool

    def como_dict(self) -> dict[str, object]:
        return asdict(self)


def sha256_de(ruta: Path) -> str:
    """Hash en bloques: un PDF de 400 páginas no tiene por qué entrar en RAM."""
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def descargar(
    url: str,
    destino: Path,
    *,
    forzar: bool = False,
    max_edad_horas: float | None = None,
) -> Descarga:
    """Descarga ``url`` a ``destino``, salvo que el cache sirva.

    Args:
        forzar: ignora el cache y vuelve a pedir el archivo.
        max_edad_horas: si el archivo local es más viejo que esto, se re-descarga.
            ``None`` significa que el cache nunca expira — lo correcto para un
            documento publicado, que no cambia salvo reemplazo silencioso.

    Reintenta con espera exponencial: los servicios del Estado se caen, y un
    pipeline que falla en el primer 503 obliga a correr todo de nuevo a mano.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)

    if destino.exists() and not forzar:
        fresco = True
        if max_edad_horas is not None:
            edad = (time.time() - destino.stat().st_mtime) / 3600
            fresco = edad <= max_edad_horas
        if fresco:
            log.info("cache: %s", destino.name)
            return Descarga(
                url=url,
                ruta=str(destino),
                sha256=sha256_de(destino),
                bytes=destino.stat().st_size,
                fecha_descarga=datetime.fromtimestamp(
                    destino.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
                desde_cache=True,
            )

    ultimo_error: Exception | None = None
    for intento in range(REINTENTOS):
        try:
            log.info("descargando %s (intento %d)", url, intento + 1)
            pedido = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(pedido, timeout=TIEMPO_ESPERA) as resp:
                # Escritura a un temporal y rename: si la descarga se corta, el
                # archivo bueno anterior sigue intacto en vez de quedar a medias.
                temporal = destino.with_suffix(destino.suffix + ".parcial")
                with temporal.open("wb") as f:
                    while bloque := resp.read(1 << 20):
                        f.write(bloque)
                temporal.replace(destino)
            break
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            ultimo_error = e
            if intento == REINTENTOS - 1:
                break
            espera = 2 ** (intento + 1)
            log.warning("falló (%s), reintento en %ds", e, espera)
            time.sleep(espera)
    else:  # pragma: no cover - el break de arriba lo hace inalcanzable
        pass

    if not destino.exists():
        raise RuntimeError(f"no se pudo descargar {url}: {ultimo_error}")

    h = sha256_de(destino)
    log.info("descargado %s (%d bytes, sha256 %s…)", destino.name, destino.stat().st_size, h[:12])

    return Descarga(
        url=url,
        ruta=str(destino),
        sha256=h,
        bytes=destino.stat().st_size,
        fecha_descarga=datetime.now(tz=timezone.utc).isoformat(),
        desde_cache=False,
    )


def verificar_hash(registro: Path, url: str, sha256_actual: str) -> bool:
    """Compara contra el hash registrado y avisa si la fuente cambió.

    Es la mitad del mecanismo de §13: el job semanal revalida el hash y notifica.
    Devuelve ``True`` si coincide o si es la primera vez que se ve esta URL.
    """
    if not registro.exists():
        return True

    datos = json.loads(registro.read_text(encoding="utf-8"))
    anterior = datos.get("fuente", {}).get("sha256")
    if anterior is None or anterior == sha256_actual:
        return True

    log.error(
        "LA FUENTE CAMBIÓ: %s\n  registrado: %s\n  ahora:      %s\n"
        "  Los datos publicados no se tocan hasta revisar qué cambió.",
        url,
        anterior,
        sha256_actual,
    )
    return False
