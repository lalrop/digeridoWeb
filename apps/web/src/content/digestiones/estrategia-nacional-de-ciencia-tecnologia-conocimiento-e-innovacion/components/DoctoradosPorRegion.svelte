<!--
  DoctoradosPorRegion.svelte — gráfico principal, en "El plato de fondo".

  Barras horizontales, ordenadas de mayor a menor, de doctorados trabajando
  por cada 1.000 trabajadores — la métrica de INTENSIDAD que da vuelta la
  pregunta que abrió la pieza (el mapa de calor de "El plato de entrada"
  mostraba VOLUMEN de investigadores, donde la Región Metropolitana domina
  sin competencia; acá no). Un solo destacado (Los Ríos, el hallazgo) y el
  resto en contexto — "un solo destacado por gráfico"
  (packages/tokens/src/color.ts).

  Es una fotografía de las 16 regiones en un momento dado, no una secuencia:
  hover/foco para explorar, sin scrollytelling — mismo criterio que el resto
  de gráficos de apoyo/principales de una sola tabla en este kit.

  Momento de deleite: las barras entran en cascada, de mayor a menor, la
  primera vez que el gráfico aparece en pantalla (acción `enVista`). Es
  progresivo: sin JS, con `prefers-reduced-motion`, o si ya está visible al
  cargar, se muestran directo en su posición final.
-->
<script lang="ts">
  import { max } from 'd3-array';
  import { scaleBand, scaleLinear } from 'd3-scale';

  import Eje from '@digerido/kit/charts/Eje.svelte';
  import Figura from '@digerido/kit/charts/Figura.svelte';
  import TablaEquivalente from '@digerido/kit/charts/TablaEquivalente.svelte';
  import Tooltip from '@digerido/kit/charts/Tooltip.svelte';
  import { enVista, escalaDestacado, numero, observarAncho } from '@digerido/kit/utils';

  interface Fila {
    region: string;
    universidades: number;
    investigadores: number;
    doctoradosPor1000: number;
  }

  let { datos }: { datos: Fila[] } = $props();

  const REGION_DESTACADA = 'Los Ríos';

  const ordenados = $derived([...datos].sort((a, b) => b.doctoradosPor1000 - a.doctoradosPor1000));

  const ANCHO = 720;
  const ALTO_POR_FILA = 26;
  const ALTO = $derived(ordenados.length * ALTO_POR_FILA + 60);

  const ANCHO_CARACTER = 6.4;
  const margen = $derived({
    top: 20,
    right: 40,
    bottom: 32,
    // "Arica y Parinacota" es el nombre más largo de las 16 regiones.
    left: Math.max(64, Math.ceil(Math.max(...datos.map((d) => d.region.length)) * ANCHO_CARACTER) + 16),
  });

  // ── D3 calcula ────────────────────────────────────────────────────────────
  const x = $derived(
    scaleLinear()
      .domain([0, max(ordenados, (d) => d.doctoradosPor1000) ?? 0])
      .nice()
      .range([margen.left, ANCHO - margen.right]),
  );

  const y = $derived(
    scaleBand()
      .domain(ordenados.map((d) => d.region))
      .range([margen.top, ALTO - margen.bottom])
      .padding(0.28),
  );

  const colores = $derived(escalaDestacado(ordenados, (d) => d.region === REGION_DESTACADA));

  // ── Estado del tooltip ────────────────────────────────────────────────────
  let activa = $state<Fila | null>(null);
  let lienzo = $state<HTMLDivElement | null>(null);

  let anchoLienzo = $state(ANCHO);
  const factorTexto = $derived(ANCHO / Math.max(1, anchoLienzo));

  function mostrar(d: Fila) {
    activa = d;
  }
  const ocultar = () => (activa = null);

  const posicionTooltip = $derived.by(() => {
    if (!activa) return { x: 0, y: 0 };
    const factor = anchoLienzo / ANCHO;
    return {
      x: x(activa.doctoradosPor1000) * factor,
      y: ((y(activa.region) ?? 0) + y.bandwidth() / 2) * factor,
    };
  });

  // ── Momento de deleite: revelado en cascada ─────────────────────────────
  let estadoRevelado = $state<'oculto' | 'revelado'>('revelado');
</script>

<Figura
  id="doctorados-por-region"
  titulo="Los Ríos tiene más doctorados por trabajador que la Región Metropolitana"
  descripcion="Los Ríos lidera con 4,3 doctorados trabajando por cada 1.000 personas empleadas, por encima de Biobío (2,7) y de la Región Metropolitana (2,6); O'Higgins tiene la tasa más baja del país (0,3)."
  unidades="Doctorados trabajando por cada 1.000 trabajadores, por región"
  fuente="Consejo Nacional de CTCI, Estrategia Nacional de Ciencia, Tecnología, Conocimiento e Innovación para el Desarrollo de Chile 2026"
  sangria="ancho"
>
  <div
    class="lienzo"
    bind:this={lienzo}
    use:enVista={(estado) => (estadoRevelado = estado)}
    use:observarAncho={(a) => (anchoLienzo = a)}
  >
    <svg viewBox="0 0 {ANCHO} {ALTO}" role="img" aria-label="Los Ríos tiene más doctorados por trabajador que la Región Metropolitana">
      <Eje
        escala={x}
        lado="abajo"
        ancho={ANCHO}
        alto={ALTO}
        {margen}
        grilla
        formato={(v) => numero(v as number, 1)}
        factor={factorTexto}
      />
      <Eje escala={y} lado="izquierda" ancho={ANCHO} alto={ALTO} {margen} factor={factorTexto} />

      {#each ordenados as d, i (d.region)}
        {@const valorX = x(d.doctoradosPor1000) + 8}
        {@const valorY = (y(d.region) ?? 0) + y.bandwidth() / 2}
        <g
          class="barra"
          class:atenuada={activa !== null && activa.region !== d.region}
          role="graphics-symbol"
          tabindex="0"
          aria-label="{d.region}: {numero(d.doctoradosPor1000, 1)} doctorados trabajando cada 1.000 trabajadores"
          onmouseenter={() => mostrar(d)}
          onmouseleave={ocultar}
          onfocus={() => mostrar(d)}
          onblur={ocultar}
        >
          <rect
            class="rect"
            class:oculta={estadoRevelado === 'oculto'}
            style="transition-delay: {i * 45}ms"
            x={margen.left}
            y={y(d.region)}
            width={Math.max(0, x(d.doctoradosPor1000) - margen.left)}
            height={y.bandwidth()}
            fill={colores[i]}
          />
          <!-- Compensación de escala: ver Eje.svelte/Anotacion.svelte, mismo patrón. -->
          <g transform="translate({valorX} {valorY}) scale({factorTexto}) translate({-valorX} {-valorY})">
            <text class="etiqueta-valor" x={valorX} y={valorY} dominant-baseline="middle"
              >{numero(d.doctoradosPor1000, 1)}</text
            >
          </g>
        </g>
      {/each}
    </svg>

    <Tooltip
      visible={activa !== null}
      x={posicionTooltip.x}
      y={posicionTooltip.y}
      anchoContenedor={lienzo?.clientWidth ?? 0}
      altoContenedor={lienzo?.clientHeight ?? 0}
    >
      {#if activa}
        <strong>{activa.region}</strong><br />
        {numero(activa.doctoradosPor1000, 1)} doctorados/1.000 trabajadores<br />
        {numero(activa.investigadores)} investigadores · {activa.universidades} universidades
      {/if}
    </Tooltip>
  </div>

  {#snippet tabla()}
    <TablaEquivalente
      datos={ordenados}
      resumen="Doctorados trabajando por cada 1.000 trabajadores, universidades e investigadores, por región, ordenadas de mayor a menor tasa."
      columnas={[
        { llave: 'region', titulo: 'Región' },
        {
          llave: 'doctoradosPor1000',
          titulo: 'Doctorados/1.000 trab.',
          numerica: true,
          formato: (v) => numero(v as number, 1),
        },
        { llave: 'investigadores', titulo: 'Investigadores', numerica: true, formato: (v) => numero(v as number) },
        { llave: 'universidades', titulo: 'Universidades', numerica: true, formato: (v) => numero(v as number) },
      ]}
    />
  {/snippet}
</Figura>

<style>
  .lienzo {
    position: relative;
  }

  .etiqueta-valor {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-2xs);
    font-variant-numeric: tabular-nums;
    fill: var(--color-tinta);
  }

  .barra {
    transition: opacity var(--duracion-rapida) var(--curva-salida);
  }

  .barra rect {
    transition: fill var(--duracion-media) var(--curva-salida);
  }

  .atenuada {
    opacity: 0.45;
  }

  .barra:focus-visible {
    outline: none;
  }

  .barra:focus-visible rect {
    stroke: var(--color-enzima);
    stroke-width: 3;
    paint-order: stroke;
  }

  /* Momento de deleite: entrada en cascada, de mayor a menor. */
  .rect {
    transform-box: fill-box;
    transform-origin: left center;
    transition: transform 500ms var(--curva-salida);
  }

  .rect.oculta {
    transform: scaleX(0);
  }

  @media (prefers-reduced-motion: reduce) {
    .barra,
    .barra rect,
    .rect {
      transition: none;
    }
  }
</style>
