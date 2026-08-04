<!--
  Scrolly.svelte — scrollytelling compartido (§6).

  Un componente, no una reimplementación por artículo. Las cuatro reglas de uso
  del plan están implementadas acá, no anotadas en un README:

  1. El gráfico sticky debe ser legible SIN el texto → el gráfico recibe
     `activo`, pero nunca se le oculta información; el texto solo anota.
  2. Máximo 6 pasos → se avisa en desarrollo si se pasa (regla editorial).
  3. En móvil (<720 px) el gráfico ocupa el 55% superior, no el 100%.
  4. Con `prefers-reduced-motion`, degrada a gráficos estáticos apilados,
     NO a una pantalla en blanco.

  La degradación es también la ruta sin JS: el marcado renderizado en build ya
  muestra todos los pasos. Si scrollama nunca se hidrata, el lector igual lee la
  pieza completa.
-->
<script lang="ts">
  import { onMount, setContext, type Snippet } from 'svelte';

  interface Props {
    /** Snippet del gráfico sticky. Recibe el paso activo y su progreso 0–1. */
    grafico: Snippet<[number, number]>;
    /** Snippet con los `<Paso>`. */
    pasos: Snippet;
    /** Cuántos pasos contiene. Necesario para acotar `activo`. */
    total: number;
    /** Punto de disparo, fracción de la altura de viewport. */
    offset?: number;
    /**
     * Fallback estático: un snippet por paso, apilado. Si no se entrega, con
     * movimiento reducido se muestra el gráfico una vez arriba de los pasos.
     */
    estaticos?: Snippet<[number]>;
  }

  let { grafico, pasos, total, offset = 0.6, estaticos }: Props = $props();

  let activo = $state(0);
  let progreso = $state(0);
  /** Arranca en modo degradado y solo lo abandona si scrollama se hidrata. */
  let interactivo = $state(false);

  // Los `<Paso>` leen esto para marcarse como actual sin recibir props.
  setContext('scrolly', {
    get activo() {
      return activo;
    },
  });

  // Regla editorial de §6.2, avisada en desarrollo. En `$effect` para leer el
  // valor actual de `total`, no el inicial.
  $effect(() => {
    if (import.meta.env.DEV && total > 6) {
      console.warn(
        `[kit] Scrolly con ${total} pasos. §6.2 fija el máximo en 6: ` +
          'más que eso y el lector abandona. Partí la secuencia en dos.',
      );
    }
  });

  let raiz: HTMLElement;

  onMount(() => {
    const consulta = matchMedia('(prefers-reduced-motion: reduce)');

    let instancia: { destroy: () => void; resize: () => void } | null = null;

    async function activar() {
      if (consulta.matches || instancia) return;
      // Carga diferida: con movimiento reducido, scrollama nunca se descarga.
      const { default: scrollama } = await import('scrollama');
      const s = scrollama();
      // `offset` va tipado como literal decimal en scrollama; el cast mantiene
      // la prop como `number` para quien usa el componente.
      s.setup({ step: `#${raiz.id} .paso`, offset, progress: true } as Parameters<
        typeof s.setup
      >[0])
        .onStepEnter(({ index }: { index: number }) => {
          activo = Math.min(index, total - 1);
        })
        .onStepProgress(({ progress }: { progress: number }) => {
          progreso = progress;
        });
      instancia = s as unknown as { destroy: () => void; resize: () => void };
      interactivo = true;
    }

    function desactivar() {
      instancia?.destroy();
      instancia = null;
      interactivo = false;
      activo = 0;
      progreso = 0;
    }

    void activar();

    // El lector puede cambiar la preferencia del sistema con la página abierta.
    const alCambiar = () => (consulta.matches ? desactivar() : void activar());
    consulta.addEventListener('change', alCambiar);

    const alRedimensionar = () => instancia?.resize();
    window.addEventListener('resize', alRedimensionar);

    return () => {
      consulta.removeEventListener('change', alCambiar);
      window.removeEventListener('resize', alRedimensionar);
      desactivar();
    };
  });

  /** `id` único: scrollama necesita un selector, y puede haber dos por página. */
  const id = `scrolly-${Math.random().toString(36).slice(2, 9)}`;
</script>

<section class="scrolly" class:interactivo bind:this={raiz} {id}>
  {#if interactivo}
    <!-- Modo interactivo: un gráfico pegado, los pasos lo anotan al pasar. -->
    <figure class="sticky">
      {@render grafico(activo, progreso)}
    </figure>
    <div class="pasos">
      {@render pasos()}
    </div>
  {:else if estaticos}
    <!--
      Degradación de §6.4: una secuencia de gráficos estáticos apilados, cada
      uno con su texto. El lector recibe el mismo contenido sin depender de
      IntersectionObserver ni de que el JS haya cargado.
    -->
    <div class="apilados">
      {#each Array.from({ length: total }, (_, i) => i) as i (i)}
        <div class="apilado">
          {@render estaticos(i)}
        </div>
      {/each}
    </div>
  {:else}
    <!-- Sin snippet de estáticos: el gráfico una vez, y todos los pasos como
         prosa corrida. Sigue siendo legible; nunca una pantalla en blanco. -->
    <figure class="estatico">
      {@render grafico(0, 0)}
    </figure>
    <div class="pasos pasos--corridos">
      {@render pasos()}
    </div>
  {/if}
</section>

<style>
  .scrolly {
    position: relative;
    margin-block: var(--espacio-3xl);
  }

  /* ── Modo interactivo: dos columnas en desktop ────────────────────────── */
  @media (min-width: 721px) {
    .scrolly.interactivo {
      display: grid;
      grid-template-columns: 1fr minmax(20rem, 26rem);
      gap: var(--espacio-2xl);
      align-items: start;
    }

    .scrolly.interactivo .sticky {
      position: sticky
      /* Centrado vertical en el viewport, con aire para el título del gráfico. */;
      inset-block-start: max(var(--espacio-xl), 8vh);
      margin: 0;
      z-index: var(--capa-sticky);
    }
  }

  /* ── Móvil: el gráfico toma el 55% superior, NO el 100% (§6.3) ────────── */
  @media (max-width: 720px) {
    .scrolly.interactivo .sticky {
      position: sticky;
      inset-block-start: 0;
      /* 55vh deja siempre visible el texto que explica lo que cambió. Con
         100vh el lector scrollea a ciegas. */
      height: 55vh;
      display: flex;
      align-items: center;
      margin: 0;
      padding-block: var(--espacio-sm);
      background: var(--color-papel);
      /* Sombra inferior: separa el gráfico del texto que pasa por debajo. */
      box-shadow: 0 6px 12px -8px color-mix(in srgb, var(--color-tinta) 40%, transparent);
      z-index: var(--capa-sticky);
    }

    .scrolly.interactivo .sticky :global(svg) {
      max-height: 100%;
    }

    /* Primer paso a media pantalla: entra en cuadro junto con el gráfico. */
    .scrolly.interactivo .pasos {
      margin-block-start: var(--espacio-xl);
    }
  }

  .pasos {
    display: grid;
    /* El aire entre pasos es lo que da tiempo a leer antes del cambio. */
    gap: 70vh;
    padding-block: 25vh;
  }

  /* Sin interactividad no hace falta aire de scroll: es prosa corrida. */
  .pasos--corridos {
    gap: var(--espacio-xl);
    padding-block: var(--espacio-xl) 0;
  }

  .estatico {
    margin: 0 0 var(--espacio-lg);
  }

  /* ── Degradación apilada (movimiento reducido / sin JS) ───────────────── */
  .apilados {
    display: grid;
    gap: var(--espacio-3xl);
  }

  .apilado {
    display: grid;
    gap: var(--espacio-md);
  }
</style>
