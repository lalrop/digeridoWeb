/**
 * Esquemas de contenido (§4).
 *
 * "Esto convierte el frontmatter en un contrato: sin fuente verificable y sin
 * `hallazgo`, el build falla. La credibilidad se impone por tipos, no por
 * buenas intenciones."
 *
 * Nota de versión: el plan ubica esto en `src/content/config.ts` con
 * `type: 'content'`. Astro 5 reemplazó ese API por el Content Layer —
 * `src/content.config.ts` y un `loader`— y Astro 7 (la versión en uso) ya no
 * acepta el anterior. La estructura de carpetas y los esquemas son los del
 * plan; solo cambia cómo se cargan.
 */
import { glob } from 'astro/loaders';
import { defineCollection, z } from 'astro:content';

/** Temas del portal. Cerrado a propósito: un tema nuevo es una decisión editorial. */
const TEMAS = [
  'presupuesto', 'economia', 'salud', 'educacion',
  'medioambiente', 'legislativo', 'compras-publicas', 'territorio',
] as const;

/**
 * El documento original digerido.
 *
 * `sha256` es trazabilidad, no adorno: un organismo puede reemplazar un PDF sin
 * aviso, y el job semanal de §13 compara contra este valor para avisar.
 */
const fuente = z.object({
  titulo: z.string().min(1),
  organismo: z.string().min(1), // "DIPRES", "Banco Central", "INE"
  url: z.string().url(),
  fechaPublicacion: z.coerce.date(),
  fechaDescarga: z.coerce.date(),
  // 64 hex: un placeholder tipo "pendiente" no pasa, que es el punto.
  sha256: z
    .string()
    .regex(/^[a-f0-9]{64}$/, 'sha256 debe ser 64 caracteres hexadecimales en minúscula'),
  paginas: z.number().int().positive().optional(),
  formato: z.enum(['pdf', 'xlsx', 'csv', 'api', 'html']),
}).superRefine((f, ctx) => {
  // No se puede descargar un documento antes de que exista. Casi siempre
  // significa que alguien copió una fecha del documento anterior.
  if (f.fechaDescarga < f.fechaPublicacion) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ['fechaDescarga'],
      message: `fechaDescarga (${f.fechaDescarga.toISOString().slice(0, 10)}) es anterior a fechaPublicacion (${f.fechaPublicacion.toISOString().slice(0, 10)})`,
    });
  }
});

const dataset = z.object({
  nombre: z.string().min(1),
  /** Ruta relativa dentro de public/data/. La produce el pipeline. */
  archivo: z.string().min(1),
  licencia: z.string().default('CC BY 4.0'),
  descripcion: z.string().optional(),
  filas: z.number().int().nonnegative().optional(),
  bytes: z.number().int().nonnegative().optional(),
});

const digestiones = defineCollection({
  loader: glob({
    base: './src/content/digestiones',
    pattern: '**/index.{md,mdx}',
    // El id es la carpeta: "presupuesto-2027/index" → "presupuesto-2027".
    generateId: ({ entry }) => entry.replace(/\/index\.mdx?$/, ''),
  }),

  schema: z
    .object({
      titulo: z.string().min(1),
      bajada: z.string().max(220),

      /**
       * La frase única. "Si una digestión no puede resumirse en una frase que
       * le importe a alguien, no se publica" (§2).
       *
       * El máximo de 180 no es cosmético: obliga a que sea UNA frase. Un
       * hallazgo de tres oraciones es un resumen, y un resumen no es un ángulo.
       */
      hallazgo: z.string().min(20).max(180),

      fecha: z.coerce.date(),
      actualizado: z.coerce.date().optional(),
      autores: z.array(z.string()).default(['digerido']),
      temas: z.array(z.enum(TEMAS)).min(1),

      /** Alimenta la etiqueta nutricional. 1 = legible, 5 = ilegible. */
      dificultadOriginal: z.number().int().min(1).max(5),

      /** Minutos. La comparación es el argumento del sitio. */
      tiempoLectura: z.object({
        original: z.number().positive(),
        digerido: z.number().positive(),
      }),

      /** Métricas medidas por el pipeline para la Etiqueta Nutricional (§5). */
      etiqueta: z
        .object({
          palabrasOriginal: z.number().int().positive(),
          siglasSinDefinir: z.number().int().nonnegative().optional(),
          legibilidadOriginal: z.number().min(0).max(100),
          legibilidadDigerido: z.number().min(0).max(100),
          graficos: z.number().int().nonnegative(),
        })
        .optional(),

      fuentes: z.array(fuente).min(1),
      datasets: z.array(dataset).default([]),

      destacada: z.boolean().default(false),
      estado: z.enum(['borrador', 'publicada', 'archivada']).default('borrador'),

      /**
       * Pieza de andamiaje con datos sintéticos. Renderiza un aviso visible y
       * queda fuera de RSS y del índice público.
       *
       * No está en el plan; lo agrego porque el esqueleto necesita una pieza de
       * ejemplo y nada en el sitio debe poder confundirse con una digestión
       * real de un documento real.
       */
      demo: z.boolean().default(false),

      /** Limitaciones y errores conocidos (§10, último ítem del checklist). */
      limitaciones: z.array(z.string()).default([]),

      /** Log de correcciones público con fecha (§13). */
      correcciones: z
        .array(z.object({ fecha: z.coerce.date(), descripcion: z.string().min(1) }))
        .default([]),
    })
    .superRefine((d, ctx) => {
      if (d.actualizado && d.actualizado < d.fecha) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ['actualizado'],
          message: 'actualizado no puede ser anterior a fecha',
        });
      }

      // La premisa del sitio: digerir reduce el tiempo de lectura. Si no lo
      // reduce, o los números están mal o la pieza no digirió nada.
      if (d.tiempoLectura.digerido >= d.tiempoLectura.original) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ['tiempoLectura'],
          message: `el tiempo digerido (${d.tiempoLectura.digerido} min) no es menor al original (${d.tiempoLectura.original} min)`,
        });
      }

      if (d.etiqueta && d.etiqueta.legibilidadDigerido <= d.etiqueta.legibilidadOriginal) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ['etiqueta', 'legibilidadDigerido'],
          message: 'el texto digerido debería ser más legible que el original',
        });
      }

      // El hallazgo es una frase, no un párrafo.
      if ((d.hallazgo.match(/[.!?](\s|$)/g) ?? []).length > 1) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ['hallazgo'],
          message: 'el hallazgo debe ser UNA frase (§2). Encontré más de un punto final.',
        });
      }

      // Reglas que solo aplican a lo que sale a producción. Un borrador puede
      // estar incompleto; una pieza publicada, no.
      if (d.estado === 'publicada') {
        if (!d.etiqueta) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: ['etiqueta'],
            message: 'una digestión publicada necesita las métricas de la Etiqueta Nutricional',
          });
        }
        if (d.demo) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: ['demo'],
            message: 'una pieza con datos sintéticos no puede quedar en estado "publicada"',
          });
        }
        // §10: "Errores conocidos y limitaciones declarados al final."
        if (d.limitaciones.length === 0) {
          ctx.addIssue({
            code: z.ZodIssueCode.custom,
            path: ['limitaciones'],
            message:
              'el checklist de §10 exige declarar limitaciones antes de publicar. ' +
              'Si de verdad no hay ninguna, decilo explícitamente en una entrada.',
          });
        }
      }
    }),
});

/**
 * Registro global de fuentes que alimenta /metodo/ (§7).
 *
 * Separado de las digestiones porque una fuente se digiere más de una vez (la
 * ejecución presupuestaria es trimestral) y su historial de hashes es del
 * documento, no del artículo.
 */
const fuentesGlobales = defineCollection({
  loader: glob({ base: './src/content/fuentes', pattern: '**/*.json' }),
  schema: z.object({
    organismo: z.string(),
    titulo: z.string(),
    url: z.string().url(),
    formato: z.enum(['pdf', 'xlsx', 'csv', 'api', 'html']),
    /** Cadena de custodia: cada descarga con su hash y fecha. */
    revisiones: z
      .array(
        z.object({
          fechaDescarga: z.coerce.date(),
          sha256: z.string().regex(/^[a-f0-9]{64}$/),
          cambio: z.string().optional(),
        }),
      )
      .min(1),
  }),
});

export const collections = { digestiones, fuentes: fuentesGlobales };
export { TEMAS };
