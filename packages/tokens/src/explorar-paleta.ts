/**
 * Buscador de paletas categóricas CVD-seguras.  `pnpm -F @digerido/tokens explorar`
 *
 * Herramienta de diseño, NO un test: la búsqueda es exhaustiva y no tiene
 * sentido pagarla en cada CI. Se corre a mano cuando hay que cambiar la escala
 * categórica, y su resultado se congela en `color.ts` con los invariantes
 * verificados por `color.test.ts`.
 *
 * Restricciones que impone:
 *   1. contraste >= 3:1 sobre `papel` (marca de datos legible sobre el fondo)
 *   2. una familia de tono por serie (dos naranjas distintos NO son dos series:
 *      pasan ΔE y fallan el propósito)
 *   3. ΔE76 > 18 entre todo par, bajo visión normal, deuteranopía y protanopía
 *
 * Objetivo: maximizar la ΔE mínima. Reporta la mejor solución para cada k.
 */
import { marca } from './color.js';
import { contraste, deltaE, simularCVD, type TipoCVD } from './contraste.js';

const CVD: TipoCVD[] = ['deuteranopia', 'protanopia'];
const MODOS = ['normal', ...CVD] as const;
const DELTA_MINIMO = 18;

/** Candidatos: Okabe-Ito y variantes oscurecidas por familia de tono. */
const CANDIDATOS = [
  '#0072B2', '#005B8F', '#004E7A', '#1F6E9C', '#2E8CC4',
  '#D55E00', '#A8480C', '#8C3A17', '#B85200', '#C25A0A',
  '#006B4F', '#00785A', '#00563F', '#0A7A5C',
  '#A14C7B', '#B85C8A', '#8E3F6B', '#CC79A7',
  '#463869', '#5B4B8A', '#3B2F58', '#6A5A99',
  '#3F4144', '#56585B', '#6E7175', '#2B2D30',
  '#8A6100', '#B37C00', '#6E4D00',
];

/** Tono HSL en grados; -1 para acromáticos. */
function tono(hex: string): number {
  const h = hex.replace('#', '');
  const [r, g, b] = [0, 2, 4].map((i) => Number.parseInt(h.slice(i, i + 2), 16) / 255) as [
    number, number, number,
  ];
  const mx = Math.max(r, g, b);
  const d = mx - Math.min(r, g, b);
  if (d < 0.02) return -1;
  const bruto = mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
  return (bruto * 60 + 360) % 360;
}

/** Bins de 45°, más una familia acromática. */
const familia = (c: string): string => {
  const t = tono(c);
  return t < 0 ? 'acromatico' : `tono-${Math.floor(t / 45)}`;
};

function peorPar(set: readonly string[]): { delta: number; par: string } {
  let delta = Number.POSITIVE_INFINITY;
  let par = '';
  for (const modo of MODOS) {
    const ver = (c: string) => (modo === 'normal' ? c : simularCVD(c, modo));
    for (let i = 0; i < set.length; i++) {
      for (let j = i + 1; j < set.length; j++) {
        const d = deltaE(ver(set[i]!), ver(set[j]!));
        if (d < delta) {
          delta = d;
          par = `${set[i]}/${set[j]} @${modo}`;
        }
      }
    }
  }
  return { delta, par };
}

const viables = CANDIDATOS.filter((c) => contraste(c, marca.papel) >= 3);
console.log(`candidatos: ${CANDIDATOS.length} → viables (>=3:1 sobre papel): ${viables.length}\n`);

for (const k of [3, 4, 5, 6, 7]) {
  let mejor: { set: string[]; delta: number; par: string } | null = null;

  const recorrer = (inicio: number, acc: string[], familias: Set<string>) => {
    if (acc.length === k) {
      const { delta, par } = peorPar(acc);
      if (!mejor || delta > mejor.delta) mejor = { set: [...acc], delta, par };
      return;
    }
    // Poda: no alcanzan los candidatos restantes para completar k.
    if (viables.length - inicio < k - acc.length) return;
    for (let i = inicio; i < viables.length; i++) {
      const c = viables[i]!;
      const f = familia(c);
      if (familias.has(f)) continue; // una familia de tono por serie
      familias.add(f);
      recorrer(i + 1, [...acc, c], familias);
      familias.delete(f);
    }
  };
  recorrer(0, [], new Set());

  const m = mejor as { set: string[]; delta: number; par: string } | null;
  if (!m) {
    console.log(`k=${k}  SIN SOLUCIÓN con familias de tono distintas`);
  } else {
    const marca_ = m.delta > DELTA_MINIMO ? 'OK  ' : 'BAJO';
    console.log(`k=${k}  ${marca_} minΔE=${m.delta.toFixed(1)}  ${m.set.join(' ')}  (peor: ${m.par})`);
  }
}
