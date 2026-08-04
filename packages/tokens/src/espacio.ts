/**
 * Espaciado y grilla (§5).
 *
 * Escala de base 4px en pasos no lineales: los saltos grandes son los que
 * separan secciones, y deben ser inconfundibles respecto de los pequeños.
 * Si dos espaciados se parecen, uno de los dos no existe.
 */
export const espacio = {
  '3xs': '0.125rem',
  '2xs': '0.25rem',
  xs: '0.5rem',
  sm: '0.75rem',
  md: '1rem',
  lg: '1.5rem',
  xl: '2rem',
  '2xl': '3rem',
  '3xl': '4.5rem',
  '4xl': '7rem',
  '5xl': '10rem',
} as const;

/**
 * Grilla del artículo. Un solo `grid-template-columns` en el shell gobierna
 * todos los anchos de contenido; los componentes eligen carril, no píxeles.
 *
 *   [borde]  [ancho]  [texto]  [ancho]  [borde]
 *              └── figura suelta        └── figura suelta
 */
export const carril = {
  /** Columna de texto: la medida de lectura. */
  texto: 'min(66ch, 100% - 2 * var(--espacio-lg))',
  /** Figura que respira: se sale del texto sin llegar al borde. */
  ancho: 'min(56rem, 100% - 2 * var(--espacio-lg))',
  /** Gráfico a sangre completa (mapas, scrollytelling). */
  completo: '100%',
} as const;

export const radio = {
  none: '0',
  sm: '2px',
  md: '4px',
  /** El sitio es de papel y timbres: los radios grandes no pertenecen. */
  pill: '999px',
} as const;

export const sombra = {
  /** Sombras de fotocopia: desplazadas, duras, sin difusión gaussiana. */
  folio: '2px 2px 0 var(--color-borde)',
  folioFuerte: '3px 3px 0 var(--color-tinta)',
  ninguna: 'none',
} as const;

export const quiebre = {
  /** Bajo este ancho el scrollytelling reserva 55% de alto al gráfico (§6.3). */
  movil: '720px',
  tablet: '960px',
  ancho: '1280px',
} as const;

export const duracion = {
  instant: '80ms',
  rapida: '160ms',
  media: '280ms',
  lenta: '520ms',
} as const;

export const curva = {
  salida: 'cubic-bezier(0.2, 0, 0.38, 0.9)',
  entrada: 'cubic-bezier(0.4, 0.14, 0.3, 1)',
  estandar: 'cubic-bezier(0.4, 0.14, 0.3, 1)',
} as const;

/** Capas. Declaradas aquí para que nadie invente un z-index: 9999. */
export const capa = {
  base: 0,
  grafico: 10,
  sticky: 20,
  tooltip: 30,
  barra: 40,
  modal: 50,
} as const;
