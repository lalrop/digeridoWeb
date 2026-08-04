/**
 * Tarjeta OG por defecto del sitio (home, /datos/, /metodo/).
 *
 * Usa la misma Etiqueta Nutricional, pero declarando la tesis del portal en vez
 * de las métricas de una pieza: lo que se comparte cuando se comparte el sitio.
 */
import type { APIRoute } from 'astro';

import { generarOG } from '../../lib/og';

export const GET: APIRoute = async () => {
  const png = await generarOG({
    titulo: 'Chile publica todo. Nadie puede leerlo.',
    hallazgo:
      'El problema del dato público en Chile no es la disponibilidad: es la digestibilidad.',
    organismo: 'documentos públicos',
    filas: [
      { etiqueta: 'Formato habitual', valor: 'PDF' },
      { etiqueta: 'Diccionario de datos', valor: 'ninguno' },
      { etiqueta: 'Legibilidad típica', valor: '22 / 100' },
      { etiqueta: 'Lectura', valor: 'horas' },
    ],
    filasDigerido: [
      { etiqueta: 'Lectura', valor: 'minutos' },
      { etiqueta: 'Gráfico principal', valor: '1' },
      { etiqueta: 'Fuente y hash', valor: 'sí' },
    ],
    reduccion: 97,
  });

  return new Response(png as unknown as BodyInit, {
    headers: { 'Content-Type': 'image/png', 'Cache-Control': 'public, max-age=3600' },
  });
};
