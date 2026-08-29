<!--
  FlujoPartidas.svelte — el gráfico principal de la pieza de ejemplo.

  Existe como referencia ejecutable del patrón canónico del plan:

    · D3 calcula (escalas), Svelte renderiza. Sin select, append ni enter/exit.
    · Solo los módulos de d3 que se usan, nunca `d3` completo.
    · Un destacado y el resto en contexto: más legible que N colores, y sin tope.
    · Anotación como contenido, no como adorno.
    · Tooltip accesible por teclado, no solo por mouse.
    · Tabla equivalente desde LOS MISMOS datos.

  Vive en la carpeta de la digestión porque es exclusivo de esta pieza (§3). Si
  un segundo artículo lo necesitara, sube a packages/kit (§13).
-->
<script lang="ts">
  import { max } from 'd3-array';
  import { scaleBand, scaleLinear } from 'd3-scale';

  import Anotacion from '@digerido/kit/charts/Anotacion.svelte';
  import Eje from '@digerido/kit/charts/Eje.svelte';
  import Figura from '@digerido/kit/charts/Figura.svelte';
  import TablaEquivalente from '@digerido/kit/charts/TablaEquivalente.svelte';
  import Tooltip from '@digerido/kit/charts/Tooltip.svelte';
  import { delta, formatoCLP, grafico, numero, observarAncho } from '@digerido/kit/utils';

  interface Partida {
    partida: string;
    monto: number;
    variacion: number;
    destacado: boolean;
  }

  interface Props {
    datos: Partida[];
    unidad: string;
    /**
     * Paso activo dentro de un Scrolly.
     *
     * Por defecto 1, no 0: fuera del scrollytelling el gráfico se muestra solo
     * y tiene que sostener su propio título ("Salud concentra un tercio del
     * aumento"). Con paso 0 todas las barras son contexto y el título afirma
     * algo que el gráfico no muestra. El Scrolly pasa 0 explícitamente para su
     * apertura neutra.
     */
    paso?: number;
  }

  let { datos, unidad, paso = 1 }: Props = $props();

  const ANCHO = 720;
  const ALTO = 420;

  /**
   * El margen izquierdo se calcula desde la etiqueta más larga en vez de fijarse
   * a ojo: con 132 px, "Trabajo y Previsión" quedaba recortada. Un eje de
   * categorías se rompe con el primer dataset cuyos nombres son más largos que
   * los del que se usó para elegir el número.
   *
   * 6,4 px por carácter es el ancho medio de IBM Plex Mono a `--tipo-2xs`.
   */
  const ANCHO_CARACTER = 6.4;
  const margen = $derived({
    top: 28,
    right: 90,
    bottom: 44,
    left: Math.max(
      64,
      Math.ceil(Math.max(...datos.map((d) => d.partida.length)) * ANCHO_CARACTER) + 16,
    ),
  });

  // ── D3 calcula ────────────────────────────────────────────────────────────
  const x = $derived(
    scaleLinear()
      .domain([0, max(datos, (d) => d.monto) ?? 0])
      .nice()
      .range([margen.left, ANCHO - margen.right]),
  );

  const y = $derived(
    scaleBand()
      .domain(datos.map((d) => d.partida))
      .range([margen.top, ALTO - margen.bottom])
      .padding(0.24),
  );

  /**
   * El color depende del paso del scrollytelling: al principio todo es contexto
   * y solo en el paso 1 aparece el destacado. El gráfico igual se entiende
   * detenido en cualquier paso (§6.1).
   */
  function color(d: Partida): string {
    if (paso === 0) return grafico.contexto;
    if (paso >= 2 && d.variacion < 0) return grafico.divergente[1]!;
    return d.destacado ? grafico.destacado : grafico.contexto;
  }

  // ── Estado del tooltip ────────────────────────────────────────────────────
  let activa = $state<Partida | null>(null);
  let posicion = $state({ x: 0, y: 0 });

  /**
   * Coordenadas del SVG a px del contenedor. El SVG escala con `width: 100%`,
   * así que hay que convertir por el factor real de render — si no, el tooltip
   * se desalinea en cuanto la pantalla no mide 720 px.
   */
  let lienzo = $state<HTMLDivElement | null>(null);

  // Ancho real del contenedor, medido en vivo: alimenta el factor de posición
  // del tooltip y el de compensación de texto de Eje/Anotacion/`.valor`
  // (§ "el SVG se encoge en móvil").
  let anchoLienzo = $state(ANCHO);
  const factorTexto = $derived(ANCHO / Math.max(1, anchoLienzo));

  function mostrar(d: Partida) {
    activa = d;
    const factor = anchoLienzo / ANCHO;
    posicion = {
      x: x(d.monto) * factor,
      y: ((y(d.partida) ?? 0) + y.bandwidth() / 2) * factor,
    };
  }

  const ocultar = () => (activa = null);

  const anotada = $derived(datos.find((d) => d.destacado));
</script>

<Figura
  id="flujo-partidas"
  titulo="Salud concentra un tercio del aumento"
  descripcion="Salud concentra el 31 % del aumento presupuestario, tres veces más que Educación, la segunda partida que más crece."
  unidades={unidad}
  fuente="Documento sintético de ejemplo — cifras inventadas para probar el sistema"
  bajada="Monto asignado por partida. La variación respecto del año anterior aparece al costado de cada barra."
  nota="Cifras sintéticas: esta figura existe para demostrar el patrón de gráfico, no para informar sobre presupuesto alguno."
>
  <div class="lienzo" bind:this={lienzo} use:observarAncho={(a) => (anchoLienzo = a)}>
    <!--
      `role="img"` con el hallazgo como aria-label (§8). Un lector de pantalla
      recibe la conclusión, no una descripción del tipo de gráfico.
    -->
    <svg
      viewBox="0 0 {ANCHO} {ALTO}"
      role="img"
      aria-label="Salud concentra el 31 % del aumento presupuestario, tres veces más que Educación"
    >
      <Eje
        escala={x}
        lado="abajo"
        ancho={ANCHO}
        alto={ALTO}
        {margen}
        grilla
        marcas={5}
        formato={(v) => numero(v as number)}
        factor={factorTexto}
      />
      <Eje escala={y} lado="izquierda" ancho={ANCHO} alto={ALTO} {margen} factor={factorTexto} />

      {#each datos as d (d.partida)}
        {@const valorX = x(d.monto) + 8}
        {@const valorY = (y(d.partida) ?? 0) + y.bandwidth() / 2}
        <!--
          `tabindex` y los handlers de foco: cada barra es alcanzable con Tab, y
          el tooltip aparece igual que con el mouse. Sin esto, el detalle solo
          existe para quien usa puntero.
        -->
        <g
          class="barra"
          class:atenuada={activa !== null && activa.partida !== d.partida}
          role="graphics-symbol"
          tabindex="0"
          aria-label="{d.partida}: {formatoCLP(d.monto * 1e6, { compacto: true })}, {delta(
            d.variacion,
            1,
            ' %',
          )}"
          onmouseenter={() => mostrar(d)}
          onmouseleave={ocultar}
          onfocus={() => mostrar(d)}
          onblur={ocultar}
        >
          <rect
            x={margen.left}
            y={y(d.partida)}
            width={Math.max(0, x(d.monto) - margen.left)}
            height={y.bandwidth()}
            fill={color(d)}
          />

          <!-- Etiqueta directa al final de la barra: en §8, "forma, posición o
               etiqueta directa como respaldo" del color, nunca solo color.
               Compensación de escala: ver Eje.svelte/Anotacion.svelte. -->
          <g transform="translate({valorX} {valorY}) scale({factorTexto}) translate({-valorX} {-valorY})">
            <text
              class="valor"
              class:negativa={d.variacion < 0}
              x={valorX}
              y={valorY}
              dominant-baseline="middle">{delta(d.variacion, 1, ' %')}</text
            >
          </g>
        </g>
      {/each}

      <!-- La anotación aparece con el paso 1: es el contenido del gráfico. -->
      {#if paso >= 1 && anotada}
        <Anotacion
          x={x(anotada.monto)}
          y={(y(anotada.partida) ?? 0) + y.bandwidth() / 2}
          dx={-150}
          dy={-52}
          ancho={150}
          texto="Tres veces el aumento de Educación"
          enfasis
          factor={factorTexto}
        />
      {/if}
    </svg>

    <Tooltip
      visible={activa !== null}
      x={posicion.x}
      y={posicion.y}
      anchoContenedor={lienzo?.clientWidth ?? 0}
      altoContenedor={lienzo?.clientHeight ?? 0}
    >
      {#if activa}
        <strong>{activa.partida}</strong><br />
        {formatoCLP(activa.monto * 1e6, { compacto: true })}<br />
        <span class:negativa={activa.variacion < 0}>{delta(activa.variacion, 1, ' %')}</span>
        respecto del año anterior
      {/if}
    </Tooltip>
  </div>

  {#snippet tabla()}
    <TablaEquivalente
      {datos}
      resumen="Monto asignado y variación anual por partida, en {unidad}. Cifras sintéticas."
      nota="Los montos están redondeados en el pipeline. «Variación» es el cambio porcentual respecto del año anterior."
      columnas={[
        { llave: 'partida', titulo: 'Partida' },
        {
          llave: 'monto',
          titulo: `Monto (${unidad})`,
          numerica: true,
          formato: (v) => numero(v as number),
        },
        {
          llave: 'variacion',
          titulo: 'Variación',
          numerica: true,
          formato: (v) => delta(v as number, 1, ' %'),
        },
      ]}
    />
  {/snippet}
</Figura>

<style>
  .lienzo {
    position: relative;
  }

  .barra {
    /* La transición es de opacidad y color, nunca de geometría: una barra que
       se estira al pasar el cursor impide comparar longitudes. */
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

  /* El foco se dibuja en la barra misma, con el verde ácido: el outline del
     navegador sobre un <g> de SVG se recorta de formas impredecibles. */
  .barra:focus-visible rect {
    stroke: var(--color-enzima);
    stroke-width: 3;
    paint-order: stroke;
  }

  .valor {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-3xs);
    fill: var(--color-tinta-suave);
    font-variant-numeric: tabular-nums;
  }

  .valor.negativa,
  .negativa {
    fill: var(--color-bilis);
    color: var(--color-bilis);
  }

  @media (prefers-reduced-motion: reduce) {
    .barra,
    .barra rect {
      transition: none;
    }
  }
</style>
