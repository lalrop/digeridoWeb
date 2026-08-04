/**
 * Tipografía (§5). Tres familias, tres trabajos.
 *
 * Todas autoalojadas, subsetting a latin-ext, `font-display: swap`.
 * Solo la display se precarga (aparece sobre el pliegue en todas las páginas).
 */
export const familia = {
  /** Archivo Expanded (variable). Anchos expandidos = formularios oficiales. */
  display: "'Archivo Expanded Variable', 'Archivo', 'Helvetica Neue', Arial, sans-serif",
  /** Literata. Lectura larga en pantalla con carácter propio. */
  cuerpo: "'Literata Variable', 'Literata', Georgia, 'Times New Roman', serif",
  /** IBM Plex Mono. Folios, cifras, ejes, citas de fuente. */
  utilidad: "'IBM Plex Mono', ui-monospace, 'SF Mono', Menlo, monospace",
} as const;

export const peso = {
  regular: 400,
  media: 500,
  semi: 600,
  bold: 700,
} as const;

/**
 * Escala tipográfica fluida. Cada paso es un `clamp()` sobre el viewport, así
 * la jerarquía no se aplana en móvil ni explota en pantallas anchas.
 *
 * Razón ~1.2 en móvil y ~1.28 en desktop: los títulos crecen más rápido que el
 * cuerpo, que se queda anclado en ~18-19px por legibilidad.
 */
export const escala = {
  '3xs': 'clamp(0.688rem, 0.67rem + 0.09vw, 0.75rem)',
  '2xs': 'clamp(0.75rem, 0.73rem + 0.11vw, 0.813rem)',
  xs: 'clamp(0.813rem, 0.79rem + 0.13vw, 0.875rem)',
  sm: 'clamp(0.938rem, 0.91rem + 0.14vw, 1rem)',
  base: 'clamp(1.063rem, 1.03rem + 0.18vw, 1.188rem)',
  lg: 'clamp(1.188rem, 1.13rem + 0.29vw, 1.375rem)',
  xl: 'clamp(1.375rem, 1.27rem + 0.5vw, 1.75rem)',
  '2xl': 'clamp(1.625rem, 1.42rem + 1vw, 2.375rem)',
  '3xl': 'clamp(2rem, 1.6rem + 1.9vw, 3.25rem)',
  '4xl': 'clamp(2.375rem, 1.7rem + 3.2vw, 4.5rem)',
} as const;

export const interlinea = {
  ajustada: '1.05', // titulares grandes
  corta: '1.25', // subtítulos, bajadas
  cuerpo: '1.65', // párrafo largo: el número que más importa del sistema
  suelta: '1.8',
} as const;

export const tracking = {
  ajustado: '-0.02em',
  normal: '0',
  amplio: '0.02em',
  /** Versalitas de utilidad: folios, etiquetas de sección. */
  versalita: '0.08em',
} as const;

/** Ancho de medida. 66ch en cuerpo es el óptimo de lectura larga. */
export const medida = {
  texto: '66ch',
  angosta: '54ch',
  ancha: '78ch',
} as const;
