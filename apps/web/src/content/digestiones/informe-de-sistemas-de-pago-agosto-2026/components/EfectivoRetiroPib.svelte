<!--
  EfectivoRetiroPib.svelte — comparador tipográfico, en "Los aperitivos".

  No es un `<Figura>`: son 2 cifras (2019 y 2025), citadas tal cual del
  cuerpo del Informe (§ "La materia prima" ya explica que sus gráficos son
  imágenes sin datos detrás — ver `limitaciones` del frontmatter). Envolverlo
  en Figura pediría una tabla equivalente y una interacción que no aportan
  nada con solo 2 números: es el mismo criterio que ya usa el layout para el
  pull-quote del `hallazgo`, tipografía grande en vez de un gráfico de barras
  de 2 columnas.

  Sigue siendo accesible sin necesitar foco/hover: los dos números y el
  delta están en el DOM como texto normal, con `aria-hidden` solo en la
  flecha decorativa.
-->
<script lang="ts">
  interface Props {
    desde: { anio: number; valor: number };
    hasta: { anio: number; valor: number };
    unidad: string;
  }

  let { desde, hasta, unidad }: Props = $props();

  const delta = $derived(Math.round((hasta.valor - desde.valor) * 10) / 10);
</script>

<figure class="comparador">
  <div class="cifras">
    <div class="cifra">
      <p class="cifra__valor">{desde.valor}%</p>
      <p class="cifra__etiqueta">{desde.anio}</p>
    </div>

    <span class="flecha" aria-hidden="true">→</span>

    <div class="cifra">
      <p class="cifra__valor cifra__valor--actual">{hasta.valor}%</p>
      <p class="cifra__etiqueta">{hasta.anio}</p>
    </div>
  </div>

  <figcaption>
    <p class="unidad">{unidad}</p>
    <p class="delta">{delta} puntos porcentuales en {hasta.anio - desde.anio} años</p>
  </figcaption>
</figure>

<style>
  .comparador {
    margin: var(--espacio-lg) 0;
    padding: var(--espacio-md) var(--espacio-lg);
    border: 1px solid var(--color-borde);
    border-radius: var(--radio-md);
    width: fit-content;
    max-width: 100%;
  }

  .cifras {
    display: flex;
    align-items: baseline;
    gap: var(--espacio-md);
    flex-wrap: wrap;
  }

  .cifra {
    text-align: center;
  }

  .cifra__valor {
    font-family: var(--fuente-display);
    font-size: var(--tipo-3xl);
    font-weight: var(--peso-semi);
    color: var(--color-tinta-suave);
    margin: 0;
    font-variant-numeric: tabular-nums;
  }

  .cifra__valor--actual {
    color: var(--color-bilis);
  }

  .cifra__etiqueta {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-2xs);
    color: var(--color-sello);
    margin: 0;
  }

  .flecha {
    font-size: var(--tipo-xl);
    color: var(--color-borde-fuerte);
  }

  figcaption {
    margin-block-start: var(--espacio-sm);
    padding-block-start: var(--espacio-sm);
    border-block-start: 1px solid var(--color-borde);
  }

  .unidad {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-3xs);
    letter-spacing: var(--tracking-amplio);
    text-transform: uppercase;
    color: var(--color-sello);
    margin: 0;
  }

  .delta {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-xs);
    color: var(--color-tinta);
    margin: var(--espacio-2xs) 0 0;
  }
</style>
