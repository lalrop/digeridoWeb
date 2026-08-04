"""Logging común de los pipelines.

Formato pensado para leerse en la salida de CI: sin colores, con el paso del
pipeline en el prefijo, así un log de tres etapas se puede filtrar con grep.
"""

from __future__ import annotations

import logging
import os
import sys

_FORMATO = "%(asctime)s %(levelname)-7s %(name)s │ %(message)s"


def configurar(nombre: str = "digerido") -> logging.Logger:
    logger = logging.getLogger(nombre)
    if logger.handlers:
        return logger

    nivel = os.environ.get("DIGERIDO_LOG", "INFO").upper()
    logger.setLevel(getattr(logging, nivel, logging.INFO))

    # stderr: stdout queda libre para que un paso pueda emitir datos a una
    # tubería sin que el log lo contamine.
    manejador = logging.StreamHandler(sys.stderr)
    manejador.setFormatter(logging.Formatter(_FORMATO, datefmt="%H:%M:%S"))
    logger.addHandler(manejador)
    return logger


log = configurar()
