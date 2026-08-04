"""Contrato entre las dos implementaciones de legibilidad.

Estos casos son LOS MISMOS que los de
``packages/kit/src/utils/legibilidad.test.ts``, a propósito.

La Etiqueta Nutricional compara el índice del documento original (calculado en
Python) contra el del texto digerido (calculado en TypeScript). Si las dos
implementaciones se separan, la comparación —que es el argumento central del
sitio— miente. Cambiar una obliga a cambiar la otra, y este archivo es el que
avisa.
"""

from __future__ import annotations

import pytest

from pipelines._common.legibilidad import (
    contar_silabas,
    detectar_siglas,
    frases,
    legibilidad,
    tiempo_lectura,
)


@pytest.mark.parametrize(
    ("palabra", "esperado"),
    [
        ("casa", 2),
        ("presupuesto", 4),
        ("ciudad", 2),  # diptongo iu
        ("aéreo", 4),  # hiato fuerte-fuerte, dos veces
        ("país", 2),  # hiato por débil tildada
        ("baúl", 2),
        ("cuidado", 3),  # diptongo ui
        ("queso", 2),  # u muda
        ("guerra", 2),  # u muda
        ("pingüino", 3),  # ü sí suena
        ("buey", 1),  # triptongo
        ("ley", 1),
        ("a", 1),
        ("y", 1),
        ("transparencia", 4),
        ("ejecución", 4),
        ("presupuestaria", 5),
    ],
)
def test_contar_silabas(palabra: str, esperado: int) -> None:
    assert contar_silabas(palabra) == esperado


def test_silabas_minimo_uno() -> None:
    for w in ("sí", "no", "ah"):
        assert contar_silabas(w) >= 1


def test_silabas_sin_letras() -> None:
    assert contar_silabas("1.234") == 0
    assert contar_silabas("—") == 0


def test_frases_corta_en_puntuacion() -> None:
    assert len(frases("Uno. Dos. Tres.")) == 3


def test_frases_no_corta_en_separador_de_miles() -> None:
    # El caso que arruina la medición de cualquier documento presupuestario.
    assert len(frases("El total llega a 1.234.567 pesos este año.")) == 1


def test_frases_no_corta_en_abreviaturas() -> None:
    assert len(frases("Según el Art. 4 del D.F.L. N° 1, el gasto sube.")) == 1


def test_frases_corta_en_parrafos() -> None:
    assert len(frases("Primer párrafo\n\nSegundo párrafo")) == 2


def test_frases_ignora_vacios() -> None:
    assert len(frases("Hola...  ¿Qué tal?  ")) == 2


def test_prosa_simple_puntua_alto() -> None:
    r = legibilidad("El gato come. La casa es alta. El sol sale.")
    assert r.indice > 85
    assert "fácil" in r.nivel


def test_jerga_administrativa_puntua_bajo() -> None:
    burocracia = (
        "La individualización precedentemente consignada se entenderá supeditada "
        "a la verificación de la concurrencia copulativa de los requisitos "
        "establecidos reglamentariamente en la normativa presupuestaria vigente, "
        "sin perjuicio de las facultades interpretativas correspondientes."
    )
    r = legibilidad(burocracia)
    assert r.indice < 40
    assert "difícil" in r.nivel


def test_indice_recortado() -> None:
    r = legibilidad("contrarrevolucionariamente " * 80 + ".")
    assert 0 <= r.indice <= 100


def test_texto_vacio() -> None:
    r = legibilidad("")
    assert r.indice == 0
    assert r.nivel == "sin texto"
    assert r.palabras == 0


def test_digerir_sube_el_indice() -> None:
    """La premisa del sitio, como test."""
    original = (
        "No obstante lo precedentemente expuesto, la asignación presupuestaria "
        "correspondiente experimentará una variación porcentual equivalente al "
        "treinta y uno por ciento respecto del ejercicio inmediatamente anterior."
    )
    digerido = "El presupuesto de salud sube 31 %. Es el mayor alza del año."
    assert legibilidad(digerido).indice > legibilidad(original).indice


def test_magnitudes_intermedias_auditables() -> None:
    r = legibilidad("El gato come. La casa es alta.")
    assert r.palabras == 7
    assert r.frases == 2
    assert r.silabas_por_palabra > 1
    assert r.palabras_por_frase == pytest.approx(3.5, abs=0.1)


def test_siglas_sin_definir() -> None:
    r = detectar_siglas("El informe de la SUBDERE menciona el FNDR y el PMU.")
    assert r.sin_definir == 3
    assert r.total == 3


def test_sigla_definida_expansion_primero() -> None:
    r = detectar_siglas("La Subsecretaría de Desarrollo Regional (SUBDERE) informó.")
    assert next(s for s in r.encontradas if s["sigla"] == "SUBDERE")["definida"] is True
    assert r.sin_definir == 0


def test_sigla_definida_sigla_primero() -> None:
    r = detectar_siglas("El FNDR (Fondo Nacional de Desarrollo Regional) creció.")
    assert next(s for s in r.encontradas if s["sigla"] == "FNDR")["definida"] is True


def test_siglas_de_dominio_publico() -> None:
    r = detectar_siglas("El IVA y el PIB subieron según el INE.")
    assert r.sin_definir == 0


def test_no_confunde_romanos_con_siglas() -> None:
    r = detectar_siglas("La Región XIV y el capítulo III del informe.")
    siglas = [s["sigla"] for s in r.encontradas]
    assert "XIV" not in siglas
    assert "III" not in siglas


def test_frecuencia_y_orden() -> None:
    r = detectar_siglas("SUBDERE, SUBDERE y SUBDERE contra un solo FNDR.")
    assert r.encontradas[0]["sigla"] == "SUBDERE"
    assert r.encontradas[0]["veces"] == 3
    assert r.total == 2


def test_no_cuenta_palabras_de_titular_en_mayusculas() -> None:
    """Bug real encontrado corriendo el pipeline.

    "INFORME DE EJECUCIÓN PRESUPUESTARIA SINTÉTICO" aportaba 4 siglas sin
    definir, e inflaba una cifra destacada de la Etiqueta Nutricional.
    """
    r = detectar_siglas("INFORME DE EJECUCIÓN PRESUPUESTARIA SINTÉTICO\n\nLa SUBDERE informó.")
    assert [s["sigla"] for s in r.encontradas] == ["SUBDERE"]
    assert r.sin_definir == 1


def test_sigla_suelta_en_frase_sigue_detectada() -> None:
    r = detectar_siglas("La SUBDERE informó al FNDR sobre el PMU.")
    assert r.total == 3


def test_descarta_palabras_con_tilde() -> None:
    r = detectar_siglas("La palabra EJECUCIÓN no es una sigla.")
    assert "EJECUCIÓN" not in [s["sigla"] for s in r.encontradas]


def test_descarta_preposiciones_en_mayuscula() -> None:
    r = detectar_siglas("GASTO POR REGIÓN Y COMUNA")
    assert "POR" not in [s["sigla"] for s in r.encontradas]


def test_tiempo_lectura_desde_conteo() -> None:
    assert tiempo_lectura(1400) == 7


def test_tiempo_lectura_nunca_cero() -> None:
    assert tiempo_lectura("Tres palabras acá") == 1


def test_tiempo_lectura_constante_compartida() -> None:
    # Mismo caso que en legibilidad.test.ts: si una implementación cambia la
    # constante, este test y su gemelo divergen.
    assert tiempo_lectura(186_430) == 932
