/**
 * Casos compartidos con `pipelines/_common/legibilidad.py`.
 *
 * La Etiqueta Nutricional compara el índice del documento original (calculado
 * en Python) con el del digerido (calculado acá). Si las dos implementaciones
 * se separan, la comparación miente. Estos casos son el contrato entre ambas:
 * cualquier cambio en uno tiene que replicarse en el otro y en
 * `tests/test_legibilidad.py`.
 */
import { describe, expect, it } from 'vitest';

import {
  contarSilabas, detectarSiglas, frases, legibilidad, tiempoLectura,
} from './legibilidad.js';

describe('contarSilabas', () => {
  const casos: Array<[string, number]> = [
    ['casa', 2],
    ['presupuesto', 4],
    ['ciudad', 2],        // diptongo iu
    ['aéreo', 4],         // hiato fuerte-fuerte, dos veces
    ['país', 2],          // hiato por débil tildada
    ['baúl', 2],
    ['cuidado', 3],       // diptongo ui
    ['queso', 2],         // u muda
    ['guerra', 2],        // u muda
    ['pingüino', 3],      // ü sí suena
    ['buey', 1],          // triptongo
    ['ley', 1],
    ['a', 1],
    ['y', 1],
    ['transparencia', 4],
    ['ejecución', 4],
    ['presupuestaria', 5],
  ];

  for (const [palabra, esperado] of casos) {
    it(`"${palabra}" → ${esperado}`, () => {
      expect(contarSilabas(palabra)).toBe(esperado);
    });
  }

  it('no devuelve 0 para palabras con letras', () => {
    for (const w of ['sí', 'no', 'ah']) expect(contarSilabas(w)).toBeGreaterThanOrEqual(1);
  });

  it('devuelve 0 para cadenas sin letras', () => {
    expect(contarSilabas('1.234')).toBe(0);
    expect(contarSilabas('—')).toBe(0);
  });
});

describe('frases', () => {
  it('corta en puntuación fuerte', () => {
    expect(frases('Uno. Dos. Tres.')).toHaveLength(3);
  });

  it('NO corta dentro de cifras con separador de miles', () => {
    // Este es el caso que arruina la medición de un documento presupuestario.
    expect(frases('El total llega a 1.234.567 pesos este año.')).toHaveLength(1);
  });

  it('NO corta en abreviaturas de normativa', () => {
    expect(frases('Según el Art. 4 del D.F.L. N° 1, el gasto sube.')).toHaveLength(1);
  });

  it('corta en párrafos aunque falte el punto', () => {
    expect(frases('Primer párrafo\n\nSegundo párrafo')).toHaveLength(2);
  });

  it('ignora fragmentos vacíos', () => {
    expect(frases('Hola...  ¿Qué tal?  ')).toHaveLength(2);
  });
});

describe('legibilidad', () => {
  it('prosa simple puntúa alto', () => {
    const r = legibilidad('El gato come. La casa es alta. El sol sale.');
    expect(r.indice).toBeGreaterThan(85);
    expect(r.nivel).toMatch(/fácil/);
  });

  it('jerga administrativa puntúa bajo', () => {
    const burocracia =
      'La individualización precedentemente consignada se entenderá supeditada ' +
      'a la verificación de la concurrencia copulativa de los requisitos ' +
      'establecidos reglamentariamente en la normativa presupuestaria vigente, ' +
      'sin perjuicio de las facultades interpretativas correspondientes.';
    const r = legibilidad(burocracia);
    expect(r.indice).toBeLessThan(40);
    expect(r.nivel).toMatch(/difícil/);
  });

  it('el índice está recortado a 0–100', () => {
    const absurdo = `${'contrarrevolucionariamente '.repeat(80)}.`;
    const r = legibilidad(absurdo);
    expect(r.indice).toBeGreaterThanOrEqual(0);
    expect(r.indice).toBeLessThanOrEqual(100);
  });

  it('texto vacío no explota', () => {
    const r = legibilidad('');
    expect(r.indice).toBe(0);
    expect(r.nivel).toBe('sin texto');
    expect(r.palabras).toBe(0);
  });

  it('digerir un texto sube su índice (la premisa del sitio)', () => {
    const original =
      'No obstante lo precedentemente expuesto, la asignación presupuestaria ' +
      'correspondiente experimentará una variación porcentual equivalente al ' +
      'treinta y uno por ciento respecto del ejercicio inmediatamente anterior.';
    const digerido = 'El presupuesto de salud sube 31 %. Es el mayor alza del año.';
    expect(legibilidad(digerido).indice).toBeGreaterThan(legibilidad(original).indice);
  });

  it('reporta las magnitudes intermedias para poder auditar la cifra', () => {
    const r = legibilidad('El gato come. La casa es alta.');
    expect(r.palabras).toBe(7);
    expect(r.frases).toBe(2);
    expect(r.silabasPorPalabra).toBeGreaterThan(1);
    expect(r.palabrasPorFrase).toBeCloseTo(3.5, 1);
  });
});

describe('detectarSiglas', () => {
  it('cuenta las no definidas', () => {
    const r = detectarSiglas('El informe de la SUBDERE menciona el FNDR y el PMU.');
    expect(r.sinDefinir).toBe(3);
    expect(r.total).toBe(3);
  });

  it('reconoce "Expansión (SIGLA)" como definida', () => {
    const r = detectarSiglas('La Subsecretaría de Desarrollo Regional (SUBDERE) informó.');
    expect(r.encontradas.find((s) => s.sigla === 'SUBDERE')?.definida).toBe(true);
    expect(r.sinDefinir).toBe(0);
  });

  it('reconoce "SIGLA (expansión)" como definida', () => {
    const r = detectarSiglas('El FNDR (Fondo Nacional de Desarrollo Regional) creció.');
    expect(r.encontradas.find((s) => s.sigla === 'FNDR')?.definida).toBe(true);
  });

  it('no cuenta siglas de dominio público', () => {
    const r = detectarSiglas('El IVA y el PIB subieron según el INE.');
    expect(r.sinDefinir).toBe(0);
  });

  it('no confunde numerales romanos con siglas', () => {
    const r = detectarSiglas('La Región XIV y el capítulo III del informe.');
    expect(r.encontradas.map((s) => s.sigla)).not.toContain('XIV');
    expect(r.encontradas.map((s) => s.sigla)).not.toContain('III');
  });

  it('acumula frecuencia y ordena por ella', () => {
    const r = detectarSiglas('SUBDERE, SUBDERE y SUBDERE contra un solo FNDR.');
    expect(r.encontradas[0]).toMatchObject({ sigla: 'SUBDERE', veces: 3 });
    expect(r.total).toBe(2);
  });

  it('no cuenta las palabras de un titular en mayúsculas', () => {
    // Bug real encontrado corriendo el pipeline: "INFORME DE EJECUCIÓN
    // PRESUPUESTARIA SINTÉTICO" aportaba 4 siglas sin definir, e inflaba una
    // cifra destacada de la Etiqueta Nutricional.
    const r = detectarSiglas('INFORME DE EJECUCIÓN PRESUPUESTARIA SINTÉTICO\n\nLa SUBDERE informó.');
    const siglas = r.encontradas.map((s) => s.sigla);
    expect(siglas).toEqual(['SUBDERE']);
    expect(r.sinDefinir).toBe(1);
  });

  it('sigue detectando una sigla suelta dentro de una frase', () => {
    const r = detectarSiglas('La SUBDERE informó al FNDR sobre el PMU.');
    expect(r.total).toBe(3);
  });

  it('descarta palabras con tilde: una sigla no lleva tilde', () => {
    const r = detectarSiglas('La palabra EJECUCIÓN no es una sigla.');
    expect(r.encontradas.map((s) => s.sigla)).not.toContain('EJECUCIÓN');
  });

  it('descarta preposiciones en mayúscula', () => {
    const r = detectarSiglas('GASTO POR REGIÓN Y COMUNA');
    expect(r.encontradas.map((s) => s.sigla)).not.toContain('POR');
  });
});


describe('tiempoLectura', () => {
  it('acepta un conteo de palabras directo', () => {
    expect(tiempoLectura(1400)).toBe(7); // 1400 / 200
  });

  it('nunca devuelve 0 minutos', () => {
    expect(tiempoLectura('Tres palabras acá')).toBe(1);
  });

  it('usa la misma constante que el pipeline (original vs digerido comparables)', () => {
    expect(tiempoLectura(186_430)).toBe(932); // ~15,5 h del documento original
  });
});
