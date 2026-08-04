<!--
  Tooltip.svelte — capa de detalle al pasar el cursor o enfocar con teclado.

  Dos reglas que la mayoría de los tooltips rompe:

  1. Accesible por teclado (§8). Se muestra con `focus`, no solo con `mouse`.
     Un tooltip que solo responde al mouse esconde datos a quien navega con
     Tab, y en móvil no existe.
  2. Nunca tapa el dato que explica. Se voltea contra los bordes del contenedor
     y se corre del cursor.

  Vive en coordenadas del CONTENEDOR (div posicionado), no del SVG: así el
  texto usa tipografía normal, se envuelve y no hereda transformaciones.
-->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    /** Visible o no. El dueño del gráfico controla el estado. */
    visible?: boolean;
    /** Posición en px relativa al contenedor del gráfico. */
    x?: number;
    y?: number;
    /** Tamaño del contenedor, para decidir el volteo. */
    anchoContenedor?: number;
    altoContenedor?: number;
    /** Contenido. Cifras en tabular-nums por herencia. */
    children?: Snippet;
  }

  let {
    visible = false, x = 0, y = 0,
    anchoContenedor = 0, altoContenedor = 0, children,
  }: Props = $props();

  /** Estimación del tamaño para el volteo. Ancho fijo, alto acotado. */
  const ANCHO = 200;
  const ALTO_APROX = 76;
  const SEPARACION = 14;

  /** Voltea a la izquierda si no cabe a la derecha. */
  const izquierda = $derived(
    anchoContenedor > 0 && x + SEPARACION + ANCHO > anchoContenedor
      ? Math.max(0, x - SEPARACION - ANCHO)
      : x + SEPARACION,
  );

  /** Sube si no cabe abajo; nunca se sale por arriba. */
  const arriba = $derived(
    altoContenedor > 0 && y + ALTO_APROX > altoContenedor
      ? Math.max(0, y - ALTO_APROX)
      : y,
  );
</script>

<!--
  `aria-live="polite"` en vez de `role="tooltip"`: el contenido cambia al
  recorrer las marcas, y un lector de pantalla debe anunciar el valor nuevo.
  `pointer-events: none` evita que el tooltip se robe el hover de la marca.
-->
<div
  class="tooltip"
  class:visible
  style:left="{izquierda}px"
  style:top="{arriba}px"
  style:width="{ANCHO}px"
  aria-live="polite"
  aria-atomic="true">
  {#if visible}{@render children?.()}{/if}
</div>

<style>
  .tooltip {
    position: absolute;
    z-index: var(--capa-tooltip);
    pointer-events: none;
    padding: var(--espacio-xs) var(--espacio-sm);
    background: var(--color-papel-alto);
    border: 1px solid var(--color-tinta);
    /* Sombra de fotocopia: desplazada y dura, sin difusión (§5). */
    box-shadow: var(--sombra-folio);
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-2xs);
    line-height: 1.45;
    color: var(--color-tinta);
    font-variant-numeric: tabular-nums;
    opacity: 0;
    transition: opacity var(--duracion-rapida) var(--curva-salida);
  }

  .tooltip.visible {
    opacity: 1;
  }

  /* El tooltip no se mueve suavemente entre marcas: seguir una caja animada
     mientras se lee un número es peor que un salto instantáneo. */
  @media (prefers-reduced-motion: reduce) {
    .tooltip {
      transition: none;
    }
  }
</style>
