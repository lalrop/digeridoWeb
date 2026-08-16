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
