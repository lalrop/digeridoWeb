/**
 * Acceso a las escalas de gráfico con las restricciones puestas en el código.
 *
 * §8 dice "nunca codificar información solo por color" y §5 fija el tope de la
 * escala categórica. Una regla que vive solo en un comentario se rompe en la
 * tercera digestión, cuando ya nadie recuerda por qué existía. Estas funciones
 * la hacen fallar en el acto.
 */
import { grafico, MAX_CATEGORICA } from '@digerido/tokens';

/**
 * Devuelve los primeros `n` colores categóricos.
 *
 * Lanza si `n` supera el tope verificado contra dicromacia: a partir de la
 * sexta serie hay que rotular directo o facetar, no estirar la paleta.
 */
export function escalaCategorica(n: number): string[] {
  if (!Number.isInteger(n) || n < 1) {
    throw new Error(`escalaCategorica(${n}): se espera un entero >= 1`);
  }
  if (n > MAX_CATEGORICA) {
    throw new Error(
      `escalaCategorica(${n}): la escala categórica tope en ${MAX_CATEGORICA} series. ` +
        'Con más de eso los colores dejan de distinguirse bajo deuteranopía y protanopía. ' +
        'Usá etiqueta directa, facetado (small multiples) o agrupá las series menores en "otros".',
    );
  }
  return grafico.categorica.slice(0, n);
}

/**
 * Patrón destacado/contexto: una serie protagonista y el resto en gris.
 *
 * Es el recurso correcto cuando hay muchas categorías y una sola importa —
 * mucho más legible que N colores, y no tiene tope.
 */
export function escalaDestacado<T>(
  items: readonly T[],
  esDestacado: (item: T, i: number) => boolean,
): string[] {
  return items.map((item, i) => (esDestacado(item, i) ? grafico.destacado : grafico.contexto));
}

/** Interpola la rampa secuencial en `n` pasos discretos (n <= largo de la rampa). */
export function escalaSecuencial(n: number): string[] {
  const rampa = grafico.secuencial;
  if (n < 1) throw new Error(`escalaSecuencial(${n}): se espera n >= 1`);
  if (n === 1) return [rampa[rampa.length - 1]!];
  // Muestrea la rampa en n puntos equiespaciados, extremos incluidos.
  return Array.from({ length: n }, (_, i) => {
    const t = i / (n - 1);
    return rampa[Math.round(t * (rampa.length - 1))]!;
  });
}

/**
 * Divergente centrada en cero. Devuelve el color para un valor dado su máximo
 * absoluto, de modo que el cero caiga siempre en el paso neutro.
 */
export function colorDivergente(valor: number, maxAbsoluto: number): string {
  const d = grafico.divergente;
  const medio = (d.length - 1) / 2;
  if (maxAbsoluto === 0 || !Number.isFinite(valor)) return d[medio]!;
  const t = Math.max(-1, Math.min(1, valor / maxAbsoluto));
  return d[Math.round(medio + t * medio)]!;
}

/**
 * ¿Necesita filete esta marca? Los pasos claros de la secuencial y la
 * divergente casi desaparecen sobre el papel (§5).
 */
export function necesitaFilete(color: string): boolean {
  const claros = new Set<string>([
    grafico.secuencial[0], grafico.secuencial[1],
    grafico.divergente[2], grafico.divergente[3], grafico.divergente[4],
    grafico.sinDato,
  ]);
  return claros.has(color);
}

export { grafico, MAX_CATEGORICA };
