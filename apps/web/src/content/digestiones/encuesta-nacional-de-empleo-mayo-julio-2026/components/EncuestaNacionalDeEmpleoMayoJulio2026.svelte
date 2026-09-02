<!--
  EncuestaNacionalDeEmpleoMayoJulio2026.svelte — gráfico principal de la digestión
  "Encuesta nacional de empleo (ENE) mayo - julio 2026".

  Mismo patrón que la edición anterior (mismo shape de dato: variación
  interanual de ocupados por sector, 7 categorías destacadas por el propio
  INE) — no se varía el lenguaje visual acá porque el dato es literalmente
  el mismo tipo de serie trimestre a trimestre; variar por variar habría
  sido ruido, no señal (criterio del agente disenador-visualizaciones).

  Patrón canónico: D3 CALCULA, SVELTE RENDERIZA.
  Sin select, sin append, sin enter/exit. Svelte es dueño del DOM; D3 aporta
  escalas, formas y geografías. Importá SOLO los módulos que uses
  (d3-scale, d3-array), nunca `d3` completo.

  Barras divergentes: hay sectores que ganaron empleo y otros que perdieron,
  así que las barras crecen desde el cero hacia la derecha o la izquierda en
  vez de siempre desde el margen.

  Paleta: solo naranjo (`--color-bilis`) y gris (`--color-sello`), mezclados
  según qué tan grande es la variación — cuanto más lejos de cero, más
  naranjo; los movimientos chicos quedan casi grises.

  Interacción: tooltip accesible por teclado — cada sector es alcanzable con
  Tab y el detalle exacto aparece igual con foco que con cursor.

  Compensación de escala de texto (`factorTexto`/`observarAncho`): el SVG se
  encoge con `width: 100%` en pantallas angostas, y sin esto el texto de los
  ejes y las etiquetas de valor se encoge junto con el dibujo hasta quedar
  ilegible en celular (ver packages/kit/src/utils/redimension.ts). Mismo
  arreglo ya aplicado a las tres piezas publicadas — esta pieza nueva lo
  incluye desde el principio en vez de tener que agregarlo después.

  Momento de deleite: las barras entran una a una, en cascada, la primera
  vez que el gráfico aparece en pantalla (acción `enVista` del kit). Es
  progresivo: sin JS, con `prefers-reduced-motion`, o si el gráfico ya está
  visible al cargar la página, las barras se muestran directo en su
  posición final.
-->
<script lang="ts">
  import { max, min } from 'd3-array';
  import { scaleBand, scaleLinear } from 'd3-scale';

  import Eje from '@digerido/kit/charts/Eje.svelte';
  import Figura from '@digerido/kit/charts/Figura.svelte';
  import TablaEquivalente from '@digerido/kit/charts/TablaEquivalente.svelte';
  import Tooltip from '@digerido/kit/charts/Tooltip.svelte';
  import { delta, enVista, numero, observarAncho } from '@digerido/kit/utils';

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

  // Ancho real del contenedor, medido en vivo: alimenta el factor de posición
  // del tooltip y el de compensación de texto de Eje/`.etiqueta-valor`
  // (§ "el SVG se encoge en móvil").
  let anchoLienzo = $state(ANCHO);
  const factorTexto = $derived(ANCHO / Math.max(1, anchoLienzo));

  function mostrar(d: Fila) {
    activo = d;
    const factor = anchoLienzo / ANCHO;
    posicion = {
      x: x(d.variacion12meses) * factor,
      y: ((y(d.sector) ?? 0) + y.bandwidth() / 2) * factor,
    };
  }

  const ocultar = () => (activo = null);

  // ── Momento de deleite: revelado en cascada ─────────────────────────────
  let estadoRevelado = $state<'oculto' | 'revelado'>('revelado');
</script>

<Figura
  id="encuesta-nacional-de-empleo-mayo-julio-2026"
  titulo="Información y comunicaciones perdió más empleo que ningún otro sector"
  descripcion="Información y comunicaciones perdió 14,6% de sus empleos en doce meses, la caída más fuerte entre los sectores destacados; servicios administrativos y de apoyo (+10,8%) fue el que más contrató."
  unidades={unidad}
  fuente="INE, Boletín Estadístico: Empleo Trimestral, edición n°334 (28 agosto 2026)"
>
  <div
    class="lienzo"
    bind:this={lienzo}
    use:enVista={(estado) => (estadoRevelado = estado)}
    use:observarAncho={(a) => (anchoLienzo = a)}
  >
    <svg viewBox="0 0 {ANCHO} {ALTO}" role="img" aria-label="Información y comunicaciones perdió más empleo que ningún otro sector; servicios administrativos y de apoyo fue el que más contrató">
      <Eje
        escala={x}
        lado="abajo"
        ancho={ANCHO}
        alto={ALTO}
        {margen}
        grilla
        formato={(v) => `${numero(v as number, 0)}%`}
        factor={factorTexto}
      />
      <Eje escala={y} lado="izquierda" ancho={ANCHO} alto={ALTO} {margen} factor={factorTexto} />

      <line x1={cero} x2={cero} y1={margen.top} y2={ALTO - margen.bottom} class="linea-cero" />

      {#each ordenados as d, i (d.sector)}
        {@const desde = Math.min(cero, x(d.variacion12meses))}
        {@const hasta = Math.max(cero, x(d.variacion12meses))}
        {@const valorX = d.variacion12meses >= 0 ? hasta + 6 : desde - 6}
        {@const valorY = (y(d.sector) ?? 0) + y.bandwidth() / 2}
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
            class="rect"
            class:oculta={estadoRevelado === 'oculto'}
            style="transition-delay: {i * 55}ms"
            x={desde}
            y={y(d.sector)}
            width={Math.max(0, hasta - desde)}
            height={y.bandwidth()}
            fill={colorImportancia(d.variacion12meses)}
          />
          <!-- Compensación de escala: ver Eje.svelte/Anotacion.svelte, mismo patrón. -->
          <g transform="translate({valorX} {valorY}) scale({factorTexto}) translate({-valorX} {-valorY})">
            <text
              x={valorX}
              y={valorY}
              text-anchor={d.variacion12meses >= 0 ? 'start' : 'end'}
              dominant-baseline="middle"
              class="etiqueta-valor"
            >
              {delta(d.variacion12meses, 1, '%')}
            </text>
          </g>
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
      resumen="Variación porcentual interanual de personas ocupadas por sector económico, trimestre móvil mayo-julio 2026 vs. mayo-julio 2025."
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

  /*
    Momento de deleite: entrada en cascada. Vive en `.rect`, no en `.barra`,
    a propósito — la regla de arriba ("nunca de geometría" en hover) sigue
    valiendo para pasar el cursor; esto es una animación de una sola vez,
    al montar el gráfico, no una respuesta a interacción continua.
  */
  .rect {
    transform-box: fill-box;
    transform-origin: center;
    transition: transform 550ms var(--curva-salida);
  }

  .rect.oculta {
    transform: translateY(10px) scaleY(0.82);
  }

  @media (prefers-reduced-motion: reduce) {
    .rect {
      transition: none;
    }

    .barra {
      transition: none;
    }
  }
</style>
