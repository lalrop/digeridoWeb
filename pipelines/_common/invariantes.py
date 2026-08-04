"""Invariantes reutilizables para los tests de pipeline (§7).

"Un dato que no pasa el test no llega al sitio."

Estas funciones son las comprobaciones que se repiten en toda digestión chilena:
que los totales cuadren, que los códigos territoriales existan, que no haya
nulos en las llaves. Cada pipeline agrega las suyas en ``tests/``.

Devuelven listas de problemas en vez de lanzar: un pipeline debe poder reportar
los quince errores de un dataset de una vez, no el primero y nada más.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

# Rangos de códigos de la división político-administrativa chilena.
# Regiones: 1–16 (15 = Arica y Parinacota, 16 = Ñuble, creada en 2018).
REGIONES_VALIDAS = frozenset(range(1, 17))
LARGO_CODIGO_COMUNA = 5


def sin_nulos_en(filas: Sequence[Mapping[str, Any]], llaves: Sequence[str]) -> list[str]:
    """Ninguna llave puede venir vacía: es lo que rompe los joins río abajo."""
    problemas: list[str] = []
    for i, fila in enumerate(filas):
        for llave in llaves:
            if llave not in fila:
                problemas.append(f"fila {i}: falta la llave '{llave}'")
            elif fila[llave] is None or fila[llave] == "":
                problemas.append(f"fila {i}: llave '{llave}' vacía")
    return problemas


def total_cuadra(
    filas: Sequence[Mapping[str, Any]],
    campo: str,
    total_declarado: float,
    *,
    tolerancia: float = 0.5,
) -> list[str]:
    """La suma de las partes contra el total que declara el documento.

    La tolerancia existe porque los documentos oficiales redondean cada línea y
    el total no siempre es la suma exacta de lo publicado. Una diferencia mayor
    a la tolerancia no es redondeo: es un error de extracción.
    """
    suma = sum(float(f[campo]) for f in filas if f.get(campo) is not None)
    diferencia = abs(suma - total_declarado)
    if diferencia > tolerancia:
        return [
            f"el total no cuadra: suma de '{campo}' = {suma:,.2f}, "
            f"declarado = {total_declarado:,.2f}, diferencia = {diferencia:,.2f}"
        ]
    return []


def sin_duplicados_en(filas: Sequence[Mapping[str, Any]], llaves: Sequence[str]) -> list[str]:
    """La llave compuesta debe ser única."""
    vistos: dict[tuple[Any, ...], int] = {}
    problemas: list[str] = []
    for i, fila in enumerate(filas):
        clave = tuple(fila.get(k) for k in llaves)
        if clave in vistos:
            problemas.append(
                f"fila {i}: duplica la fila {vistos[clave]} en {list(llaves)}: {clave}"
            )
        else:
            vistos[clave] = i
    return problemas


def en_rango(
    filas: Sequence[Mapping[str, Any]],
    campo: str,
    minimo: float,
    maximo: float,
) -> list[str]:
    """Un valor fuera de rango casi siempre es una columna mal mapeada."""
    problemas: list[str] = []
    for i, fila in enumerate(filas):
        v = fila.get(campo)
        if v is None:
            continue
        try:
            n = float(v)
        except (TypeError, ValueError):
            problemas.append(f"fila {i}: '{campo}' = {v!r} no es numérico")
            continue
        if not (minimo <= n <= maximo):
            problemas.append(f"fila {i}: '{campo}' = {n} fuera de [{minimo}, {maximo}]")
    return problemas


def codigos_comuna_validos(filas: Sequence[Mapping[str, Any]], campo: str) -> list[str]:
    """Los códigos de comuna del INE son 5 dígitos; los 2 primeros, la región.

    Se valida la forma y el rango de región, no la existencia del código: la
    lista completa de comunas se verifica contra la geometría en el pipeline que
    la use, que es donde el archivo de comunas está disponible.
    """
    problemas: list[str] = []
    for i, fila in enumerate(filas):
        v = fila.get(campo)
        if v is None:
            problemas.append(f"fila {i}: '{campo}' vacío")
            continue
        codigo = str(v).strip()
        if not codigo.isdigit() or len(codigo) != LARGO_CODIGO_COMUNA:
            problemas.append(
                f"fila {i}: '{campo}' = {v!r} no es un código de comuna de "
                f"{LARGO_CODIGO_COMUNA} dígitos"
            )
            continue
        region = int(codigo[:2])
        if region not in REGIONES_VALIDAS:
            problemas.append(f"fila {i}: '{campo}' = {codigo} tiene región {region}, inexistente")
    return problemas


def fechas_en_ventana(
    filas: Sequence[Mapping[str, Any]],
    campo: str,
    desde: str,
    hasta: str,
) -> list[str]:
    """Fechas ISO dentro de una ventana esperada.

    Atrapa el error clásico de extracción de PDF: una fecha de 1900 o de 2202
    porque el parser leyó mal una celda.
    """
    problemas: list[str] = []
    for i, fila in enumerate(filas):
        v = fila.get(campo)
        if v is None:
            continue
        s = str(v)[:10]
        if not (desde <= s <= hasta):
            problemas.append(f"fila {i}: '{campo}' = {s} fuera de [{desde}, {hasta}]")
    return problemas


def reportar(problemas: Sequence[str], contexto: str = "") -> None:
    """Convierte una lista de problemas en un fallo legible de pytest.

    Muestra hasta 20: el mensaje de un test que lista 4.000 filas malas es
    inservible, y con 20 ya se ve el patrón.
    """
    if not problemas:
        return
    encabezado = f"{len(problemas)} problema(s)" + (f" en {contexto}" if contexto else "")
    muestra = "\n  ".join(problemas[:20])
    resto = f"\n  … y {len(problemas) - 20} más" if len(problemas) > 20 else ""
    raise AssertionError(f"{encabezado}:\n  {muestra}{resto}")
