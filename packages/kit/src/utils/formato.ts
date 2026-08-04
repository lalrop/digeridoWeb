/**
 * Formateo de cifras para lectores chilenos.
 *
 * Regla del plan (§7): "redondear en el pipeline, no en el front. Nunca enviar
 * 14 decimales de un porcentaje." Estas funciones PRESENTAN; no arreglan datos
 * sucios. Si un número llega con 14 decimales, el bug está en el pipeline.
 */

const NUM_CL = new Intl.NumberFormat('es-CL');

/** Separador de miles con punto, decimal con coma: 186.430 / 22,5 */
export function numero(n: number, decimales = 0): string {
  return new Intl.NumberFormat('es-CL', {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  }).format(n);
}

/**
 * Pesos chilenos. `compacto` usa la convención de prensa local (M$ = miles de
 * pesos, MM$ = millones), no las abreviaturas anglo (K/M/B), que en cifras
 * fiscales chilenas se leen mal.
 *
 * Nota de unidades: MM$ significa millones de pesos. Toda cifra fiscal debe
 * declarar además su año base — eso va en el `figcaption`, no acá.
 */
export function formatoCLP(monto: number, opciones: { compacto?: boolean } = {}): string {
  const { compacto = false } = opciones;
  const signo = monto < 0 ? '−' : ''; // U+2212, no guión: alinea en tablas
  const abs = Math.abs(monto);

  if (!compacto) return `${signo}$${NUM_CL.format(Math.round(abs))}`;

  if (abs >= 1e12) return `${signo}$${numero(abs / 1e12, 1)} billones`;
  if (abs >= 1e9) return `${signo}MM$${numero(abs / 1e6, 0)}`;
  if (abs >= 1e6) return `${signo}MM$${numero(abs / 1e6, 1)}`;
  if (abs >= 1e3) return `${signo}M$${numero(abs / 1e3, 0)}`;
  return `${signo}$${numero(abs)}`;
}

/** Porcentaje ya expresado en puntos (31.4 → "31,4 %"). Espacio fino antes del signo. */
export function porcentaje(pct: number, decimales = 1): string {
  return `${numero(pct, decimales)} %`;
}

/**
 * Delta con signo explícito. En un gráfico de cambios, "+2,1" y "2,1" no son lo
 * mismo, y el lector no debería tener que inferir el signo del color (§8).
 */
export function delta(n: number, decimales = 1, sufijo = ''): string {
  const signo = n > 0 ? '+' : n < 0 ? '−' : '±';
  return `${signo}${numero(Math.abs(n), decimales)}${sufijo}`;
}

const MESES = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
] as const;

/** "14 de marzo de 2027". Sin abreviaturas: es una publicación, no un log. */
export function formatoFecha(fecha: Date | string): string {
  const d = fecha instanceof Date ? fecha : new Date(fecha);
  if (Number.isNaN(d.getTime())) throw new Error(`Fecha inválida: ${String(fecha)}`);
  return `${d.getUTCDate()} de ${MESES[d.getUTCMonth()]} de ${d.getUTCFullYear()}`;
}

/** "marzo 2027" — para ejes de tiempo y listados. */
export function formatoMesAno(fecha: Date | string): string {
  const d = fecha instanceof Date ? fecha : new Date(fecha);
  return `${MESES[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

/** ISO 8601 corto para `<time datetime>`. */
export function fechaISO(fecha: Date | string): string {
  const d = fecha instanceof Date ? fecha : new Date(fecha);
  return d.toISOString().slice(0, 10);
}

/**
 * Duración legible a partir de minutos. La etiqueta nutricional compara
 * "14 h" contra "7 min": la unidad tiene que cambiar sola.
 */
export function duracion(minutos: number): string {
  if (minutos < 1) return '< 1 min';
  if (minutos < 60) return `${Math.round(minutos)} min`;
  const horas = minutos / 60;
  if (horas < 24) return `${numero(horas, horas < 10 ? 1 : 0)} h`;
  return `${numero(horas / 24, 1)} días`;
}

/** Bytes → "412 KB". Para la página /datos/. */
export function tamano(bytes: number): string {
  const u = ['B', 'KB', 'MB', 'GB'];
  let i = 0;
  let n = bytes;
  while (n >= 1024 && i < u.length - 1) {
    n /= 1024;
    i++;
  }
  return `${numero(n, i === 0 ? 0 : 1)} ${u[i]}`;
}

/** Hash largo → "a3f9c1…8b2e" para mostrar trazabilidad sin ocupar la línea. */
export function hashCorto(sha256: string, visibles = 6): string {
  if (sha256.length <= visibles * 2) return sha256;
  return `${sha256.slice(0, visibles)}…${sha256.slice(-4)}`;
}
