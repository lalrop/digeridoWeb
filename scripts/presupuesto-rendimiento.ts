/**
 * Presupuesto de rendimiento (§8). `pnpm presupuesto`
 *
 * "falla el CI si se excede". Este script es esa falla.
 *
 * Mide lo que se puede medir sobre `dist/` sin levantar un navegador: peso de JS
 * y peso de la primera vista. LCP y CLS los mide Lighthouse CI, que necesita
 * ejecución real (ver `.lighthouserc.json`).
 *
 * Se comprime con Brotli porque es lo que sirve Nginx (§9). Medir sin comprimir
 * infla los números y vuelve el presupuesto decorativo.
 */
import { existsSync, readFileSync } from 'node:fs';
import { readdir } from 'node:fs/promises';
import { join, relative, resolve } from 'node:path';
import { brotliCompressSync } from 'node:zlib';

const RAIZ = resolve(import.meta.dirname, '..');
const DIST = join(RAIZ, 'apps/web/dist');

/** Límites de §8, en KB comprimidos. */
const PRESUPUESTO = {
  /** JS del shell del artículo: lo que carga toda página. */
  jsShell: 40,
  /** JS total de una digestión, islas incluidas. */
  jsDigestion: 150,
  /** Peso total de primera vista. */
  primeraVista: 500,
} as const;

/**
 * Islas específicas de una pieza. No cuentan para el shell, pero sí para el
 * total de la digestión. El patrón se amplía cuando aparezcan otros prefijos.
 */
const ES_ISLA = /(Flujo|Grafico|Mapa|Scrolly|scrollama)[^/]*\.js$/;

const kb = (bytes: number) => bytes / 1024;
const pesoBrotli = (ruta: string) => brotliCompressSync(readFileSync(ruta)).byteLength;

async function listar(dir: string): Promise<string[]> {
  const salida: string[] = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) salida.push(...(await listar(p)));
    else salida.push(p);
  }
  return salida;
}

if (!existsSync(DIST)) {
  console.error(`No existe ${relative(RAIZ, DIST)}. Corré \`pnpm build\` primero.`);
  process.exit(1);
}

const todos = await listar(DIST);
const js = todos.filter((f) => f.endsWith('.js'));
const css = todos.filter((f) => f.endsWith('.css'));
const html = todos.filter((f) => f.endsWith('.html'));

const pesos = new Map(js.map((f) => [f, pesoBrotli(f)]));
const sumar = (archivos: string[]) => archivos.reduce((a, f) => a + (pesos.get(f) ?? 0), 0);

const pesoShell = sumar(js.filter((f) => !ES_ISLA.test(f)));
const pesoJsTotal = sumar(js);
const pesoCss = css.reduce((a, f) => a + pesoBrotli(f), 0);

/**
 * Primera vista: el HTML de digestión más pesado, más todo el CSS, más el shell
 * de JS. Es una cota superior deliberada —el CSS realmente cargado es menor—
 * porque un presupuesto que se mide optimista no protege de nada.
 */
const htmlDigestiones = html.filter((f) => f.includes(`digestiones${sep()}`));
const pesoHtmlMax = Math.max(
  0,
  ...(htmlDigestiones.length > 0 ? htmlDigestiones : html).map((f) => pesoBrotli(f)),
);

function sep(): string {
  return join('a', 'b').includes('/') ? '/' : '\\';
}

const controles = [
  { nombre: 'JS del shell', medido: kb(pesoShell), limite: PRESUPUESTO.jsShell },
  { nombre: 'JS total, islas incluidas', medido: kb(pesoJsTotal), limite: PRESUPUESTO.jsDigestion },
  {
    nombre: 'Primera vista (HTML + CSS + shell)',
    medido: kb(pesoHtmlMax + pesoCss + pesoShell),
    limite: PRESUPUESTO.primeraVista,
  },
];

console.log('\nPresupuesto de rendimiento §8 — pesos en KB, comprimidos con Brotli\n');

let excedido = false;
for (const c of controles) {
  const ok = c.medido <= c.limite;
  if (!ok) excedido = true;
  const holgura = ((1 - c.medido / c.limite) * 100).toFixed(0);
  console.log(
    `  ${(ok ? 'OK' : 'EXCEDE').padEnd(6)} ${c.nombre.padEnd(36)} ` +
      `${c.medido.toFixed(1).padStart(7)} / ${String(c.limite).padStart(3)} KB` +
      (ok ? `   holgura ${holgura} %` : '   ← revisar'),
  );
}

console.log('\n  JS emitido, por archivo:');
for (const [ruta, peso] of [...pesos.entries()].sort((a, b) => b[1] - a[1])) {
  const marca = ES_ISLA.test(ruta) ? 'isla ' : 'shell';
  console.log(`    ${marca}  ${kb(peso).toFixed(1).padStart(7)} KB  ${relative(DIST, ruta)}`);
}

console.log(`\n  CSS total: ${kb(pesoCss).toFixed(1)} KB · HTML más pesado: ${kb(pesoHtmlMax).toFixed(1)} KB`);
console.log('  LCP (< 2,0 s en 4G) y CLS (< 0,05) los mide Lighthouse CI.\n');

if (excedido) {
  console.error('Presupuesto de §8 excedido. El CI falla acá a propósito.\n');
  process.exit(1);
}
