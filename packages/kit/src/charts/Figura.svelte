<!--
  Figura.svelte — el envoltorio canónico de todo gráfico (apéndice del plan).

  Existe para que el checklist de publicación de §10 sea estructural en vez de
  una lista que alguien recuerda: "todo gráfico tiene título, unidades, fuente y
  anotación" y "tabla equivalente accesible presente". Acá, un gráfico sin
  fuente ni descripción no se puede construir.

  Aporta además lo de §8 sobre compartibilidad: ancla propia (`#g-<id>`) para
  que el gráfico circule solo, no solo el artículo.
-->
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    /** Ancla y `id` del SVG. Genera `#g-<id>`, la URL compartible del gráfico. */
    id: string;
    /** Título del gráfico. Afirma algo; no nombra el tipo de gráfico. */
    titulo: string;
    /**
     * Descripción para lector de pantalla. Debe comunicar EL HALLAZGO (§8):
     *   mal:  "gráfico de barras de gasto por partida"
     *   bien: "Salud concentra el 31 % del aumento, tres veces más que Educación"
     */
    descripcion: string;
    /** Unidades y año base. "MM$ de 2026", "% del total". */
    unidades: string;
    /** Atribución. "DIPRES, Ley de Presupuestos 2027". */
    fuente: string;
    /** Bajada opcional entre el título y el gráfico. */
    bajada?: string;
    /** Nota al pie: metodología, redondeos, exclusiones. */
    nota?: string;
    /** El SVG o canvas. */
    children: Snippet;
    /** La tabla equivalente. Obligatoria por §8. */
    tabla?: Snippet;
    /** A sangre: el gráfico se sale de la columna de texto. */
    sangria?: 'texto' | 'ancho' | 'completo';
  }

  let {
    id, titulo, descripcion, unidades, fuente,
    bajada, nota, children, tabla, sangria = 'ancho',
  }: Props = $props();

  /**
   * Guardias editoriales de desarrollo para las reglas de §8. Una descripción
   * que empieza nombrando el tipo de gráfico no describe nada: es lo único que
   * un lector de pantalla NO necesita que le digan.
   *
   * Va en `$effect` y no en el cuerpo del módulo para que lea los valores
   * actuales de las props, no los iniciales.
   */
  $effect(() => {
    if (!import.meta.env.DEV) return;

    const tipoDeGrafico = /^(un |el )?(gr[áa]fico|diagrama|mapa|tabla|barra|l[íi]nea)/i;
    if (tipoDeGrafico.test(descripcion.trim())) {
      console.warn(
        `[kit] Figura "${id}": la descripción empieza nombrando el tipo de gráfico ` +
          `("${descripcion.slice(0, 40)}…"). §8 pide que comunique el hallazgo. ` +
          'Mal: "gráfico de barras de gasto". Bien: "Salud concentra el 31 % del aumento".',
      );
    }
    if (!tabla) {
      console.warn(
        `[kit] Figura "${id}": sin tabla equivalente. §8 la declara no negociable ` +
          '— pasá el snippet `tabla` con <TablaEquivalente>.',
      );
    }
  });
</script>

<figure class="figura figura--{sangria}" id="g-{id}">
  <figcaption class="encabezado">
    <!-- El título es h3: el gráfico vive dentro de una sección del artículo,
         y saltarse niveles rompe la navegación por encabezados. -->
    <h3>
      {titulo}
      <!-- Ancla visible al pasar el cursor: así se copia el link del gráfico. -->
      <a class="ancla" href="#g-{id}" aria-label="Enlace permanente a este gráfico">§</a>
    </h3>
    {#if bajada}<p class="bajada">{bajada}</p>{/if}
    <p class="unidades">{unidades}</p>
  </figcaption>

  <div class="lienzo">
    {@render children()}
  </div>

  {#if tabla}{@render tabla()}{/if}

  <figcaption class="pie">
    {#if nota}<p class="nota">{nota}</p>{/if}
    <p class="fuente">Fuente: {fuente}</p>
    <!-- La descripción del hallazgo también queda en el DOM para lectores de
         pantalla que no anuncian el aria-label de un SVG anidado. -->
    <p class="sr-only">{descripcion}</p>
  </figcaption>
</figure>

<style>
  .figura {
    margin-block: var(--espacio-2xl);
    margin-inline: auto;
  }

  /* Carriles de la grilla del artículo: el componente elige carril, no px. */
  .figura--texto {
    width: var(--medida-texto);
  }
  .figura--ancho {
    width: min(56rem, 100%);
  }
  .figura--completo {
    width: 100%;
  }

  .encabezado {
    margin-block-end: var(--espacio-md);
  }

  h3 {
    font-family: var(--fuente-display);
    font-size: var(--tipo-lg);
    font-weight: var(--peso-semi);
    line-height: var(--interlinea-corta);
    color: var(--color-tinta);
    margin: 0;
    text-wrap: balance;
  }

  .ancla {
    color: var(--color-borde-fuerte);
    text-decoration: none;
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-xs);
    opacity: 0;
    transition: opacity var(--duracion-rapida) var(--curva-salida);
    padding-inline: var(--espacio-2xs);
  }

  /* El ancla aparece al pasar por la figura, y siempre que reciba foco. */
  .figura:hover .ancla,
  .ancla:focus-visible {
    opacity: 1;
  }

  .ancla:focus-visible {
    outline: 2px solid var(--color-enzima);
    outline-offset: 2px;
  }

  .bajada {
    font-family: var(--fuente-cuerpo);
    font-size: var(--tipo-sm);
    line-height: var(--interlinea-corta);
    color: var(--color-tinta-suave);
    max-width: var(--medida-angosta);
    margin-block: var(--espacio-2xs) 0;
  }

  .unidades,
  .fuente,
  .nota {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-3xs);
    color: var(--color-sello);
    margin: 0;
  }

  .unidades {
    margin-block-start: var(--espacio-xs);
    letter-spacing: var(--tracking-amplio);
  }

  .lienzo {
    /* Un gráfico ancho scrollea dentro de su marco; el body nunca. */
    overflow-x: auto;
  }

  .lienzo :global(svg) {
    display: block;
    width: 100%;
    height: auto;
    overflow: visible;
  }

  .pie {
    margin-block-start: var(--espacio-sm);
    padding-block-start: var(--espacio-xs);
    border-block-start: 1px solid var(--color-borde);
    display: grid;
    gap: var(--espacio-2xs);
  }

  .nota {
    line-height: 1.5;
    max-width: var(--medida-angosta);
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip-path: inset(50%);
    white-space: nowrap;
    border: 0;
  }
</style>
