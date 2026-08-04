/**
 * Consultas de contenido, en un solo lugar.
 *
 * La regla de qué es público vive acá y solo acá: si cada página filtra por su
 * cuenta, tarde o temprano una olvida excluir un borrador y una pieza a medias
 * aparece en el RSS. Toda página e índice pasa por estas funciones.
 */
import { getCollection, type CollectionEntry } from 'astro:content';

import { incluirEjemplos } from './entorno';

export type Digestion = CollectionEntry<'digestiones'>;

/**
 * Lo que un lector puede encontrar navegando: publicadas y archivadas.
 * Las archivadas siguen accesibles por URL —los enlaces no deben morir— pero no
 * encabezan los índices.
 */
export async function digestionesPublicas(): Promise<Digestion[]> {
  const todas = await getCollection('digestiones', ({ data }) => {
    if (data.estado === 'publicada') return true;
    // Borradores y piezas de ejemplo: visibles solo en desarrollo.
    return incluirEjemplos;
  });

  return todas.sort(porFecha);
}

/**
 * Lo que se indexa, comparte y difunde: solo publicadas y nunca una pieza con
 * datos sintéticos. Es el filtro del RSS, del sitemap y de la home.
 */
export async function digestionesDifundibles(): Promise<Digestion[]> {
  const todas = await getCollection(
    'digestiones',
    ({ data }) => data.estado === 'publicada' && !data.demo,
  );
  return todas.sort(porFecha);
}

/**
 * Todas las rutas a construir.
 *
 * En desarrollo se construye todo, para poder previsualizar una pieza en curso.
 * En producción queda fuera lo que no debería existir en el sitio público:
 * borradores y piezas de andamiaje con datos sintéticos.
 *
 * Que la pieza demo NO se construya en producción es lo que evita la
 * contradicción de emitir `noindex` en la página y a la vez listarla en el
 * sitemap — dos señales opuestas al mismo crawler.
 */
export async function digestionesConRuta(): Promise<Digestion[]> {
  const todas = await getCollection('digestiones', ({ data }) =>
    incluirEjemplos ? true : data.estado !== 'borrador' && !data.demo,
  );
  return todas.sort(porFecha);
}

/** Más reciente primero; `actualizado` no altera el orden de publicación. */
function porFecha(a: Digestion, b: Digestion): number {
  return b.data.fecha.getTime() - a.data.fecha.getTime();
}

/** La destacada de la home: la marcada, o la más reciente si no hay ninguna. */
export function destacada(digestiones: Digestion[]): Digestion | undefined {
  return digestiones.find((d) => d.data.destacada) ?? digestiones[0];
}

/** Índice de temas con su conteo, para los filtros de la Fase 3. */
export function temasConConteo(digestiones: Digestion[]): Array<{ tema: string; total: number }> {
  const conteo = new Map<string, number>();
  for (const d of digestiones) {
    for (const t of d.data.temas) conteo.set(t, (conteo.get(t) ?? 0) + 1);
  }
  return [...conteo.entries()]
    .map(([tema, total]) => ({ tema, total }))
    .sort((a, b) => b.total - a.total || a.tema.localeCompare(b.tema));
}

/**
 * Todos los datasets publicados, con la digestión que los originó.
 * Alimenta /datos/ (la Despensa).
 */
export function despensa(digestiones: Digestion[]) {
  return digestiones.flatMap((d) =>
    d.data.datasets.map((ds) => ({
      ...ds,
      digestion: { id: d.id, titulo: d.data.titulo },
      fecha: d.data.fecha,
      organismo: d.data.fuentes[0]?.organismo ?? '',
    })),
  );
}
