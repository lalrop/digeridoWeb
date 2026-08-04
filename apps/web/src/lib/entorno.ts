/**
 * Qué contenido entra al build.
 *
 * Una sola definición, usada por el loader de la colección y por las consultas.
 * Si estuviera duplicada, el loader podría incluir una pieza que las consultas
 * excluyen —o al revés— y el resultado es JS muerto en el bundle o un enlace
 * roto.
 *
 * ─── Por qué una variable y no `import.meta.env.PROD` ───────────────────────
 * `astro build` fija `PROD = true` siempre, incluso con `--mode development`:
 * el modo elige qué archivos `.env` se cargan, no la bandera. Así que "¿es un
 * build de producción?" no distingue lo que hace falta distinguir acá.
 *
 * `DIGERIDO_EJEMPLOS=1` es explícito y funciona igual en el servidor de
 * desarrollo y en un build:
 *
 *   DIGERIDO_EJEMPLOS=1 pnpm -F @digerido/web build   # incluye el andamiaje
 *   pnpm -F @digerido/web build                       # sitio público
 */

/** El servidor de desarrollo siempre muestra todo. */
const enDesarrollo = import.meta.env.DEV;

/** Un build puede pedir el andamiaje explícitamente. */
const pedidoPorEntorno =
  typeof process !== 'undefined' && process.env?.DIGERIDO_EJEMPLOS === '1';

/**
 * ¿Se incluyen las piezas de andamiaje (carpetas `ejemplo-*`) y los borradores?
 *
 * Útil para medir el presupuesto de rendimiento con una isla hidratada antes de
 * que exista la primera digestión real (§8).
 */
export const incluirEjemplos = enDesarrollo || pedidoPorEntorno;
