<!--
  CostoTef.svelte — el gráfico principal de esta pieza.

  · D3 calcula (escalas + generador de línea), Svelte renderiza.
  · Un destacado ("Iniciador de Pagos 1", la serie del hallazgo) y el resto en
    contexto — "un solo destacado por gráfico" (packages/tokens/src/color.ts).
    El contraste con "Banco 1" (la línea más barata y más plana) se cuenta con
    una anotación de texto, no con un segundo color.
  · Las 5 series se identifican con una LEYENDA en HTML normal (no texto SVG):
    en un `viewBox` que se achica a lo ancho de la pantalla, el texto SVG se
    encoge junto con el dibujo y en un celular queda ilegible. Nombre de
    proveedor + color en DOM aparte, a tamaño de letra real, resuelve eso y
    además libera margen izquierdo para que el gráfico se vea más grande.
  · Los 15 puntos son focuseables: son pocos (menos que los 42 de un solo mes
    en la pieza del IPN), y acá cada uno es un dato real de la tabla I.2, no
    un punto de una serie continua.
-->
<script lang="ts">
  import { max } from 'd3-array';
  import { scaleLinear, scalePoint } from 'd3-scale';
  import { line as lineaD3 } from 'd3-shape';

  import Anotacion from '@digerido/kit/charts/Anotacion.svelte';
  import Eje from '@digerido/kit/charts/Eje.svelte';
  import Figura from '@digerido/kit/charts/Figura.svelte';
  import TablaEquivalente from '@digerido/kit/charts/TablaEquivalente.svelte';
  import Tooltip from '@digerido/kit/charts/Tooltip.svelte';
  import { formatoCLP, grafico, porcentaje } from '@digerido/kit/utils';

  interface Fila {
    entidad: string;
    monto: number;
    porcentaje: number;
  }

  interface Props {
    datos: Fila[];
    /** Paso activo dentro de un Scrolly (0, 1 o 2). Por defecto 2: fuera del
     * scrollytelling el gráfico se muestra ya revelado del todo. */
    paso?: number;
  }

  let { datos, paso = 2 }: Props = $props();

  const ENTIDAD_DESTACADA = 'Iniciador de Pagos 1';
  const MONTOS = [1000, 20000, 50000];

  const ANCHO = 720;
  const ALTO = 420;
  // Sin etiquetas de texto dentro del SVG, el margen izquierdo solo necesita
  // espacio para los números del eje Y — mucho menos que para 5 nombres de
  // proveedor, así que el área de trazo queda bastante más ancha.
  const margen = { top: 24, right: 24, bottom: 32, left: 56 };

  const entidades = $derived([...new Set(datos.map((d) => d.entidad))]);

  function serieDe(entidad: string): Fila[] {
    return MONTOS.map((monto) => datos.find((d) => d.entidad === entidad && d.monto === monto)).filter(
      (d): d is Fila => d !== undefined,
    );
  }

  // ── D3 calcula ────────────────────────────────────────────────────────────
  const x = $derived(scalePoint(MONTOS, [margen.left, ANCHO - margen.right]).padding(0.5));

  const y = $derived(
    scaleLinear()
      .domain([0, max(datos, (d) => d.porcentaje) ?? 0])
      .nice()
      .range([ALTO - margen.bottom, margen.top]),
  );

  const generador = $derived(
    lineaD3<Fila>()
      .x((d) => x(d.monto) ?? 0)
      .y((d) => y(d.porcentaje)),
  );

  function colorDe(entidad: string): string {
    return paso >= 1 && entidad === ENTIDAD_DESTACADA ? grafico.destacado : grafico.contexto;
  }

  const puntoDestacado1000 = $derived(
    datos.find((d) => d.entidad === ENTIDAD_DESTACADA && d.monto === 1000),
  );
  const puntoBanco50000 = $derived(datos.find((d) => d.entidad === 'Banco 1' && d.monto === 50000));

  // ── Estado del tooltip ────────────────────────────────────────────────────
  let activo = $state<Fila | null>(null);
  let lienzo = $state<HTMLDivElement | null>(null);

  function mostrar(d: Fila) {
    activo = d;
  }
  const ocultar = () => (activo = null);

  const factor = $derived((lienzo?.clientWidth ?? ANCHO) / ANCHO);
  const posicionTooltip = $derived(
    activo ? { x: (x(activo.monto) ?? 0) * factor, y: y(activo.porcentaje) * factor } : { x: 0, y: 0 },
  );
</script>

<Figura
  id="costo-tef"
  titulo="Un proveedor cobra hasta 42% por aceptar un pago chico con transferencia"
  descripcion="Aceptar un pago de $1.000 por transferencia (TEF) cuesta 42,1% del monto con Iniciador de Pagos 1, contra 1% con Banco 1; la brecha entre proveedores casi desaparece en pagos de $50.000."
  unidades="% del monto pagado"
  fuente="Banco Central de Chile, Informe de Sistemas de Pago, agosto 2026 (Tabla I.2)"
  sangria="ancho"
>
  <div class="lienzo" bind:this={lienzo}>
    <svg
      viewBox="0 0 {ANCHO} {ALTO}"
      role="img"
      aria-label="Aceptar un pago de $1.000 por transferencia cuesta 42,1% del monto con Iniciador de Pagos 1, muy por encima del 1% que cobra Banco 1; con pagos de $50.000 la diferencia entre proveedores casi desaparece"
    >
      <Eje escala={y} lado="izquierda" ancho={ANCHO} alto={ALTO} {margen} grilla marcas={5} formato={(v) => porcentaje(v as number, 0)} />
      <Eje escala={x} lado="abajo" ancho={ANCHO} alto={ALTO} {margen} formato={(v) => formatoCLP(v as number)} />

      {#each entidades as entidad (entidad)}
        {@const serie = serieDe(entidad)}
        <path
          d={generador(serie) ?? ''}
          class="linea"
          class:linea--destacada={colorDe(entidad) === grafico.destacado}
          style:stroke={colorDe(entidad)}
        />
      {/each}

      {#each datos as d (d.entidad + d.monto)}
        <g
          class="punto"
          role="graphics-symbol"
          tabindex="0"
          aria-label="{d.entidad}, pago de {formatoCLP(d.monto)}: {porcentaje(d.porcentaje)} del monto"
          onmouseenter={() => mostrar(d)}
          onmouseleave={ocultar}
          onfocus={() => mostrar(d)}
          onblur={ocultar}
        >
          <circle
            cx={x(d.monto) ?? 0}
            cy={y(d.porcentaje)}
            r={activo === d ? 7 : 4.5}
            fill={colorDe(d.entidad)}
          />
        </g>
      {/each}

      {#if paso >= 1 && puntoDestacado1000}
        <Anotacion
          x={x(puntoDestacado1000.monto) ?? 0}
          y={y(puntoDestacado1000.porcentaje)}
          dx={14}
          dy={-16}
          ancho={150}
          texto="42,1% de la venta se va en la comisión"
          enfasis
        />
      {/if}

      {#if paso >= 2 && puntoBanco50000}
        <Anotacion
          x={x(puntoBanco50000.monto) ?? 0}
          y={y(puntoBanco50000.porcentaje)}
          dx={-90}
          dy={24}
          ancho={140}
          alinear="fin"
          texto="Banco 1 cobra siempre 1%, sin importar el monto"
        />
      {/if}
    </svg>

    <Tooltip
      visible={activo !== null}
      x={posicionTooltip.x}
      y={posicionTooltip.y}
      anchoContenedor={lienzo?.clientWidth ?? 0}
      altoContenedor={lienzo?.clientHeight ?? 0}
    >
      {#if activo}
        <strong>{activo.entidad}</strong><br />
        Pago de {formatoCLP(activo.monto)}: {porcentaje(activo.porcentaje)}
      {/if}
    </Tooltip>
  </div>

  <!-- Leyenda en HTML normal: nombre + color, a tamaño de letra real (§8). -->
  <ul class="leyenda">
    {#each entidades as entidad (entidad)}
      <li class:leyenda__item--destacada={colorDe(entidad) === grafico.destacado}>
        <span class="leyenda__punto" style:background={colorDe(entidad)}></span>
        {entidad}
      </li>
    {/each}
  </ul>

  {#snippet tabla()}
    <TablaEquivalente
      datos={[...datos].sort((a, b) => a.entidad.localeCompare(b.entidad) || a.monto - b.monto)}
      resumen="Costo de aceptar un pago por transferencia (TEF), como % del monto, por proveedor y monto pagado."
      columnas={[
        { llave: 'entidad', titulo: 'Proveedor' },
        { llave: 'monto', titulo: 'Monto', numerica: true, formato: (v) => formatoCLP(v as number) },
        {
          llave: 'porcentaje',
          titulo: 'Costo',
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

  .linea {
    fill: none;
    stroke-width: 2.5;
    transition: stroke var(--duracion-media) var(--curva-salida);
  }

  .linea--destacada {
    stroke-width: 3.5;
  }

  .leyenda {
    display: flex;
    flex-wrap: wrap;
    gap: var(--espacio-xs) var(--espacio-md);
    list-style: none;
    margin: var(--espacio-sm) 0 0;
    padding: 0;
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-xs);
    color: var(--color-tinta-suave);
  }

  .leyenda li {
    display: inline-flex;
    align-items: center;
    gap: var(--espacio-2xs);
    transition: color var(--duracion-media) var(--curva-salida);
  }

  .leyenda__item--destacada {
    color: var(--color-tinta);
    font-weight: var(--peso-media);
  }

  .leyenda__punto {
    width: 0.7em;
    height: 0.7em;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .punto {
    cursor: pointer;
  }

  .punto circle {
    transition:
      r var(--duracion-rapida) var(--curva-salida),
      fill var(--duracion-media) var(--curva-salida);
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
    .leyenda li,
    .punto circle {
      transition: none;
    }
  }
</style>
