<!--
  EncuestaNacionalDeEmpleoEneAbrilJunio2026.svelte — gráfico principal de la digestión
  "Encuesta nacional de empleo (ENE) abril - junio 2026".

  Patrón canónico: D3 CALCULA, SVELTE RENDERIZA.
  Sin select, sin append, sin enter/exit. Svelte es dueño del DOM; D3 aporta
  escalas, formas y geografías. Importá SOLO los módulos que uses
  (d3-scale, d3-array), nunca `d3` completo.

  Barras divergentes: hay sectores que ganaron empleo y otros que perdieron,
  así que las barras crecen desde el cero hacia la derecha o la izquierda en
  vez de siempre desde el margen.

  Paleta: solo naranjo (`--color-bilis`) y gris (`--color-sello`), mezclados
  según qué tan grande es la variación — cuanto más lejos de cero, más
  naranjo; los movimientos chicos quedan casi grises. No es la escala
  divergente de 7 pasos del kit (esa es para series de datos con muchas
  marcas); acá hay una sola serie y lo que se codifica es relevancia, no
  categoría, así que alcanza con mezclar los dos colores de marca.

  Interacción (revisión del agente disenador-visualizaciones, §pudding.cool):
  esta figura se publicó sin ningún handler de foco ni mouse — un SVG con
  datos, pero nada que explorar. Se agrega tooltip accesible por teclado,
  igual patrón que las barras de FlujoPartidas.svelte: cada sector es
  alcanzable con Tab y el detalle exacto aparece igual con foco que con
  cursor.
-->
<script lang="ts">
  import { max, min } from 'd3-array';
  import { scaleBand, scaleLinear } from 'd3-scale';

  import Eje from '@digerido/kit/charts/Eje.svelte';
  import Figura from '@digerido/kit/charts/Figura.svelte';
  import TablaEquivalente from '@digerido/kit/charts/TablaEquivalente.svelte';
  import Tooltip from '@digerido/kit/charts/Tooltip.svelte';
  import { delta, numero } from '@digerido/kit/utils';

  interface Fila {
    sector: string;
    variacion12meses: number;
  }

  let { datos, unidad }: { datos: Fila[]; unidad: string } = $props();

  const ANCHO = 720;
  const ALTO = 320;
  // Suficiente para "Servicios administrativos y de apoyo" sin cortarse
  // (el nombre más largo de este dataset) en el eje de categoría.
  const margen = { top: 24, right: 60, bottom: 44, left: 280 };

  const ordenados = $derived([...datos].sort((a, b) => b.variacion12meses - a.variacion12meses));

  const maxAbsoluto = $derived(
    Math.max(
      Math.abs(min(datos, (d) => d.variacion12meses) ?? 0),
      max(datos, (d) => d.variacion12meses) ?? 0,
    ),
  );

  // ── D3 calcula ──────────────────────────────────────────────────────────
  const x = $derived(
    scaleLinear()
      .domain([-maxAbsoluto, maxAbsoluto])
      .nice()
      .range([margen.left, ANCHO - margen.right]),
  );

  const y = $derived(
    scaleBand()
      .domain(ordenados.map((d) => d.sector))
      .range([margen.top, ALTO - margen.bottom])
      .padding(0.32),
  );

  const cero = $derived(x(0));

  /** Gris para variaciones chicas, naranjo cada vez más intenso para las grandes. */
  function colorImportancia(valor: number): string {
    const t = maxAbsoluto === 0 ? 0 : Math.abs(valor) / maxAbsoluto;
    return `color-mix(in srgb, var(--color-bilis) ${Math.round(t * 100)}%, var(--color-sello))`;
  }

  // ── Estado del tooltip ────────────────────────────────────────────────────
  let activo = $state<Fila | null>(null);
  let posicion = $state({ x: 0, y: 0 });
  let lienzo = $state<HTMLDivElement | null>(null);

  function mostrar(d: Fila) {
    activo = d;
    const factor = (lienzo?.clientWidth ?? ANCHO) / ANCHO;
    posicion = {
      x: x(d.variacion12meses) * factor,
      y: ((y(d.sector) ?? 0) + y.bandwidth() / 2) * factor,
    };
  }

  const ocultar = () => (activo = null);
</script>

<Figura
  id="encuesta-nacional-de-empleo-ene-abril-junio-2026"
  titulo="Comunicaciones y minería perdieron empleo; transporte y salud lo impulsaron"
  descripcion="Entre los sectores con mayor variación, cuatro ganaron ocupados en el último año (liderados por servicios administrativos y de apoyo, +12,9 %) y tres perdieron, con comunicaciones a la cabeza de las caídas (-15,2 %)."
  unidades={unidad}
  fuente="INE, Boletín Estadístico: Empleo Trimestral, edición n°333 (31 julio 2026)"
>
  <div class="lienzo" bind:this={lienzo}>
    <svg viewBox="0 0 {ANCHO} {ALTO}" role="img" aria-label="Comunicaciones y minería perdieron empleo; transporte y salud lo impulsaron">
      <Eje
        escala={x}
        lado="abajo"
        ancho={ANCHO}
        alto={ALTO}
        {margen}
        grilla
        formato={(v) => `${numero(v as number, 0)}%`}
      />
      <Eje escala={y} lado="izquierda" ancho={ANCHO} alto={ALTO} {margen} />

      <line x1={cero} x2={cero} y1={margen.top} y2={ALTO - margen.bottom} class="linea-cero" />

      {#each ordenados as d (d.sector)}
        {@const desde = Math.min(cero, x(d.variacion12meses))}
        {@const hasta = Math.max(cero, x(d.variacion12meses))}
        <!--
          `tabindex` y los handlers de foco: cada sector es alcanzable con Tab,
          y el tooltip aparece igual que con el mouse. Sin esto, el detalle
          exacto solo existe para quien usa puntero.
        -->
        <g
          class="barra"
          class:atenuada={activo !== null && activo.sector !== d.sector}
          role="graphics-symbol"
          tabindex="0"
          aria-label="{d.sector}: {delta(d.variacion12meses, 1, ' %')} en doce meses"
          onmouseenter={() => mostrar(d)}
          onmouseleave={ocultar}
          onfocus={() => mostrar(d)}
          onblur={ocultar}
        >
          <rect
            x={desde}
            y={y(d.sector)}
            width={Math.max(0, hasta - desde)}
            height={y.bandwidth()}
            fill={colorImportancia(d.variacion12meses)}
          />
          <text
            x={d.variacion12meses >= 0 ? hasta + 6 : desde - 6}
            y={(y(d.sector) ?? 0) + y.bandwidth() / 2}
            text-anchor={d.variacion12meses >= 0 ? 'start' : 'end'}
            dominant-baseline="middle"
            class="etiqueta-valor"
          >
            {delta(d.variacion12meses, 1, '%')}
          </text>
        </g>
      {/each}
    </svg>

    <Tooltip
      visible={activo !== null}
      x={posicion.x}
      y={posicion.y}
      anchoContenedor={lienzo?.clientWidth ?? 0}
      altoContenedor={lienzo?.clientHeight ?? 0}
    >
      {#if activo}
        <strong>{activo.sector}</strong><br />
        {delta(activo.variacion12meses, 1, ' %')} en doce meses
      {/if}
    </Tooltip>
  </div>

  {#snippet tabla()}
    <TablaEquivalente
      datos={ordenados}
      resumen="Variación porcentual interanual de personas ocupadas por sector económico, trimestre móvil abril-junio 2026 vs. abril-junio 2025."
      columnas={[
        { llave: 'sector', titulo: 'Sector' },
        {
          llave: 'variacion12meses',
          titulo: 'Variación 12 meses (%)',
          numerica: true,
          formato: (v) => delta(v as number, 1, '%'),
        },
      ]}
    />
  {/snippet}
</Figura>

<style>
  .lienzo {
    position: relative;
  }

  .linea-cero {
    stroke: var(--color-borde-fuerte);
    stroke-width: 1;
  }

  .etiqueta-valor {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-2xs);
    font-variant-numeric: tabular-nums;
    fill: var(--color-tinta);
  }

  .barra {
    /* La transición es de opacidad, nunca de geometría: una barra que se
       estira al pasar el cursor impide comparar longitudes. */
    transition: opacity var(--duracion-rapida) var(--curva-salida);
  }

  .atenuada {
    opacity: 0.45;
  }

  .barra:focus-visible {
    outline: none;
  }

  /* El foco se dibuja en la barra misma: el outline por defecto del
     navegador sobre un <g> de SVG se recorta de formas impredecibles. */
  .barra:focus-visible rect {
    stroke: var(--color-enzima);
    stroke-width: 3;
    paint-order: stroke;
  }

  @media (prefers-reduced-motion: reduce) {
    .barra {
      transition: none;
    }
  }
</style>
