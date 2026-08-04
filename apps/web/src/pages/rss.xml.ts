/**
 * RSS (§8). Usa `digestionesDifundibles`: solo publicadas, nunca borradores ni
 * piezas de andamiaje. El feed es lo que se distribuye, y una vez que sale no
 * se puede retirar de los lectores.
 */
import rss from '@astrojs/rss';
import type { APIRoute } from 'astro';

import { digestionesDifundibles } from '../lib/digestiones';

export const GET: APIRoute = async (contexto) => {
  const digestiones = await digestionesDifundibles();

  return rss({
    title: 'digerido',
    description:
      'Documentos públicos ilegibles, convertidos en historias visuales navegables.',
    site: contexto.site ?? 'https://digerido.cl',
    // Español de Chile: los lectores de feeds lo usan para hyphenation.
    customData: '<language>es-cl</language>',
    items: digestiones.map((d) => ({
      title: d.data.titulo,
      link: `/digestiones/${d.id}/`,
      pubDate: d.data.fecha,
      // El hallazgo va en la descripción, no la bajada: en un lector de feeds
      // es lo único que se ve, y es la frase que decide si vale abrirla.
      description: d.data.hallazgo,
      categories: d.data.temas,
      author: d.data.autores.join(', '),
    })),
  });
};
