<!--
  CombustiblesDivergente.svelte — gráfico de apoyo, en "Los aperitivos".

  Reemplaza una primera versión con Pictograma: la digestión de la encuesta
  de empleo ya usa ese recurso, y repetirlo en la segunda pieza publicada
  empezaba a sentirse como la única idea del sitio para "hacerlo lúdico".
  Esta es una barra horizontal por categoría, igual de interactiva
  (hover/foco con tooltip), pero con un lenguaje visual distinto: el color
  es divergente (`colorDivergente`, del mismo token que usa el resto del
  kit) y ordena las 5 categorías de la escala de "muy por debajo" a "muy
  por encima" — la sexta, "no tiene un supuesto definido", no pertenece a
  esa escala y se muestra aparte, en gris de "sin dato".

  Es una fotografía (una distribución de respuestas a una pregunta, no una
  secuencia de momentos): hover/clic, sin scrollytelling — mismo criterio
  que en el resto de gráficos de apoyo de esta pieza.

  Momento de deleite: las barras se "llenan" de izquierda a derecha la
  primera vez que el gráfico entra en pantalla — como un medidor de
  combustible, que es justo el tema del gráfico. Progresivo (acción
  `enVista` del kit): sin JS, con `prefers-reduced-motion`, o si ya está
  visible al cargar, se muestra directo en su ancho final.
-->
<script lang="ts">
  import { max } from 'd3-array';
  import { scaleBand, scaleLinear } from 'd3-scale';

  import Anotacion from '@digerido/kit/charts/Anotacion.svelte';
  import Eje from '@digerido/kit/charts/Eje.svelte';
  import Figura from '@digerido/kit/charts/Figura.svelte';
  import TablaEquivalente from '@digerido/kit/charts/TablaEquivalente.svelte';
  import Tooltip from '@digerido/kit/charts/Tooltip.svelte';
  import { colorDivergente, enVista, grafico, observarAncho, porcentaje } from '@digerido/kit/utils';

  interface Fila {
    categoria: string;
    porcentajeEmpresas: number;
  }

  let { datos }: { datos: Fila[] } = $props();

  /** Posición en la escala "por debajo ← similar → por encima". La sexta
   * categoría no tiene lugar en este eje: no está acá, se trata aparte. */
  const POSICION: Record<string, number> = {
    'Muy por debajo': -2,
    'Levemente por debajo': -1,
    'Similar al actual': 0,
    'Levemente por encima': 1,
    'Muy por encima': 2,
  };
  const MAX_POSICION = 2;
  const CATEGORIA_SIN_SUPUESTO = 'No tiene un supuesto definido';

  const escala = $derived(datos.filter((d) => d.categoria !== CATEGORIA_SIN_SUPUESTO));
  const sinSupuesto = $derived(datos.find((d) => d.categoria === CATEGORIA_SIN_SUPUESTO));

  const ANCHO = 720;
  const ALTO_POR_FILA = 44;
  const ALTO = $derived((escala.length + 1) * ALTO_POR_FILA + 60);

  const ANCHO_CARACTER = 6.4;
  const margen = $derived({
    top: 20,
    right: 56,
    bottom: 32,
    left: Math.max(64, Math.ceil(Math.max(...datos.map((d) => d.categoria.length)) * ANCHO_CARACTER) + 16),
  });

  // ── D3 calcula ────────────────────────────────────────────────────────────
  const x = $derived(
    scaleLinear()
      .domain([0, max(datos, (d) => d.porcentajeEmpresas) ?? 0])
      .nice()
      .range([margen.left, ANCHO - margen.right]),
  );

  const y = $derived(
    scaleBand()
      .domain(datos.map((d) => d.categoria))
      .range([margen.top, ALTO - margen.bottom])
      .padding(0.28),
  );

  function color(categoria: string): string {
    if (categoria === CATEGORIA_SIN_SUPUESTO) return grafico.sinDato;
    return colorDivergente(POSICION[categoria] ?? 0, MAX_POSICION);
  }

  // ── Estado del tooltip ────────────────────────────────────────────────────
  let activa = $state<Fila | null>(null);
  let posicionTooltip = $state({ x: 0, y: 0 });
  let lienzo = $state<HTMLDivElement | null>(null);

  // Ancho real del contenedor, medido en vivo: alimenta el factor de posición
  // del tooltip y el de compensación de texto de Eje/Anotacion/`.valor`
  // (§ "el SVG se encoge en móvil").
  let anchoLienzo = $state(ANCHO);
  const factorTexto = $derived(ANCHO / Math.max(1, anchoLienzo));

  function mostrar(d: Fila) {
    activa = d;
    const factor = anchoLienzo / ANCHO;
    posicionTooltip = {
      x: x(d.porcentajeEmpresas) * factor,
      y: ((y(d.categoria) ?? 0) + y.bandwidth() / 2) * factor,
    };
  }
  const ocultar = () => (activa = null);

  // ── Momento de deleite: barras que se llenan como un medidor ────────────
  let estadoRevelado = $state<'oculto' | 'revelado'>('revelado');

  const similar = $derived(datos.find((d) => d.categoria === 'Similar al actual'));

  const notaSinSupuesto = $derived(
    sinSupuesto
      ? `Un ${porcentaje(sinSupuesto.porcentajeEmpresas)} adicional de las empresas no tiene un ` +
        `supuesto definido sobre el precio del combustible (no graficado arriba: no pertenece a ` +
        `la escala "por debajo / por encima").`
      : undefined,
  );
</script>

<Figura
  id="expectativas-combustible"
  titulo="Casi 8 de cada 10 empresas no espera que el combustible baje"
  descripcion="El 78,9% de las empresas encuestadas cree que el precio del combustible se mantendrá igual o subirá en los próximos seis meses; muy pocas apuestan a que baje."
  unidades="% de empresas"
  fuente="Banco Central de Chile, Encuesta de Percepciones de Negocios (EPN), agosto 2026"
  nota={notaSinSupuesto}
  sangria="ancho"
>
  <div
    class="lienzo"
    bind:this={lienzo}
    use:enVista={(estado) => (estadoRevelado = estado)}
    use:observarAncho={(a) => (anchoLienzo = a)}
  >
    <svg
      viewBox="0 0 {ANCHO} {ALTO}"
      role="img"
      aria-label="El 78,9% de las empresas espera que el precio del combustible se mantenga igual o suba en los próximos seis meses"
    >
      <Eje escala={x} lado="abajo" ancho={ANCHO} alto={ALTO} {margen} grilla marcas={4} formato={(v) => porcentaje(v as number, 0)} factor={factorTexto} />
      <Eje escala={y} lado="izquierda" ancho={ANCHO} alto={ALTO} {margen} factor={factorTexto} />

      {#each datos as d, i (d.categoria)}
        {@const valorX = x(d.porcentajeEmpresas) + 8}
        {@const valorY = (y(d.categoria) ?? 0) + y.bandwidth() / 2}
        <g
          class="barra"
          class:atenuada={activa !== null && activa.categoria !== d.categoria}
          role="graphics-symbol"
          tabindex="0"
          aria-label="{d.categoria}: {porcentaje(d.porcentajeEmpresas)}"
          onmouseenter={() => mostrar(d)}
          onmouseleave={ocultar}
          onfocus={() => mostrar(d)}
          onblur={ocultar}
        >
          <rect
            class="rect"
            class:oculta={estadoRevelado === 'oculto'}
            style="transition-delay: {i * 70}ms"
            x={margen.left}
            y={y(d.categoria)}
            width={Math.max(0, x(d.porcentajeEmpresas) - margen.left)}
            height={y.bandwidth()}
            fill={color(d.categoria)}
          />
          <!-- Compensación de escala: ver Eje.svelte/Anotacion.svelte, mismo patrón. -->
          <g transform="translate({valorX} {valorY}) scale({factorTexto}) translate({-valorX} {-valorY})">
            <text class="valor" x={valorX} y={valorY} dominant-baseline="middle"
              >{porcentaje(d.porcentajeEmpresas)}</text
            >
          </g>
        </g>
      {/each}

      {#if similar}
        <Anotacion
          x={x(similar.porcentajeEmpresas)}
          y={(y(similar.categoria) ?? 0) + y.bandwidth() / 2}
          dx={-90}
          dy={-14}
          ancho={160}
          alinear="fin"
          texto="78,9% cree que no bajará: similar o más caro"
          enfasis
          factor={factorTexto}
        />
      {/if}
    </svg>

    <Tooltip
      visible={activa !== null}
      x={posicionTooltip.x}
      y={posicionTooltip.y}
      anchoContenedor={lienzo?.clientWidth ?? 0}
      altoContenedor={lienzo?.clientHeight ?? 0}
    >
      {#if activa}
        <strong>{activa.categoria}</strong><br />
        {porcentaje(activa.porcentajeEmpresas)} de las empresas
      {/if}
    </Tooltip>
  </div>

  {#snippet tabla()}
    <TablaEquivalente
      {datos}
      resumen="Qué supuesto de precio de combustible usa cada empresa para planificar los próximos seis meses, respecto del nivel actual."
      columnas={[
        { llave: 'categoria', titulo: 'Respuesta' },
        {
          llave: 'porcentajeEmpresas',
          titulo: 'Empresas',
          numerica: true,
          formato: (v) => porcentaje(v as number),
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
    transition: opacity var(--duracion-rapida) var(--curva-salida);
  }

  .barra rect {
    transition: fill var(--duracion-media) var(--curva-salida);
  }

  .atenuada {
    opacity: 0.5;
  }

  .barra:focus-visible {
    outline: none;
  }

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

  /* Momento de deleite: la barra "se llena" desde el margen izquierdo, como
     un medidor de combustible. Transform propio en `.rect` (no en `.barra`)
     para no interferir con la transición de `fill` que ya vive ahí. */
  .rect {
    transform-box: fill-box;
    transform-origin: left center;
    transition: transform 550ms var(--curva-salida);
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
