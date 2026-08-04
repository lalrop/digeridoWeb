/**
 * Emite `dist/tokens.css` desde los módulos TS.
 *
 * Una sola fuente de verdad (§3): si un color existe en CSS pero no en TS, el
 * generador de OG images y los gráficos que necesitan el valor en JS quedan
 * desincronizados. Este script hace imposible ese estado.
 *
 * Se ejecuta antes del build de Astro (`pnpm build` en la raíz).
 */
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { grafico, marca, superficie } from './color.js';
import { curva, duracion, espacio, quiebre, radio, sombra } from './espacio.js';
import { escala, familia, interlinea, medida, peso, tracking } from './tipografia.js';

const aquí = dirname(fileURLToPath(import.meta.url));
const salida = resolve(aquí, '../dist/tokens.css');

/** camelCase → kebab-case, para `--espacio-2xl` y `--tipo-3xl`. */
const kebab = (s: string) => s.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();

const decl = (prefijo: string, obj: Record<string, string | number>): string =>
  Object.entries(obj)
    .map(([k, v]) => `  --${prefijo}-${kebab(k)}: ${v};`)
    .join('\n');

const lista = (prefijo: string, valores: readonly string[]): string =>
  valores.map((v, i) => `  --${prefijo}-${i + 1}: ${v};`).join('\n');

const css = `/* ═══════════════════════════════════════════════════════════════════
 * GENERADO por packages/tokens/src/build.ts — NO EDITAR A MANO.
 * Editar los módulos en packages/tokens/src/ y correr \`pnpm -F @digerido/tokens build\`.
 * ═══════════════════════════════════════════════════════════════════ */

@layer tokens {
  :root {
    /* ── Marca ──────────────────────────────────────────────────────── */
${decl('color', marca)}

    /* ── Superficies derivadas ──────────────────────────────────────── */
${decl('color', superficie)}

    /* ── Escalas de gráfico (sistema aparte de la marca) ────────────── */
${lista('viz-cat', grafico.categorica)}
${lista('viz-seq', grafico.secuencial)}
${lista('viz-div', grafico.divergente)}
    --viz-sin-dato: ${grafico.sinDato};
    --viz-destacado: ${grafico.destacado};
    --viz-contexto: ${grafico.contexto};

    /* ── Tipografía ─────────────────────────────────────────────────── */
${decl('fuente', familia)}
${decl('peso', peso)}
${decl('tipo', escala)}
${decl('interlinea', interlinea)}
${decl('tracking', tracking)}
${decl('medida', medida)}

    /* ── Espacio, forma, movimiento ─────────────────────────────────── */
${decl('espacio', espacio)}
${decl('radio', radio)}
${decl('sombra', sombra)}
${decl('quiebre', quiebre)}
${decl('duracion', duracion)}
${decl('curva', curva)}
  }

  /* Con movimiento reducido, las duraciones no se ponen en 0: se acortan al
   * mínimo perceptible. Un cambio de estado instantáneo también desorienta. */
  @media (prefers-reduced-motion: reduce) {
    :root {
      --duracion-rapida: 1ms;
      --duracion-media: 1ms;
      --duracion-lenta: 1ms;
    }
  }
}
`;

await mkdir(dirname(salida), { recursive: true });
await writeFile(salida, css, 'utf8');
console.log(`tokens → ${salida} (${(css.length / 1024).toFixed(1)} KB)`);
