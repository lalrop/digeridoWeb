"""Índice Fernández-Huerta y detector de siglas.

Gemelo Python de ``packages/kit/src/utils/legibilidad.ts``.

Este módulo mide el documento ORIGINAL (PDF, planilla) para la Etiqueta
Nutricional; el gemelo TS mide el texto digerido en build. La etiqueta compara
las dos cifras, así que las dos implementaciones tienen que coincidir: los casos
de ``tests/test_legibilidad.py`` son el contrato, y son los mismos que los de
``legibilidad.test.ts``.

Si tocás uno, tocá el otro. Es la única duplicación deliberada del repo, y
existe porque el pipeline no puede importar TS ni el front puede leer un PDF.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

VOCALES = set("aeiouáéíóúüàèìòùâêîôûAEIOUÁÉÍÓÚÜ")
FUERTES = set("aeoáéóAEO")
# Vocal débil con tilde: rompe el diptongo (pa-ís, ba-úl).
DEBIL_TILDADA = set("íúÍÚ")

# Debe ser IDÉNTICA a PALABRAS_POR_MINUTO en legibilidad.ts, o la comparación
# original/digerido de la etiqueta no significa nada.
PALABRAS_POR_MINUTO = 200

_U_MUDA = re.compile(r"([qQgG])u([eéiíEÉIÍ])")
_NO_LETRA = re.compile(r"[^A-Za-zÀ-ÿ]")
_PALABRA = re.compile(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’-]*")

# Abreviaturas frecuentes en normativa chilena. Sin protegerlas, un documento
# presupuestario se segmenta en frases de tres palabras y sale artificialmente
# legible — el sesgo más grave posible en la cifra que este módulo produce.
_ABREVIATURAS = re.compile(
    r"\b(Art|arts|N|Nº|No|inc|lit|letra|Sr|Sra|Ud|Uds|etc|pág|págs|cap|tít"
    r"|párr|D\.F\.L|D\.S|D\.L|Ley N)\.",
    re.IGNORECASE,
)
_MILES = re.compile(r"(\d)\.(\d)")
_INICIAL = re.compile(r"\b([A-ZÁÉÍÓÚ])\.")
_CORTE_FRASE = re.compile(r"[.!?;]+[\s\"'»)\]]*|\n{2,}")

_SIGLA = re.compile(r"\b([A-ZÁÉÍÓÚÑ]{2,}[0-9]*)\b")
_ROMANO = re.compile(r"^[IVXLCDM]+$")
_CON_TILDE = re.compile(r"[ÁÉÍÓÚ]")

# Palabras en mayúscula separadas por espacios, comas, guiones o NÚMEROS: un
# encabezado real es "CAPÍTULO 1 - ANTECEDENTES GENERALES", y si el dígito
# cortara la secuencia quedarían dos palabras sueltas contadas como siglas.
# Si aparece una minúscula o un punto, el título terminó.
_TITULO = re.compile(
    r"\b[A-ZÁÉÍÓÚÑ]{2,}[0-9]*\b(?:[ \t,\-–0-9]+\b[A-ZÁÉÍÓÚÑ]{2,}[0-9]*\b)+"
)
_SEP_TITULO = re.compile(r"[ \t,\-–0-9]+")

# Palabras de función que en un título en mayúsculas se ven como siglas de dos o
# tres letras. "INFORME DE EJECUCIÓN" no aporta tres siglas sin definir.
NO_SIGLAS = frozenset(
    {
        "DE", "DEL", "LA", "EL", "LOS", "LAS", "UN", "UNA", "UNOS", "UNAS",
        "EN", "POR", "PARA", "CON", "SIN", "SOBRE", "ENTRE", "DESDE", "HASTA",
        "AL", "SE", "SU", "SUS", "ES", "SON", "NO", "NI", "QUE", "ANEXO", "TOTAL",
    }
)

# Mínimo de palabras en mayúscula seguidas para considerarlo un título.
LARGO_TITULO = 3


def _rangos_de_titulo(texto: str) -> list[tuple[int, int]]:
    """Rangos ocupados por encabezados en mayúsculas.

    Un PDF oficial está lleno de títulos como "INFORME DE EJECUCIÓN
    PRESUPUESTARIA": sin esto, cada palabra del encabezado cuenta como sigla sin
    definir e infla la cifra que se muestra en la Etiqueta Nutricional.

    Se exigen varias palabras seguidas para no descartar una sigla legítima
    suelta en medio de una frase ("La SUBDERE informó").
    """
    rangos: list[tuple[int, int]] = []
    for m in _TITULO.finditer(texto):
        if len([p for p in _SEP_TITULO.split(m.group(0)) if p]) >= LARGO_TITULO:
            rangos.append((m.start(), m.end()))
    return rangos

# Siglas que un lector general reconoce sin glosario: inflar la cifra con IVA y
# RUT convierte la etiqueta en un chiste interno.
SIGLAS_CONOCIDAS = frozenset(
    {
        "IVA", "RUT", "PIB", "UF", "UTM", "IPC", "AFP", "INE", "SII", "ONU",
        "OCDE", "PDI", "IPSA", "CAE", "FONASA", "ISAPRE", "DIPRES", "MOP",
    }
)


def contar_silabas(palabra: str) -> int:
    """Cuenta sílabas por núcleos vocálicos.

    El español es lo bastante regular para hacerlo sin diccionario:

    * fuerte + fuerte      → hiato, 2 sílabas (a-é-re-o)
    * débil tildada + otra → hiato, 2 sílabas (pa-ís)
    * el resto de grupos   → diptongo o triptongo, 1 sílaba (cui-da-do)
    """
    limpia = _NO_LETRA.sub("", unicodedata.normalize("NFC", palabra))
    if not limpia:
        return 0

    # Neutraliza la u muda de que/qui/gue/gui.
    limpia = _U_MUDA.sub(r"\1\2", limpia)

    silabas = 0
    i = 0
    n = len(limpia)
    while i < n:
        if limpia[i] not in VOCALES:
            i += 1
            continue
        nucleos = 1
        j = i
        while j + 1 < n and limpia[j + 1] in VOCALES:
            a, b = limpia[j], limpia[j + 1]
            hiato = (a in FUERTES and b in FUERTES) or a in DEBIL_TILDADA or b in DEBIL_TILDADA
            if hiato:
                nucleos += 1
            j += 1
        silabas += nucleos
        i = j + 1

    return max(1, silabas)


def palabras(texto: str) -> list[str]:
    """Secuencias con al menos una letra. Descarta cifras sueltas."""
    return _PALABRA.findall(texto)


def frases(texto: str) -> list[str]:
    """Segmenta en frases protegiendo cifras y abreviaturas."""
    protegido = _MILES.sub(r"\1 \2", texto)
    protegido = _ABREVIATURAS.sub(r"\1 ", protegido)
    protegido = _INICIAL.sub(r"\1 ", protegido)
    # Los fragmentos solo se usan para CONTAR frases; no hace falta deshacer
    # las protecciones de arriba.
    partes = (p.strip() for p in _CORTE_FRASE.split(protegido))
    return [p for p in partes if palabras(p)]


@dataclass(frozen=True)
class Legibilidad:
    """Resultado con las magnitudes intermedias, para poder auditar la cifra."""

    indice: int
    nivel: str
    palabras: int
    frases: int
    silabas: int
    silabas_por_palabra: float
    palabras_por_frase: float

    def como_dict(self) -> dict[str, float | int | str]:
        return {
            "indice": self.indice,
            "nivel": self.nivel,
            "palabras": self.palabras,
            "frases": self.frases,
            "silabas": self.silabas,
            "silabasPorPalabra": self.silabas_por_palabra,
            "palabrasPorFrase": self.palabras_por_frase,
        }


def nivel_de_legibilidad(indice: int) -> str:
    """Escala de Fernández-Huerta con los nombres de la bibliografía."""
    if indice >= 90:
        return "muy fácil"
    if indice >= 80:
        return "fácil"
    if indice >= 70:
        return "bastante fácil"
    if indice >= 60:
        return "normal"
    if indice >= 50:
        return "bastante difícil"
    if indice >= 30:
        return "difícil"
    return "muy difícil"


def legibilidad(texto: str) -> Legibilidad:
    """Fernández-Huerta (1959), en la forma implementada de facto:

        L = 206,84 − 60 · (sílabas/palabra) − 1,02 · (palabras/frase)

    La literatura cita también una variante con "frases por cada 100 palabras";
    las dos circulan bajo el mismo nombre. Se usa esta porque es la que
    implementan las herramientas con que alguien podría contrastar la cifra.

    Se recorta a 0–100: el crudo se pasa por ambos lados y una etiqueta que dice
    "−12 / 100" no comunica nada.
    """
    ws = palabras(texto)
    fs = frases(texto)

    if not ws or not fs:
        return Legibilidad(0, "sin texto", 0, 0, 0, 0.0, 0.0)

    silabas = sum(contar_silabas(w) for w in ws)
    spp = silabas / len(ws)
    ppf = len(ws) / len(fs)
    crudo = 206.84 - 60 * spp - 1.02 * ppf
    indice = round(min(100.0, max(0.0, crudo)))

    return Legibilidad(
        indice=indice,
        nivel=nivel_de_legibilidad(indice),
        palabras=len(ws),
        frases=len(fs),
        silabas=silabas,
        silabas_por_palabra=round(spp, 3),
        palabras_por_frase=round(ppf, 2),
    )


@dataclass
class Siglas:
    encontradas: list[dict[str, object]] = field(default_factory=list)
    sin_definir: int = 0
    total: int = 0

    def como_dict(self) -> dict[str, object]:
        return {
            "encontradas": self.encontradas,
            "sinDefinir": self.sin_definir,
            "total": self.total,
        }


def detectar_siglas(texto: str) -> Siglas:
    """Detecta siglas y decide si el texto las define.

    Se considera definida si aparece junto a su expansión en cualquiera de las
    dos convenciones editoriales: "Dirección de Presupuestos (DIPRES)" o
    "DIPRES (Dirección de Presupuestos)".

    Es una heurística y lo dice: sirve para poner una cifra comparable en la
    etiqueta, no para auditar el glosario de un documento.
    """
    titulos = _rangos_de_titulo(texto)

    conteo: dict[str, int] = {}
    for m in _SIGLA.finditer(texto):
        s = m.group(1)
        if _ROMANO.match(s):  # III, XIV: numeración, no sigla
            continue
        if s in NO_SIGLAS:  # DE, LA, POR… en un título
            continue
        if _CON_TILDE.search(s):  # "EJECUCIÓN" es una palabra en versalita
            continue
        if any(a <= m.start() < b for a, b in titulos):
            continue
        conteo[s] = conteo.get(s, 0) + 1

    encontradas: list[dict[str, object]] = []
    for sigla, veces in conteo.items():
        esc = re.escape(sigla)
        definida = (
            sigla in SIGLAS_CONOCIDAS
            or re.search(rf"\w[\w\s,'’-]{{3,}}\(\s*{esc}\s*\)", texto) is not None
            or re.search(rf"\b{esc}\s*\(\s*[A-ZÁÉÍÓÚa-z][\w\s,'’-]{{3,}}\)", texto) is not None
        )
        encontradas.append({"sigla": sigla, "veces": veces, "definida": definida})

    encontradas.sort(key=lambda s: (-int(s["veces"]), str(s["sigla"])))

    return Siglas(
        encontradas=encontradas,
        sin_definir=sum(1 for s in encontradas if not s["definida"]),
        total=len(encontradas),
    )


def tiempo_lectura(texto: str | int) -> int:
    """Minutos de lectura. Nunca 0."""
    n = texto if isinstance(texto, int) else len(palabras(texto))
    return max(1, round(n / PALABRAS_POR_MINUTO))


def metricas_etiqueta(texto: str, paginas: int | None = None) -> dict[str, object]:
    """Bloque listo para el frontmatter de la digestión (campo ``etiqueta``)."""
    leg = legibilidad(texto)
    siglas = detectar_siglas(texto)
    salida: dict[str, object] = {
        "palabrasOriginal": leg.palabras,
        "siglasSinDefinir": siglas.sin_definir,
        "legibilidadOriginal": leg.indice,
        "tiempoLecturaOriginal": tiempo_lectura(leg.palabras),
    }
    if paginas is not None:
        salida["paginas"] = paginas
    return salida
