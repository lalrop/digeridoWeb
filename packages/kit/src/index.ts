/**
 * @digerido/kit — design system y primitivas de visualización.
 *
 * Regla de §13: "Todo lo que se use dos veces sube a packages/kit."
 *
 * Los componentes Svelte se importan por ruta profunda para que Astro pueda
 * decidir la hidratación isla por isla:
 *
 *   import Figura from '@digerido/kit/charts/Figura.svelte';
 *   import Scrolly from '@digerido/kit/scroll/Scrolly.svelte';
 *
 * Este índice expone solo lo que no es componente: utilidades puras, testeables
 * y usables tanto en build (Astro, generador de OG) como en el cliente.
 */
export * from './utils/index.js';

export { color, marca, superficie, escala, espacio, familia } from '@digerido/tokens';
