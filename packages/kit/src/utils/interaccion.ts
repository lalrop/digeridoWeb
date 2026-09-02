/**
 * `enVista` — acción de Svelte para el "momento de deleite" que cada
 * digestión necesita (feedback del usuario, 2026-08-16): revela un gráfico o
 * una cifra con una animación de entrada la primera vez que aparece en el
 * viewport, en vez de estar ahí de entrada sin más.
 *
 * Progresivo por diseño, no al revés: el elemento SIEMPRE tiene que renderizar
 * su valor final correcto sin JS (§ "sin JavaScript, el texto y los gráficos
 * siguen ahí"). Por eso el estado por defecto que maneja quien usa esta
 * acción tiene que ser "revelado" — la acción solo pide, con JS activo,
 * ocultarlo brevemente ANTES de revelarlo nunca al revés. Y solo lo hace si
 * el elemento todavía no está a la vista al cargar la página: si ya está
 * visible, no hay nada que "revelar" y forzar un parpadeo (visible → oculto
 * → visible) sería peor que no animar.
 *
 * También respeta `prefers-reduced-motion`: ahí la acción no hace nada, el
 * estado por defecto (revelado) queda como estaba.
 */
export function enVista(
  nodo: Element,
  alCambiar: (estado: 'oculto' | 'revelado') => void,
): { destroy(): void } | void {
  if (
    typeof IntersectionObserver === 'undefined' ||
    typeof matchMedia !== 'function' ||
    matchMedia('(prefers-reduced-motion: reduce)').matches
  ) {
    return;
  }

  const rect = nodo.getBoundingClientRect();
  const yaEnPantalla = rect.top < (window.innerHeight ?? 0) && rect.bottom > 0;
  if (yaEnPantalla) return;

  alCambiar('oculto');

  const observador = new IntersectionObserver(
    (entradas) => {
      for (const entrada of entradas) {
        if (entrada.isIntersecting) {
          alCambiar('revelado');
          observador.disconnect();
        }
      }
    },
    { threshold: 0.35 },
  );
  observador.observe(nodo);

  return { destroy: () => observador.disconnect() };
}

/**
 * `observarAncho` — acción de Svelte que reporta el ancho real en px de un
 * elemento y lo mantiene al día si el layout cambia (girar el celular,
 * redimensionar la ventana).
 *
 * Vive en este mismo archivo que `enVista` (no en un módulo aparte) a
 * propósito: las dos son acciones de una sola línea que casi todo gráfico del
 * kit importa juntas, y mantenerlas separadas solo multiplicaba los límites
 * de chunk que Rollup tenía que negociar sin ahorrar una sola línea de código
 * real — ver §8, el presupuesto de rendimiento.
 *
 * Existe para un problema concreto: todo gráfico del kit dibuja su SVG con un
 * `viewBox` fijo (típicamente 720 de ancho) y lo escala con `width: 100%`
 * del contenedor. Eso significa que CUALQUIER `<text>` dentro del SVG —marcas
 * de eje, anotaciones, etiquetas de valor— se encoge en la misma proporción
 * que el dibujo: en un celular angosto, un texto nominal de 12px puede
 * terminar renderizado a ~5px, ilegible (medido: 375px de viewport → ~327px
 * de carril real → factor 0.45 → 12px pasan a ser ~5,5px reales).
 *
 * La solución vive en `Eje.svelte` y `Anotacion.svelte`: reciben un `factor`
 * de compensación (`ANCHO_VIEWBOX / anchoReal`) y envuelven su texto en una
 * transformación inversa que lo devuelve a su tamaño real en pantalla, sin
 * cambiar la posición del punto que anota. Esta acción es la que le da a cada
 * gráfico ese `anchoReal`, medido en vivo — no una sola vez al montar
 * (`clientWidth` leído una vez queda obsoleto en cuanto la ventana cambia de
 * tamaño), sino actualizado mientras la página vive.
 *
 * Progresiva: sin `ResizeObserver` (navegador muy antiguo), reporta el ancho
 * una sola vez al montar y no lo vuelve a actualizar — nunca deja el valor sin
 * definir, y el peor caso es un factor de compensación que queda fijo en vez
 * de reaccionar a un resize, no un gráfico roto.
 */
export function observarAncho(
  nodo: HTMLElement,
  alCambiar: (ancho: number) => void,
): { destroy(): void } | void {
  alCambiar(nodo.clientWidth);

  if (typeof ResizeObserver === 'undefined') return;

  const observador = new ResizeObserver((entradas) => {
    const entrada = entradas[0];
    if (entrada) alCambiar(entrada.contentRect.width);
  });
  observador.observe(nodo);

  return { destroy: () => observador.disconnect() };
}
