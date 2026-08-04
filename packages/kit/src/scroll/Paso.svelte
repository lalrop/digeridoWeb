<!--
  Paso.svelte — un paso de una secuencia de scrollytelling.

  Lee el paso activo del contexto que pone `Scrolly`, así el autor de la
  digestión escribe los pasos en orden sin numerarlos a mano.

  §6.1: "El texto anota, no explica lo obvio." El estilo empuja en esa
  dirección: la caja es angosta y el texto chico. Si un paso no cabe, es un
  párrafo del artículo, no un paso.
-->
<script lang="ts">
  import { getContext, type Snippet } from 'svelte';

  interface Props {
    /** Índice del paso, empezando en 0. Debe coincidir con el orden en el DOM. */
    indice: number;
    children: Snippet;
  }

  let { indice, children }: Props = $props();

  const ctx = getContext<{ activo: number } | undefined>('scrolly');
  const activo = $derived(ctx?.activo === indice);
</script>

<div class="paso" class:activo aria-current={activo ? 'step' : undefined}>
  <p class="folio">{String(indice + 1).padStart(2, '0')}</p>
  <div class="cuerpo">
    {@render children()}
  </div>
</div>

<style>
  .paso {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: var(--espacio-sm);
    max-width: 34rem;
    /* Los pasos inactivos se atenúan, no se ocultan: el lector puede volver
       atrás con la vista sin scrollear. */
    opacity: 0.45;
    transition: opacity var(--duracion-media) var(--curva-salida);
  }

  .paso.activo {
    opacity: 1;
  }

  /* El folio monoespaciado: el sitio numera como un oficio numera (§5). */
  .folio {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-3xs);
    color: var(--color-sello);
    letter-spacing: var(--tracking-versalita);
    margin: 0;
    padding-block-start: 0.35em;
    font-variant-numeric: tabular-nums;
  }

  .paso.activo .folio {
    color: var(--color-tinta);
  }

  .cuerpo {
    font-family: var(--fuente-cuerpo);
    font-size: var(--tipo-sm);
    line-height: var(--interlinea-cuerpo);
    color: var(--color-tinta);
    border-inline-start: 2px solid transparent;
    padding-inline-start: var(--espacio-md);
    transition: border-color var(--duracion-media) var(--curva-salida);
  }

  /* La barra `enzima` marca el paso activo: uso quirúrgico del verde ácido,
     exactamente el elemento que el scroll del lector controla (§5). */
  .paso.activo .cuerpo {
    border-inline-start-color: var(--color-enzima);
  }

  .cuerpo :global(p) {
    margin: 0;
  }

  .cuerpo :global(p + p) {
    margin-block-start: var(--espacio-sm);
  }

  .cuerpo :global(strong) {
    font-weight: var(--peso-semi);
  }

  /* Con movimiento reducido no hay paso activo: todos se leen por igual. */
  @media (prefers-reduced-motion: reduce) {
    .paso {
      opacity: 1;
      transition: none;
    }

    .cuerpo {
      transition: none;
      border-inline-start-color: var(--color-borde);
    }
  }
</style>
