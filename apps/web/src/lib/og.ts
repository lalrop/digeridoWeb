/**
 * Generación de imágenes OG con Satori + resvg (§8).
 *
 * "Imagen OG por digestión, generada en build, que reproduce la Etiqueta
 * Nutricional. Es lo que se ve en WhatsApp y X, y es inmediatamente
 * reconocible."
 *
 * Satori acepta un subconjunto de CSS sobre un árbol tipo JSX. Acá se construye
 * ese árbol con objetos planos (sin JSX, para no meter una transformación más en
 * el build) y se toman los colores de `@digerido/tokens`, así la tarjeta no se
 * desincroniza de la paleta del sitio.
 */
import { readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

import { Resvg } from '@resvg/resvg-js';
import { marca, superficie } from '@digerido/tokens';
import satori from 'satori';

export const ANCHO_OG = 1200;
export const ALTO_OG = 630;

/** Nodo mínimo que entiende Satori. */
interface Nodo {
  type: string;
  props: Record<string, unknown> & { children?: Nodo | Nodo[] | string };
}

const el = (
  type: string,
  style: Record<string, unknown>,
  children?: Nodo | Nodo[] | string,
): Nodo => ({ type, props: { style, ...(children !== undefined ? { children } : {}) } });

/**
 * Fuentes para Satori.
 *
 * Satori no puede maquetar sin al menos un buffer de fuente: no existe el
 * "usá la del sistema". Y las fuentes de marca son autoalojadas y NO viajan en
 * el repo (§5, ver README), así que un clon recién hecho no las tiene.
 *
 * En vez de romper el build o emitir una OG en blanco, se cae a una fuente del
 * sistema y se avisa fuerte. La tarjeta sale con la tipografía equivocada —lo
 * cual es visible de inmediato— en lugar de no salir.
 *
 * `.ttf`, no `.woff2`: Satori no descomprime WOFF2. Las fuentes de marca deben
 * dejarse en `public/fuentes/` también como TTF/OTF para el generador de OG.
 */
const FUENTES_SISTEMA = [
  '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
  '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
  '/System/Library/Fonts/Helvetica.ttc',
];

let avisoEmitido = false;

async function cargarFuentes() {
  const ruta = (archivo: string) =>
    fileURLToPath(new URL(`../../public/fuentes/${archivo}`, import.meta.url));

  const deMarca = [
    { name: 'Archivo', archivo: 'ArchivoExpanded-Bold.ttf', weight: 700 as const },
    { name: 'IBM Plex Mono', archivo: 'IBMPlexMono-Regular.ttf', weight: 400 as const },
  ];

  const fuentes: Array<{
    name: string;
    data: Buffer;
    weight: 400 | 700;
    style: 'normal';
  }> = [];

  for (const f of deMarca) {
    const p = ruta(f.archivo);
    if (existsSync(p)) {
      fuentes.push({ name: f.name, data: await readFile(p), weight: f.weight, style: 'normal' });
    }
  }

  if (fuentes.length === 2) return fuentes;

  // Fallback: la primera fuente de sistema que exista, registrada bajo los DOS
  // nombres que usa la tarjeta, para que Satori resuelva ambas familias.
  const respaldo = FUENTES_SISTEMA.find((p) => existsSync(p));
  if (!respaldo) {
    throw new Error(
      'No hay ninguna fuente disponible para generar las imágenes OG. ' +
        'Dejá las fuentes de marca en TTF en apps/web/public/fuentes/ ' +
        `(${deMarca.map((f) => f.archivo).join(', ')}) o instalá una fuente en el sistema.`,
    );
  }

  if (!avisoEmitido) {
    avisoEmitido = true;
    const faltantes = deMarca.filter((f) => !existsSync(ruta(f.archivo))).map((f) => f.archivo);
    console.warn(
      `\n[og] Faltan las fuentes de marca en public/fuentes/: ${faltantes.join(', ')}.\n` +
        `[og] Las imágenes OG se generan con ${respaldo} y NO tienen la tipografía del sitio.\n` +
        '[og] Antes de publicar, agregá las fuentes en TTF (Satori no lee WOFF2).\n',
    );
  }

  const data = await readFile(respaldo);
  const nombresUsados = new Set(deMarca.map((f) => f.name));
  return [...nombresUsados].map((name) => ({
    name,
    data,
    weight: 400 as const,
    style: 'normal' as const,
  }));
}

export interface DatosOG {
  titulo: string;
  hallazgo: string;
  organismo: string;
  filas: Array<{ etiqueta: string; valor: string }>;
  filasDigerido: Array<{ etiqueta: string; valor: string }>;
  reduccion: number;
}

/** Una fila de la etiqueta: rótulo a la izquierda, cifra a la derecha. */
const fila = (etiqueta: string, valor: string, ultima = false): Nodo =>
  el(
    'div',
    {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'baseline',
      padding: '7px 16px',
      borderBottom: ultima ? 'none' : `1px solid ${superficie.borde}`,
      fontSize: 20,
      fontFamily: 'IBM Plex Mono',
    },
    [
      el('div', { color: marca.tinta }, etiqueta),
      el('div', { color: marca.tinta, fontWeight: 600 }, valor),
    ],
  );

const rotuloSeccion = (texto: string, corte = false): Nodo =>
  el(
    'div',
    {
      padding: corte ? '12px 16px 6px' : '10px 16px 6px',
      borderTop: corte ? `6px solid ${marca.tinta}` : 'none',
      borderBottom: `1px solid ${marca.tinta}`,
      fontSize: 15,
      letterSpacing: 1.6,
      textTransform: 'uppercase',
      color: corte ? marca.tinta : marca.sello,
      fontFamily: 'IBM Plex Mono',
    },
    texto,
  );

/**
 * Construye la tarjeta: el titular y el hallazgo a la izquierda, la Etiqueta
 * Nutricional a la derecha. La etiqueta es lo reconocible del sitio, así que
 * ocupa un tercio fijo del ancho y nunca se comprime.
 */
function tarjeta(d: DatosOG): Nodo {
  return el(
    'div',
    {
      width: ANCHO_OG,
      height: ALTO_OG,
      display: 'flex',
      backgroundColor: marca.papel,
      fontFamily: 'Archivo',
    },
    [
      // ── Columna izquierda ───────────────────────────────────────────────
      el(
        'div',
        {
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          width: 720,
          padding: '52px 44px',
        },
        [
          el('div', { display: 'flex', flexDirection: 'column' }, [
            el(
              'div',
              {
                fontSize: 17,
                letterSpacing: 2.4,
                textTransform: 'uppercase',
                color: marca.sello,
                fontFamily: 'IBM Plex Mono',
                marginBottom: 26,
              },
              `digerido · ${d.organismo}`,
            ),
            el(
              'div',
              {
                fontSize: 52,
                lineHeight: 1.08,
                fontWeight: 700,
                color: marca.tinta,
                letterSpacing: -1,
              },
              d.titulo,
            ),
          ]),

          // El hallazgo con el filete naranja: el mismo tratamiento que en la
          // portada del artículo, para que la tarjeta y la pieza se reconozcan.
          el(
            'div',
            {
              display: 'flex',
              borderLeft: `5px solid ${marca.bilis}`,
              paddingLeft: 18,
              fontSize: 25,
              lineHeight: 1.35,
              color: marca.tinta,
            },
            d.hallazgo,
          ),
        ],
      ),

      // ── Columna derecha: la Etiqueta Nutricional ────────────────────────
      el(
        'div',
        {
          display: 'flex',
          alignItems: 'center',
          width: 480,
          padding: '44px 44px 44px 0',
        },
        [
          el(
            'div',
            {
              display: 'flex',
              flexDirection: 'column',
              width: '100%',
              backgroundColor: superficie.papelAlto,
              border: `3px solid ${marca.tinta}`,
            },
            [
              el(
                'div',
                {
                  padding: '10px 16px',
                  backgroundColor: marca.tinta,
                  color: marca.papel,
                  fontSize: 15,
                  fontWeight: 700,
                  letterSpacing: 1.6,
                  textTransform: 'uppercase',
                  fontFamily: 'IBM Plex Mono',
                },
                'Información nutricional',
              ),

              rotuloSeccion('Antes de digerir'),
              ...d.filas.map((f, i) => fila(f.etiqueta, f.valor, i === d.filas.length - 1)),

              rotuloSeccion('Después de digerir', true),
              ...d.filasDigerido.map((f, i) =>
                fila(f.etiqueta, f.valor, i === d.filasDigerido.length - 1),
              ),

              el(
                'div',
                {
                  display: 'flex',
                  alignItems: 'baseline',
                  justifyContent: 'center',
                  gap: 10,
                  padding: '14px 16px',
                  borderTop: `3px solid ${marca.tinta}`,
                  backgroundColor: superficie.papelBajo,
                  fontFamily: 'IBM Plex Mono',
                },
                [
                  el(
                    'div',
                    { fontSize: 34, fontWeight: 700, color: marca.bilis },
                    `${d.reduccion} %`,
                  ),
                  el('div', { fontSize: 18, color: marca.tinta }, 'menos tiempo'),
                ],
              ),
            ],
          ),
        ],
      ),
    ],
  );
}

/** Renderiza la tarjeta a PNG. */
export async function generarOG(d: DatosOG): Promise<Uint8Array> {
  const fonts = await cargarFuentes();

  const svg = await satori(tarjeta(d) as never, {
    width: ANCHO_OG,
    height: ALTO_OG,
    fonts,
  });

  const png = new Resvg(svg, {
    fitTo: { mode: 'width', value: ANCHO_OG },
    font: { loadSystemFonts: true },
  })
    .render()
    .asPng();

  return new Uint8Array(png);
}
