<!--
  ExpectativasInflacion.svelte — el gráfico principal de esta pieza.

  · D3 calcula (escalas + generador de línea), Svelte renderiza.
  · Solo los módulos de d3 que se usan, nunca `d3` completo.
  · Un destacado (24 meses, la serie del hallazgo) y el resto en contexto (12
    meses): la interactividad punto a punto vive solo en la serie destacada —
    con 42 meses por serie, hacer las dos completamente focuseables duplica el
    recorrido de teclado sin agregar nada al argumento.
  · Anotación como contenido: marca el mínimo histórico y el repunte, no son
    adorno.
  · Tabla equivalente desde LOS MISMOS datos.
-->
<script lang="ts">
  import { max } from 'd3-array';
  import { scaleLinear, scaleTime } from 'd3-scale';
  import { line as lineaD3 } from 'd3-shape';

  import Anotacion from '@digerido/kit/charts/Anotacion.svelte';
  import Eje from '@digerido/kit/charts/Eje.svelte';
  import Figura from '@digerido/kit/charts/Figura.svelte';
  import TablaEquivalente from '@digerido/kit/charts/TablaEquivalente.svelte';
  import Tooltip from '@digerido/kit/charts/Tooltip.svelte';
  import { formatoMesAno, grafico, numero, observarAncho, porcentaje } from '@digerido/kit/utils';

  interface Fila {
    horizonte: '12 meses' | '24 meses';
    periodo: string; // "YYYY-MM"
    media: number;
    mediana: number;
  }

  interface Props {
    datos: Fila[];
    /**
     * Paso activo dentro de un Scrolly (0, 1 o 2). Por defecto 2: fuera del
     * scrollytelling el gráfico se muestra ya revelado del todo, con las dos
     * anotaciones puestas — igual que FlujoPartidas con su `paso` por defecto.
     */
    paso?: number;
  }

  let { datos, paso = 2 }: Props = $props();

  const ANCHO = 720;
  const ALTO = 380;
  const margen = { top: 28, right: 84, bottom: 32, left: 40 };

  function parsePeriodo(periodo: string): Date {
    const [anio, mes] = periodo.split('-').map(Number);
    return new Date(Date.UTC(anio!, mes! - 1, 1));
  }

  const serie24 = $derived(
    datos.filter((d) => d.horizonte === '24 meses').sort((a, b) => a.periodo.localeCompare(b.periodo)),
  );
  const serie12 = $derived(
    datos.filter((d) => d.horizonte === '12 meses').sort((a, b) => a.periodo.localeCompare(b.periodo)),
  );

  // ── D3 calcula ────────────────────────────────────────────────────────────
  const x = $derived(
    scaleTime()
      .domain([parsePeriodo(datos[0]?.periodo ?? '2023-01'), parsePeriodo(datos.at(-1)?.periodo ?? '2026-06')])
      .range([margen.left, ANCHO - margen.right]),
  );

  const y = $derived(
    scaleLinear()
      .domain([0, max([...serie24, ...serie12], (d) => d.mediana) ?? 10])
      .nice()
      .range([ALTO - margen.bottom, margen.top]),
  );

  const generador = $derived(
    lineaD3<Fila>()
      .x((d) => x(parsePeriodo(d.periodo)))
      .y((d) => y(d.mediana)),
  );

  const trazo24 = $derived(generador(serie24) ?? '');
  const trazo12 = $derived(generador(serie12) ?? '');

  const colorDestacado = $derived(paso >= 1 ? grafico.destacado : grafico.contexto);

  /** El mínimo histórico de la serie a 24 meses: febrero de 2026. */
  const minimo24 = $derived(
    serie24.reduce((m, d) => (d.mediana < m.mediana ? d : m), serie24[0] ?? { periodo: '', mediana: 0 }),
  );
  const mayo26 = $derived(serie24.find((d) => d.periodo === '2026-05'));

  // ── Estado del tooltip (solo la serie destacada) ────────────────────────────
  let activo = $state<Fila | null>(null);
  let lienzo = $state<HTMLDivElement | null>(null);

  function mostrar(d: Fila) {
    activo = d;
  }
  const ocultar = () => (activo = null);

  // Ancho real del contenedor, medido en vivo: alimenta el factor de posición
  // del tooltip y el de compensación de texto de Eje/Anotacion/las etiquetas
  // de serie (§ "el SVG se encoge en móvil").
  let anchoLienzo = $state(ANCHO);
  const factor = $derived(anchoLienzo / ANCHO);
  const factorTexto = $derived(ANCHO / Math.max(1, anchoLienzo));
  const posicion = $derived(
    activo
      ? { x: x(parsePeriodo(activo.periodo)) * factor, y: y(activo.mediana) * factor }
      : { x: 0, y: 0 },
  );

  // Posición de las etiquetas de serie ("12 meses"/"24 meses"), al final de
  // cada línea. Derivadas acá (no `{@const}` en el markup) porque las usa a
  // la vez el `<g>` de compensación de escala y el `<text>` que envuelve.
  const etiquetaX = $derived(ANCHO - margen.right + 6);
  const etiqueta12 = $derived({ x: etiquetaX, y: y(serie12.at(-1)?.mediana ?? 0) });
  const etiqueta24 = $derived({ x: etiquetaX, y: y(serie24.at(-1)?.mediana ?? 0) });
</script>

<Figura
  id="expectativas-inflacion"
  titulo="La inflación esperada a dos años tocó su mínimo y rebotó en cuatro meses"
  descripcion="La mediana de las expectativas de inflación a 24 meses cayó a 3% en febrero de 2026 —el mínimo de toda la serie— y subió a 3,5% en mayo, nivel que se repitió en junio."
  unidades="% (mediana EDEP, mensual)"
  fuente="Banco Central de Chile, Encuesta de Determinantes y Expectativas de Precios (EDEP), Excel adjunto al IPN de agosto 2026"
  sangria="ancho"
>
  <div class="lienzo" bind:this={lienzo} use:observarAncho={(a) => (anchoLienzo = a)}>
    <svg
      viewBox="0 0 {ANCHO} {ALTO}"
      role="img"
      aria-label="La mediana de expectativas de inflación a 24 meses tocó su mínimo histórico (3%) en febrero de 2026 y subió a 3,5% en mayo, repitiéndose en junio"
    >
      <Eje escala={y} lado="izquierda" ancho={ANCHO} alto={ALTO} {margen} grilla marcas={4} formato={(v) => porcentaje(v as number, 0)} factor={factorTexto} />
      <Eje escala={x} lado="abajo" ancho={ANCHO} alto={ALTO} {margen} marcas={4} factor={factorTexto} />

      <!-- Serie de contexto: 12 meses. Sin marcadores por punto (§ arriba). -->
      <path d={trazo12} class="linea linea--contexto" />
      <!-- Compensación de escala: ver Eje.svelte/Anotacion.svelte, mismo patrón. -->
      <g
        transform="translate({etiqueta12.x} {etiqueta12.y}) scale({factorTexto}) translate({-etiqueta12.x} {-etiqueta12.y})"
      >
        <text class="etiqueta-linea" x={etiqueta12.x} y={etiqueta12.y} dominant-baseline="middle"
          >12 meses</text
        >
      </g>

      <!-- Serie destacada: 24 meses — la del hallazgo. -->
      <path d={trazo24} class="linea linea--destacada" style:stroke={colorDestacado} />
      <g
        transform="translate({etiqueta24.x} {etiqueta24.y}) scale({factorTexto}) translate({-etiqueta24.x} {-etiqueta24.y})"
      >
        <text
          class="etiqueta-linea etiqueta-linea--destacada"
          x={etiqueta24.x}
          y={etiqueta24.y}
          dominant-baseline="middle"
          style:fill={colorDestacado}>24 meses</text
        >
      </g>

      {#each serie24 as d (d.periodo)}
        <g
          class="punto"
          role="graphics-symbol"
          tabindex="0"
          aria-label="{formatoMesAno(parsePeriodo(d.periodo))}: mediana {numero(d.mediana, 1)}%, media {numero(d.media, 1)}%"
          onmouseenter={() => mostrar(d)}
          onmouseleave={ocultar}
          onfocus={() => mostrar(d)}
          onblur={ocultar}
        >
          <circle
            cx={x(parsePeriodo(d.periodo))}
            cy={y(d.mediana)}
            r={activo === d ? 5 : 2.5}
            fill={colorDestacado}
          />
        </g>
      {/each}

      {#if paso >= 1 && minimo24.periodo}
        <Anotacion
          x={x(parsePeriodo(minimo24.periodo))}
          y={y(minimo24.mediana)}
          dx={-8}
          dy={30}
          ancho={140}
          alinear="fin"
          texto="Mínimo histórico: {numero(minimo24.mediana, 0)}% (feb. 2026)"
          factor={factorTexto}
        />
      {/if}

      {#if paso >= 2 && mayo26}
        <Anotacion
          x={x(parsePeriodo(mayo26.periodo))}
          y={y(mayo26.mediana)}
          dx={-140}
          dy={-30}
          ancho={150}
          texto="Repunte a 3,5% tras el shock de costos"
          enfasis
          factor={factorTexto}
        />
      {/if}
    </svg>

    <Tooltip
      visible={activo !== null}
      x={posicion.x}
      y={posicion.y}
      anchoContenedor={lienzo?.clientWidth ?? 0}
      altoContenedor={lienzo?.clientHeight ?? 0}
    >
      {#if activo}
        <strong>{formatoMesAno(parsePeriodo(activo.periodo))}</strong><br />
        Mediana: {numero(activo.mediana, 1)}%<br />
        Media: {numero(activo.media, 1)}%
      {/if}
    </Tooltip>
  </div>

  {#snippet tabla()}
    <TablaEquivalente
      datos={[...serie24].reverse()}
      resumen="Mediana y media mensual de expectativas de inflación a 24 meses (EDEP), desde el mes más reciente."
      columnas={[
        { llave: 'periodo', titulo: 'Mes' },
        { llave: 'mediana', titulo: 'Mediana', numerica: true, formato: (v) => porcentaje(v as number) },
        { llave: 'media', titulo: 'Media', numerica: true, formato: (v) => porcentaje(v as number) },
      ]}
    />
  {/snippet}
</Figura>

<style>
  .lienzo {
    position: relative;
  }

  .linea {
    fill: none;
    stroke-width: 2;
    transition: stroke var(--duracion-media) var(--curva-salida);
  }

  .linea--contexto {
    stroke: var(--color-borde);
  }

  .etiqueta-linea {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-2xs);
    fill: var(--color-tinta-suave);
  }

  .etiqueta-linea--destacada {
    font-weight: var(--peso-media);
  }

  .punto {
    cursor: pointer;
  }

  .punto circle {
    transition: r var(--duracion-rapida) var(--curva-salida);
  }

  .punto:focus-visible {
    outline: none;
  }

  .punto:focus-visible circle {
    stroke: var(--color-enzima);
    stroke-width: 2;
    paint-order: stroke;
  }

  @media (prefers-reduced-motion: reduce) {
    .linea,
    .punto circle {
      transition: none;
    }
  }
</style>
