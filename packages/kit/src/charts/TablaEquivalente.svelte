<!--
  TablaEquivalente.svelte — la tabla accesible de cada gráfico (§8).

  Punto clave del plan: "Se genera desde la misma fuente, así nunca queda
  desactualizada." Por eso este componente recibe LOS MISMOS datos que el
  gráfico, no una copia escrita a mano. Si el gráfico cambia de datos, la tabla
  cambia sola; no hay forma de que se separen.

  Va dentro de un `<details>` para no empujar el artículo, pero el contenido
  existe en el DOM desde el build: un lector de pantalla lo encuentra, y
  también Ctrl+F.
-->
<script lang="ts" generics="T extends Record<string, unknown>">
  interface Columna {
    /** Llave en el objeto de datos. */
    llave: string;
    /** Encabezado visible. Debe incluir la unidad. */
    titulo: string;
    /** Formateador. Sin él se usa String(). */
    formato?: (valor: never, fila: never) => string;
    /** Alineación: los números van a la derecha para comparar magnitudes. */
    numerica?: boolean;
  }

  interface Props {
    datos: readonly T[];
    columnas: readonly Columna[];
    /** Resumen de la tabla. Reutiliza el aria-label del gráfico. */
    resumen: string;
    /** Texto del disclosure. */
    etiqueta?: string;
    /** Nota al pie: fuente, unidades, redondeos. */
    nota?: string;
  }

  let { datos, columnas, resumen, etiqueta = 'Ver datos', nota }: Props = $props();

  function celda(fila: T, col: Columna): string {
    const v = fila[col.llave];
    if (col.formato) return col.formato(v as never, fila as never);
    if (v === null || v === undefined) return '—'; // "sin dato" ≠ cero
    return String(v);
  }
</script>

<details class="tabla-equivalente">
  <summary>{etiqueta}</summary>

  <div class="marco">
    <table>
      <caption>{resumen}</caption>
      <thead>
        <tr>
          {#each columnas as col (col.llave)}
            <th scope="col" class:num={col.numerica}>{col.titulo}</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each datos as fila, i (i)}
          <tr>
            {#each columnas as col, j (col.llave)}
              <!-- La primera columna es el encabezado de fila: da contexto al
                   navegar celda por celda con lector de pantalla. -->
              {#if j === 0}
                <th scope="row">{celda(fila, col)}</th>
              {:else}
                <td class:num={col.numerica}>{celda(fila, col)}</td>
              {/if}
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  {#if nota}<p class="nota">{nota}</p>{/if}
</details>

<style>
  .tabla-equivalente {
    margin-block-start: var(--espacio-sm);
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-2xs);
  }

  summary {
    cursor: pointer;
    color: var(--color-sello);
    letter-spacing: var(--tracking-versalita);
    text-transform: uppercase;
    font-size: var(--tipo-3xs);
    padding-block: var(--espacio-2xs);
  }

  summary:hover {
    color: var(--color-tinta);
  }

  /* Foco visible: requisito de §8, y `outline: none` sin reemplazo es la forma
     más común de romperlo. */
  summary:focus-visible {
    outline: 2px solid var(--color-enzima);
    outline-offset: 2px;
    color: var(--color-tinta);
  }

  /* Tabla ancha: scroll dentro de su propio marco, nunca en el body. */
  .marco {
    overflow-x: auto;
    margin-block-start: var(--espacio-xs);
    border: 1px solid var(--color-borde);
  }

  table {
    border-collapse: collapse;
    width: 100%;
    font-variant-numeric: tabular-nums;
  }

  caption {
    text-align: start;
    padding: var(--espacio-xs) var(--espacio-sm);
    color: var(--color-tinta-suave);
    font-size: var(--tipo-3xs);
    line-height: 1.4;
    border-block-end: 1px solid var(--color-borde);
  }

  th,
  td {
    padding: var(--espacio-2xs) var(--espacio-sm);
    text-align: start;
    border-block-end: 1px solid var(--color-borde);
  }

  thead th {
    color: var(--color-tinta);
    font-weight: var(--peso-semi);
    background: var(--color-papel-bajo);
    position: sticky;
    inset-block-start: 0;
  }

  tbody th {
    font-weight: var(--peso-regular);
    color: var(--color-tinta);
  }

  .num {
    text-align: end;
  }

  tbody tr:last-child :is(th, td) {
    border-block-end: none;
  }

  .nota {
    margin-block-start: var(--espacio-xs);
    color: var(--color-sello);
    font-size: var(--tipo-3xs);
    line-height: 1.5;
  }
</style>
