<!--
  Eje.svelte — ejes para el patrón "D3 calcula, Svelte renderiza".

  Recibe una escala de d3-scale ya construida y dibuja las marcas. Nunca llama
  a .append(): Svelte es dueño del DOM (apéndice del plan).

  Decisiones de diseño editorial:
  · La grilla es del eje de VALOR, no del de categoría. Líneas en los dos ejes
    convierten el gráfico en papel cuadriculado.
  · Sin línea de dominio en el eje de valor: la grilla ya lo comunica y una
    caja alrededor de los datos agrega tinta sin información.
  · Las unidades van en el rótulo del eje, no repetidas en cada marca.
-->
<script lang="ts">
  interface Props {
    /** Escala de d3-scale. Continua (`scaleLinear`) o de banda (`scaleBand`). */
    escala: {
      (v: never): number | undefined;
      domain(): unknown[];
      ticks?: (n?: number) => number[];
      bandwidth?: () => number;
      tickFormat?: (n?: number) => (v: never) => string;
    };
    /** Dónde vive el eje. */
    lado: 'abajo' | 'izquierda' | 'arriba' | 'derecha';
    /** Extensión del área de dibujo, para posicionar y trazar la grilla. */
    ancho: number;
    alto: number;
    margen: { top: number; right: number; bottom: number; left: number };
    /** Rótulo con la unidad. "MM$ de 2026", "% del total". */
    rotulo?: string;
    /** Cantidad sugerida de marcas. d3 la ajusta a números redondos. */
    marcas?: number;
    /** Líneas de grilla que cruzan el área de datos. Solo en el eje de valor. */
    grilla?: boolean;
    /** Formateador propio. Por defecto usa el de la escala. */
    formato?: (valor: never) => string;
    /** Oculta marcas cuando no caben (ejes de categoría densos). */
    saltar?: number;
    /**
     * Compensación de escala: `ANCHO_VIEWBOX / anchoReal`, medida con
     * `observarAncho` en el gráfico que usa este eje. El SVG entero se encoge
     * con `width: 100%` cuando el contenedor es más angosto que el viewBox —
     * sin esto, el texto de las marcas se encoge junto con el dibujo y en un
     * celular queda ilegible (ver `packages/kit/src/utils/redimension.ts`).
     * Por defecto 1: sin medición, el eje se comporta como siempre.
     */
    factor?: number;
  }

  let {
    escala, lado, ancho, alto, margen,
    rotulo, marcas = 5, grilla = false, formato, saltar = 1, factor = 1,
  }: Props = $props();

  const horizontal = $derived(lado === 'abajo' || lado === 'arriba');

  /** Una escala de banda no tiene `ticks`: sus marcas son el dominio. */
  const esBanda = $derived(typeof escala.bandwidth === 'function');

  const valores = $derived.by(() => {
    const brutos = esBanda
      ? (escala.domain() as never[])
      : ((escala.ticks?.(marcas) ?? escala.domain()) as never[]);
    return brutos.filter((_, i) => i % saltar === 0);
  });

  const etiqueta = $derived.by(() => {
    if (formato) return formato;
    const propio = escala.tickFormat?.(marcas);
    return propio ?? ((v: never) => String(v));
  });

  /** Centro de la banda, o el punto exacto en una escala continua. */
  function posicion(v: never): number {
    const base = escala(v) ?? 0;
    return esBanda ? base + (escala.bandwidth?.() ?? 0) / 2 : base;
  }

  const linea = $derived(
    lado === 'abajo' ? alto - margen.bottom
    : lado === 'arriba' ? margen.top
    : lado === 'izquierda' ? margen.left
    : ancho - margen.right,
  );
</script>

<g class="eje eje--{lado}" aria-hidden="true">
  {#if grilla}
    <g class="grilla">
      {#each valores as v (String(v))}
        {#if horizontal}
          <line x1={posicion(v)} x2={posicion(v)} y1={margen.top} y2={alto - margen.bottom} />
        {:else}
          <line x1={margen.left} x2={ancho - margen.right} y1={posicion(v)} y2={posicion(v)} />
        {/if}
      {/each}
    </g>
  {/if}

  <g class="marcas">
    {#each valores as v (String(v))}
      {#if horizontal}
        {@const px = posicion(v)}
        {@const py = lado === 'abajo' ? linea + 18 : linea - 10}
        <!--
          El `<g>` de compensación traslada al punto de anclaje, escala ahí
          mismo y traslada de vuelta: el texto queda del mismo tamaño real en
          pantalla sin moverse de la marca que etiqueta (ver prop `factor`).
        -->
        <g transform="translate({px} {py}) scale({factor}) translate({-px} {-py})">
          <text
            x={px}
            y={py}
            text-anchor="middle"
            dominant-baseline={lado === 'abajo' ? 'hanging' : 'auto'}>{etiqueta(v)}</text>
        </g>
      {:else}
        {@const px = lado === 'izquierda' ? linea - 10 : linea + 10}
        {@const py = posicion(v)}
        <g transform="translate({px} {py}) scale({factor}) translate({-px} {-py})">
          <text
            x={px}
            y={py}
            text-anchor={lado === 'izquierda' ? 'end' : 'start'}
            dominant-baseline="middle">{etiqueta(v)}</text>
        </g>
      {/if}
    {/each}
  </g>

  {#if rotulo}
    <!--
      El rótulo del eje vertical se rota, pero se ancla al tope en vez de
      centrarse: en un gráfico alto, un rótulo vertical centrado obliga a
      girar la cabeza para encontrarlo.
    -->
    {#if horizontal}
      {@const rx = margen.left}
      {@const ry = lado === 'abajo' ? alto - 4 : 12}
      <g transform="translate({rx} {ry}) scale({factor}) translate({-rx} {-ry})">
        <text class="rotulo" x={rx} y={ry} text-anchor="start">{rotulo}</text>
      </g>
    {:else}
      {@const rx = margen.left}
      {@const ry = margen.top - 12}
      <g transform="translate({rx} {ry}) scale({factor}) translate({-rx} {-ry})">
        <text class="rotulo" x={rx} y={ry} text-anchor="start">{rotulo}</text>
      </g>
    {/if}
  {/if}
</g>

<style>
  .eje text {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-2xs);
    fill: var(--color-sello);
    font-variant-numeric: tabular-nums;
  }

  .rotulo {
    fill: var(--color-tinta-suave);
    letter-spacing: var(--tracking-versalita);
    text-transform: uppercase;
    font-size: var(--tipo-3xs);
  }

  /* Grilla al fondo del tono: debe guiar el ojo sin competir con las marcas. */
  .grilla line {
    stroke: var(--color-borde);
    stroke-width: 1;
    shape-rendering: crispEdges;
  }
</style>
