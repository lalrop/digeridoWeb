/**
 * Utilidades de contraste y simulación de daltonismo.
 *
 * Viven en `tokens` a propósito: la accesibilidad de la paleta se verifica en
 * el mismo paquete que la define, y el test corre en CI. Una paleta cuya
 * accesibilidad se afirma en un README pero no se mide es una paleta sin
 * verificar (§8).
 */

export type RGB = readonly [number, number, number];

export function aRGB(hex: string): RGB {
  const h = hex.replace('#', '').trim();
  if (!/^[0-9a-fA-F]{6}$/.test(h)) {
    throw new Error(`Color hex inválido: "${hex}" (se espera #RRGGBB)`);
  }
  return [
    Number.parseInt(h.slice(0, 2), 16),
    Number.parseInt(h.slice(2, 4), 16),
    Number.parseInt(h.slice(4, 6), 16),
  ];
}

export function aHex([r, g, b]: RGB): string {
  const c = (n: number) =>
    Math.round(Math.min(255, Math.max(0, n)))
      .toString(16)
      .padStart(2, '0');
  return `#${c(r)}${c(g)}${c(b)}`.toUpperCase();
}

/** sRGB 0-255 → lineal 0-1 (inversa de la transferencia gamma). */
const aLineal = (c: number): number => {
  const s = c / 255;
  return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
};

const aGamma = (c: number): number => {
  const s = c <= 0.0031308 ? c * 12.92 : 1.055 * c ** (1 / 2.4) - 0.055;
  return s * 255;
};

/** Luminancia relativa WCAG 2.x. */
export function luminanciaRelativa(hex: string): number {
  const [r, g, b] = aRGB(hex).map(aLineal) as unknown as RGB;
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** Razón de contraste WCAG 2.x: 1 (idénticos) a 21 (negro/blanco). */
export function contraste(a: string, b: string): number {
  const la = luminanciaRelativa(a);
  const lb = luminanciaRelativa(b);
  const [claro, oscuro] = la > lb ? [la, lb] : [lb, la];
  return (claro + 0.05) / (oscuro + 0.05);
}

/**
 * Simulación de dicromacia por el método de Viénot, Brettel & Mollon (1999):
 * proyección sobre el plano de confusión en espacio LMS.
 *
 * Suficientemente fiel para decidir si dos series de un gráfico se confunden.
 * No pretende reemplazar una prueba con personas.
 */
const RGB_A_LMS = [
  [0.31399022, 0.63951294, 0.04649755],
  [0.15537241, 0.75789446, 0.08670142],
  [0.01775239, 0.10944209, 0.87256922],
] as const;

const LMS_A_RGB = [
  [5.47221206, -4.6419601, 0.16963708],
  [-1.1252419, 2.29317094, -0.1678952],
  [0.02980165, -0.19318073, 1.16364789],
] as const;

/** Matrices de proyección en LMS para cada dicromacia. */
const PROYECCION = {
  protanopia: [
    [0, 1.05118294, -0.05116099],
    [0, 1, 0],
    [0, 0, 1],
  ],
  deuteranopia: [
    [1, 0, 0],
    [0.9513092, 0, 0.04866992],
    [0, 0, 1],
  ],
  tritanopia: [
    [1, 0, 0],
    [0, 1, 0],
    [-0.86744736, 1.86727089, 0],
  ],
} as const;

export type TipoCVD = keyof typeof PROYECCION;

const aplicar = (m: readonly (readonly number[])[], v: RGB): RGB =>
  m.map((fila) => fila.reduce((acc, k, i) => acc + k * (v[i] ?? 0), 0)) as unknown as RGB;

/** Devuelve el hex tal como lo percibe una persona con la dicromacia dada. */
export function simularCVD(hex: string, tipo: TipoCVD): string {
  const lineal = aRGB(hex).map(aLineal) as unknown as RGB;
  const lms = aplicar(RGB_A_LMS, lineal);
  const proyectado = aplicar(PROYECCION[tipo], lms);
  const devuelta = aplicar(LMS_A_RGB, proyectado);
  return aHex(devuelta.map(aGamma) as unknown as RGB);
}

/**
 * Distancia perceptual aproximada en CIELAB (ΔE76) — barata y suficiente para
 * un test de "¿se distinguen estas dos series?".
 */
export function deltaE(a: string, b: string): number {
  const [l1, a1, b1] = aLab(a);
  const [l2, a2, b2] = aLab(b);
  return Math.hypot(l1 - l2, a1 - a2, b1 - b2);
}

function aLab(hex: string): RGB {
  const [r, g, b] = aRGB(hex).map(aLineal) as unknown as RGB;
  // sRGB lineal → XYZ (D65)
  const x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047;
  const y = 0.2126729 * r + 0.7151522 * g + 0.072175 * b;
  const z = (0.0193339 * r + 0.119192 * g + 0.9503041 * b) / 1.08883;
  const f = (t: number) => (t > 216 / 24389 ? Math.cbrt(t) : (841 / 108) * t + 4 / 29);
  const [fx, fy, fz] = [f(x), f(y), f(z)];
  return [116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)];
}
