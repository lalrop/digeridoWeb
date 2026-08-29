/**
 * `observarAncho` — acción de Svelte que reporta el ancho real en px de un
 * elemento y lo mantiene al día si el layout cambia (girar el celular,
 * redimensionar la ventana).
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
