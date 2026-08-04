/**
 * Una imagen OG por digestión, generada en build (§8).
 *
 * Reproduce la Etiqueta Nutricional: es lo que se ve en WhatsApp y X, y lo que
 * hace la tarjeta reconocible sin leer el título.
 */
import type { APIRoute } from 'astro';

import { duracion, numero } from '@digerido/kit/utils';

import { digestionesConRuta } from '../../lib/digestiones';
import { generarOG, type DatosOG } from '../../lib/og';

export async function getStaticPaths() {
  const digestiones = await digestionesConRuta();

  return digestiones.map((d) => {
    const e = d.data.etiqueta;

    const datos: DatosOG = {
      titulo: d.data.titulo,
      hallazgo: d.data.hallazgo,
      organismo: d.data.fuentes[0]?.organismo ?? 'fuente pública',
      filas: [
        ...(d.data.fuentes[0]?.paginas !== undefined
          ? [{ etiqueta: 'Páginas', valor: numero(d.data.fuentes[0].paginas) }]
          : []),
        ...(e ? [{ etiqueta: 'Palabras', valor: numero(e.palabrasOriginal) }] : []),
        ...(e?.siglasSinDefinir !== undefined
          ? [{ etiqueta: 'Siglas sin definir', valor: numero(e.siglasSinDefinir) }]
          : []),
        ...(e ? [{ etiqueta: 'Legibilidad', valor: `${e.legibilidadOriginal} / 100` }] : []),
        { etiqueta: 'Lectura', valor: duracion(d.data.tiempoLectura.original) },
      ],
      filasDigerido: [
        { etiqueta: 'Lectura', valor: duracion(d.data.tiempoLectura.digerido) },
        ...(e ? [{ etiqueta: 'Gráficos', valor: numero(e.graficos) }] : []),
        ...(e ? [{ etiqueta: 'Legibilidad', valor: `${e.legibilidadDigerido} / 100` }] : []),
      ],
      reduccion: Math.round(
        (1 - d.data.tiempoLectura.digerido / d.data.tiempoLectura.original) * 100,
      ),
    };

    return { params: { slug: d.id }, props: { datos } };
  });
}

export const GET: APIRoute = async ({ props }) => {
  const png = await generarOG(props.datos as DatosOG);

  return new Response(png as unknown as BodyInit, {
    headers: {
      'Content-Type': 'image/png',
      // Generada en build y con nombre estable: la purga la hace el deploy (§9).
      'Cache-Control': 'public, max-age=3600',
    },
  });
};
