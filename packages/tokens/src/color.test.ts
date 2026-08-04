/**
 * Invariantes de accesibilidad de la paleta (§8: "no negociable").
 *
 * Este archivo es la razón por la que §5 puede afirmar que las escalas están
 * "probadas contra deuteranopía y protanopía". Ya encontró dos colisiones
 * reales durante la Fase 0: el `pulpa` de marca contra el azul bajo
 * protanopía, y el verde Okabe-Ito #009E73 quedándose en 2.93:1 sobre papel.
 *
 * Para explorar alternativas cuando haga falta cambiar la paleta:
 *   pnpm -F @digerido/tokens explorar
 */
import { describe, expect, it } from 'vitest';

import { grafico, marca, MAX_CATEGORICA, superficie } from './color.js';
import { contraste, deltaE, simularCVD, type TipoCVD } from './contraste.js';

const CVD: TipoCVD[] = ['deuteranopia', 'protanopia'];
const MODOS = ['normal', ...CVD] as const;

/** Umbral ΔE76 bajo el cual dos marcas de datos se leen como la misma serie. */
const DELTA_MINIMO = 18;

/** Percibido según el modo de visión. */
const ver = (hex: string, modo: (typeof MODOS)[number]) =>
  modo === 'normal' ? hex : simularCVD(hex, modo);

describe('texto sobre papel: contraste AA', () => {
  const casos: Array<[string, string, number]> = [
    ['tinta / papel (cuerpo)', marca.tinta, 4.5],
    ['tintaSuave / papel (secundario)', superficie.tintaSuave, 4.5],
    ['sello / papel (metadatos, texto chico)', marca.sello, 4.5],
    ['bilis / papel (énfasis)', marca.bilis, 3],
    ['pulpa / papel', marca.pulpa, 4.5],
  ];

  for (const [nombre, color, minimo] of casos) {
    it(`${nombre} >= ${minimo}:1`, () => {
      expect(contraste(color, marca.papel)).toBeGreaterThanOrEqual(minimo);
    });
  }

  // `enzima` es un verde ácido: NO sirve como texto, solo como foco/estado
  // activo sobre tinta. El test fija esa restricción para que nadie lo use
  // como color de link sobre papel.
  it('enzima NO alcanza AA sobre papel (es color de interacción, no de texto)', () => {
    expect(contraste(marca.enzima, marca.papel)).toBeLessThan(3);
  });

  it('enzima sí funciona como foco sobre tinta', () => {
    expect(contraste(marca.enzima, marca.tinta)).toBeGreaterThanOrEqual(3);
  });
});

describe('escala categórica', () => {
  const { categorica } = grafico;

  it('tiene exactamente MAX_CATEGORICA entradas', () => {
    // Si alguien agrega una sexta, o el tope y la escala se desincronizan,
    // esto falla antes de que un gráfico use un color no verificado.
    expect(categorica).toHaveLength(MAX_CATEGORICA);
  });

  it('no repite valores', () => {
    expect(new Set(categorica).size).toBe(categorica.length);
  });

  it('toda marca alcanza 3:1 sobre papel', () => {
    for (const c of categorica) {
      expect(contraste(c, marca.papel), `${c} sobre papel`).toBeGreaterThanOrEqual(3);
    }
  });

  for (const modo of MODOS) {
    it(`todo par se distingue bajo ${modo}`, () => {
      for (let i = 0; i < categorica.length; i++) {
        for (let j = i + 1; j < categorica.length; j++) {
          const [a, b] = [categorica[i]!, categorica[j]!];
          const d = deltaE(ver(a, modo), ver(b, modo));
          expect(d, `${a} vs ${b} bajo ${modo}`).toBeGreaterThan(DELTA_MINIMO);
        }
      }
    });
  }

  it('el primer par (el caso más común) es el más separado que existe', () => {
    // Un gráfico de dos series usa slice(0,2). Ese par merece el margen mayor.
    const [a, b] = [categorica[0]!, categorica[1]!];
    const peorDelPrimerPar = Math.min(...MODOS.map((m) => deltaE(ver(a, m), ver(b, m))));
    expect(peorDelPrimerPar).toBeGreaterThan(DELTA_MINIMO * 1.5);
  });
});

describe('escala secuencial', () => {
  it('el contraste sobre papel crece paso a paso', () => {
    const razones = grafico.secuencial.map((c) => contraste(c, marca.papel));
    for (let i = 1; i < razones.length; i++) {
      expect(razones[i]!, `paso ${i + 1} vs ${i}`).toBeGreaterThan(razones[i - 1]!);
    }
  });

  it('sigue siendo monótona bajo dicromacia (el orden es el dato)', () => {
    for (const tipo of CVD) {
      const razones = grafico.secuencial.map((c) => contraste(simularCVD(c, tipo), marca.papel));
      for (let i = 1; i < razones.length; i++) {
        expect(razones[i]!, `${tipo}, paso ${i + 1}`).toBeGreaterThan(razones[i - 1]!);
      }
    }
  });

  it('los pasos consecutivos se distinguen entre sí', () => {
    for (const modo of MODOS) {
      const s = grafico.secuencial;
      for (let i = 1; i < s.length; i++) {
        const d = deltaE(ver(s[i]!, modo), ver(s[i - 1]!, modo));
        expect(d, `${modo}, paso ${i + 1} vs ${i}`).toBeGreaterThan(6);
      }
    }
  });

  it('el paso más claro necesita filete: se declara el token', () => {
    // Documenta la restricción en vez de dejarla en un comentario: los dos
    // pasos claros son casi invisibles sobre papel y exigen borde.
    expect(contraste(grafico.secuencial[0]!, marca.papel)).toBeLessThan(2);
    expect(contraste(grafico.filete, marca.papel)).toBeGreaterThanOrEqual(1.5);
  });
});

describe('escala divergente', () => {
  const d = grafico.divergente;

  it('tiene cantidad impar de pasos: el centro es el cero', () => {
    expect(d.length % 2).toBe(1);
  });

  it('los brazos son monótonos hacia afuera desde el centro', () => {
    const medio = (d.length - 1) / 2;
    for (const modo of MODOS) {
      const razon = (c: string) => contraste(ver(c, modo), marca.papel);
      for (let i = medio + 1; i < d.length; i++) {
        expect(razon(d[i]!), `${modo}, brazo alto paso ${i}`).toBeGreaterThan(razon(d[i - 1]!));
      }
      for (let i = medio - 1; i >= 0; i--) {
        expect(razon(d[i]!), `${modo}, brazo bajo paso ${i}`).toBeGreaterThan(razon(d[i + 1]!));
      }
    }
  });

  it('los extremos se distinguen entre sí (recorte vs. aumento)', () => {
    for (const modo of MODOS) {
      expect(deltaE(ver(d[0]!, modo), ver(d[d.length - 1]!, modo)), modo).toBeGreaterThan(
        DELTA_MINIMO,
      );
    }
  });
});

describe('destacado vs contexto', () => {
  it('el destacado se separa del contexto incluso bajo dicromacia', () => {
    for (const modo of MODOS) {
      const dist = deltaE(ver(grafico.destacado, modo), ver(grafico.contexto, modo));
      expect(dist, modo).toBeGreaterThan(DELTA_MINIMO);
    }
  });

  it('"sin dato" se distingue de toda marca con valor', () => {
    for (const c of [...grafico.categorica, grafico.destacado, grafico.contexto]) {
      expect(deltaE(c, grafico.sinDato), `${c} vs sinDato`).toBeGreaterThan(DELTA_MINIMO);
    }
  });
});

describe('utilidades de contraste', () => {
  it('contraste es simétrico y acotado', () => {
    expect(contraste('#000000', '#FFFFFF')).toBeCloseTo(21, 1);
    expect(contraste('#FFFFFF', '#000000')).toBeCloseTo(21, 1);
    expect(contraste(marca.papel, marca.papel)).toBeCloseTo(1, 5);
  });

  it('rechaza hex inválido en vez de devolver negro silenciosamente', () => {
    expect(() => contraste('rojo', marca.papel)).toThrow(/hex inválido/);
    expect(() => contraste('#FFF', marca.papel)).toThrow(/hex inválido/);
  });

  it('un gris es invariante bajo dicromacia', () => {
    // Control de sanidad del simulador: si un acromático cambia, la matriz
    // está mal y todos los demás resultados son basura.
    for (const tipo of CVD) {
      expect(deltaE(simularCVD('#808080', tipo), '#808080')).toBeLessThan(2);
    }
  });
});
