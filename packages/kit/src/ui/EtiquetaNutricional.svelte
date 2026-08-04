<!--
  EtiquetaNutricional.svelte — el elemento firma del sitio (§5).

  "Es el logo del sitio, el objeto compartible, el resumen y el chiste — todo en
  un componente." Toda la audacia visual del sistema se gasta acá; el resto se
  mantiene sobrio.

  Se renderiza en el servidor, sin isla: es estático, y no cuesta un byte de JS.
  La misma estructura la reproduce el generador de OG images
  (apps/web/src/pages/og/), que es lo que circula en WhatsApp y X.

  Trazada como una etiqueta nutricional real: reglas gruesas separando bloques,
  cifras alineadas a la derecha en monoespaciada, y una barra de contraste entre
  el antes y el después. La comparación ES el argumento del sitio.
-->
<script lang="ts">
  import { duracion, numero } from '../utils/formato.js';
  import { nivelDeLegibilidad } from '../utils/legibilidad.js';

  interface Original {
    // `| undefined` explícito: llegan desde el frontmatter, donde opcional
    // significa `T | undefined`.
    paginas?: number | undefined;
    palabras: number;
    siglasSinDefinir?: number | undefined;
    legibilidad: number;
    /** Minutos. Se formatea a "14 h" solo. */
    tiempoLectura: number;
  }

  interface Digerido {
    tiempoLectura: number;
    graficos: number;
    legibilidad: number;
    palabras?: number | undefined;
  }

  interface Props {
    original: Original;
    digerido: Digerido;
    /** Compacta: para tarjetas del índice. */
    compacta?: boolean;
  }

  let { original, digerido, compacta = false }: Props = $props();

  /** Cuánto se comprimió el tiempo de lectura. El número del chiste. */
  const reduccion = $derived(
    original.tiempoLectura > 0
      ? Math.round((1 - digerido.tiempoLectura / original.tiempoLectura) * 100)
      : 0,
  );

  const filasOriginal = $derived(
    [
      original.paginas !== undefined
        ? { etiqueta: 'Páginas originales', valor: numero(original.paginas) }
        : null,
      { etiqueta: 'Palabras', valor: numero(original.palabras) },
      original.siglasSinDefinir !== undefined
        ? { etiqueta: 'Siglas sin definir', valor: numero(original.siglasSinDefinir) }
        : null,
      {
        etiqueta: 'Índice de legibilidad',
        valor: `${original.legibilidad} / 100`,
        nota: nivelDeLegibilidad(original.legibilidad),
      },
      { etiqueta: 'Tiempo de lectura', valor: duracion(original.tiempoLectura) },
    ].filter((f): f is { etiqueta: string; valor: string; nota?: string } => f !== null),
  );

  const filasDigerido = $derived([
    { etiqueta: 'Tiempo de lectura', valor: duracion(digerido.tiempoLectura) },
    { etiqueta: 'Gráficos', valor: numero(digerido.graficos) },
    {
      etiqueta: 'Legibilidad',
      valor: `${digerido.legibilidad} / 100`,
      nota: nivelDeLegibilidad(digerido.legibilidad),
    },
  ]);
</script>

<!--
  `<table>` de verdad, no divs: son datos tabulares, y así un lector de
  pantalla los anuncia como pares etiqueta/valor.
-->
<table class="etiqueta" class:compacta>
  <caption>Información nutricional del documento</caption>

  <tbody>
    <tr class="seccion">
      <th colspan="2" scope="colgroup">Antes de digerir</th>
    </tr>
    {#each filasOriginal as fila (fila.etiqueta)}
      <tr>
        <th scope="row">
          {fila.etiqueta}
          {#if fila.nota}<span class="nota">{fila.nota}</span>{/if}
        </th>
        <td>{fila.valor}</td>
      </tr>
    {/each}

    <tr class="seccion seccion--corte">
      <th colspan="2" scope="colgroup">Después de digerir</th>
    </tr>
    {#each filasDigerido as fila (fila.etiqueta)}
      <tr>
        <th scope="row">
          {fila.etiqueta}
          {#if fila.nota}<span class="nota">{fila.nota}</span>{/if}
        </th>
        <td>{fila.valor}</td>
      </tr>
    {/each}
  </tbody>

  {#if !compacta && reduccion > 0}
    <tfoot>
      <tr>
        <td colspan="2" class="cierre">
          <strong>{reduccion} %</strong> menos tiempo de lectura
        </td>
      </tr>
    </tfoot>
  {/if}
</table>

<style>
  /* Ancho fijo en ch: la etiqueta es un objeto, no un bloque fluido. Se lee
     igual acá que en la imagen OG. */
  .etiqueta {
    width: 100%;
    max-width: 26rem;
    border-collapse: collapse;
    background: var(--color-papel-alto);
    /* Regla exterior gruesa: la etiqueta nutricional real tiene marco. */
    border: 2px solid var(--color-tinta);
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-2xs);
    color: var(--color-tinta);
    font-variant-numeric: tabular-nums;
  }

  caption {
    caption-side: top;
    text-align: start;
    padding: var(--espacio-xs) var(--espacio-sm);
    background: var(--color-tinta);
    color: var(--color-papel);
    font-weight: var(--peso-bold);
    font-size: var(--tipo-3xs);
    letter-spacing: var(--tracking-versalita);
    text-transform: uppercase;
  }

  .seccion th {
    padding: var(--espacio-xs) var(--espacio-sm) var(--espacio-2xs);
    text-align: start;
    font-size: var(--tipo-3xs);
    letter-spacing: var(--tracking-versalita);
    text-transform: uppercase;
    color: var(--color-sello);
    font-weight: var(--peso-media);
    border-block-end: 1px solid var(--color-tinta);
  }

  /* El corte entre "antes" y "después": la regla más gruesa de la etiqueta.
     Es donde ocurre la digestión, y se ve. */
  .seccion--corte th {
    border-block-start: 6px solid var(--color-tinta);
    color: var(--color-tinta);
    padding-block-start: var(--espacio-sm);
  }

  tbody tr:not(.seccion) th {
    font-weight: var(--peso-regular);
    text-align: start;
    padding: var(--espacio-2xs) var(--espacio-sm);
    border-block-end: 1px solid var(--color-borde);
    line-height: 1.35;
  }

  tbody tr:not(.seccion) td {
    text-align: end;
    padding: var(--espacio-2xs) var(--espacio-sm);
    border-block-end: 1px solid var(--color-borde);
    font-weight: var(--peso-semi);
    white-space: nowrap;
  }

  /* El nivel cualitativo ("muy difícil") explica la cifra sin ocupar su fila. */
  .nota {
    display: block;
    color: var(--color-sello);
    font-size: var(--tipo-3xs);
    font-style: normal;
  }

  .cierre {
    padding: var(--espacio-sm);
    text-align: center;
    border-block-start: 2px solid var(--color-tinta);
    background: var(--color-papel-bajo);
    font-size: var(--tipo-2xs);
  }

  .cierre strong {
    /* Único lugar de la etiqueta donde entra el naranja: el remate. */
    color: var(--color-bilis);
    font-size: var(--tipo-lg);
    font-weight: var(--peso-bold);
  }

  .compacta {
    max-width: none;
    font-size: var(--tipo-3xs);
  }

  .compacta :is(th, td) {
    padding-block: var(--espacio-3xs);
  }
</style>
