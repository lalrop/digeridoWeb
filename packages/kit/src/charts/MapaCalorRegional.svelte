<!--
  MapaCalorRegional.svelte — mapa de calor de las 16 regiones de Chile, de
  norte a sur.

  Existe para documentos extensos donde el dato ES geográfico y el propio
  texto invita a la metáfora de un mapa de calor (ver memoria de proceso
  "digerido-documentos-extensos": ampliar el análisis visual en vez de
  comprimirlo cuando el documento lo sostiene). Chile es angosto y muy largo:
  en vez de dibujar el contorno real del país (mantenimiento alto, y la forma
  exacta no aporta nada que el orden norte-sur no aporte ya), esto es una
  tira vertical de bandas — una por región, en su orden geográfico real, que
  quien usa el componente controla pasando `datos` ya ordenado.

  Es una PIEZA, no un gráfico completo: como <Eje> o <Pictograma>, se usa
  dentro del `children` de <Figura>, con su propia <TablaEquivalente> en el
  snippet `tabla` y su propio <Tooltip> posicionado por quien lo usa (mismo
  patrón que <Pictograma> en AccesoEfectivo.svelte).

  Color continuo (`colorSecuencial`), no por escalones: el VALOR en sí es lo
  que se codifica, no un ranking. Nunca es la única señal — cada banda lleva
  el nombre de la región y el valor formateado como texto directo (§8).

  Compensación de escala de texto: mismo patrón que Eje.svelte/Anotacion.svelte
  (ver packages/kit/src/utils/redimension o interaccion.ts) — recibe un
  `factor` de quien lo usa, medido con `observarAncho` sobre el contenedor
  real.
-->
<script module lang="ts">
  /** Geometría de cada banda, exportada para que quien posicione un
   * <Tooltip> externo (igual patrón que Pictograma/AccesoEfectivo) calcule
   * la misma coordenada sin duplicar los números a mano. */
  export const ALTO_BANDA = 30;
  export const ESPACIO_BANDA = 4;
</script>

<script lang="ts">
  import { colorSecuencial } from '../utils/escalas.js';

  interface Fila {
    region: string;
    valor: number;
  }

  interface Props {
    /** En orden geográfico real (norte a sur) — este componente no reordena. */
    datos: Fila[];
    /** Formatea el valor mostrado en cada banda y en el aria-label. */
    formato: (valor: number) => string;
    /** Ícono resaltado, controlado por quien usa el componente (para
     *  sincronizar con un <Tooltip> externo, igual que en Pictograma). */
    activo?: number | null;
    alActivar?: (i: number) => void;
    alDesactivar?: () => void;
    /** Etiqueta accesible por banda; por defecto "Región: valor". */
    etiquetaAria?: (fila: Fila) => string;
    /** Compensación de escala de texto (ver comentario arriba). */
    factor?: number;
  }

  let {
    datos, formato, activo = null, alActivar, alDesactivar, etiquetaAria, factor = 1,
  }: Props = $props();

  const ANCHO = 720;
  const MARGEN_INLINE = 4;

  const altoTotal = $derived(datos.length * (ALTO_BANDA + ESPACIO_BANDA) - ESPACIO_BANDA);

  const minimo = $derived(Math.min(...datos.map((d) => d.valor)));
  const maximo = $derived(Math.max(...datos.map((d) => d.valor)));

  function y(i: number): number {
    return i * (ALTO_BANDA + ESPACIO_BANDA);
  }

  function etiqueta(fila: Fila): string {
    return etiquetaAria ? etiquetaAria(fila) : `${fila.region}: ${formato(fila.valor)}`;
  }
</script>

<svg
  viewBox="0 0 {ANCHO} {altoTotal}"
  role="img"
  aria-label="Mapa de calor por región, de norte a sur"
  class="mapa-calor"
>
  {#each datos as fila, i (fila.region)}
    {@const banda = y(i)}
    {@const colorFondo = colorSecuencial(fila.valor, minimo, maximo)}
    {@const centroY = banda + ALTO_BANDA / 2}
    <!-- svelte-ignore a11y_no_noninteractive_tabindex -- "graphics-symbol" (ARIA
         Graphics Module) es el rol correcto para un punto de datos enfocable. -->
    <g
      class="banda"
      class:activa={activo === i}
      role="graphics-symbol"
      tabindex="0"
      aria-label={etiqueta(fila)}
      onmouseenter={() => alActivar?.(i)}
      onmouseleave={() => alDesactivar?.()}
      onfocus={() => alActivar?.(i)}
      onblur={() => alDesactivar?.()}
    >
      <rect
        x={MARGEN_INLINE}
        y={banda}
        width={ANCHO - MARGEN_INLINE * 2}
        height={ALTO_BANDA}
        fill={colorFondo}
      />
      <g
        transform="translate({ANCHO / 2} {centroY}) scale({factor}) translate({-ANCHO / 2} {-centroY})"
      >
        <text class="etiqueta-region" x={MARGEN_INLINE + 12} y={centroY} dominant-baseline="middle"
          >{fila.region}</text
        >
        <text
          class="etiqueta-valor"
          x={ANCHO - MARGEN_INLINE - 12}
          y={centroY}
          text-anchor="end"
          dominant-baseline="middle">{formato(fila.valor)}</text
        >
      </g>
    </g>
  {/each}
</svg>

<style>
  .mapa-calor {
    display: block;
    width: 100%;
    height: auto;
    overflow: visible;
  }

  .banda {
    cursor: pointer;
  }

  .banda rect {
    transition: stroke-width var(--duracion-rapida) var(--curva-salida);
  }

  .banda:focus-visible {
    outline: none;
  }

  .banda:focus-visible rect,
  .banda.activa rect {
    stroke: var(--color-enzima);
    stroke-width: 3;
    paint-order: stroke;
  }

  .etiqueta-region,
  .etiqueta-valor {
    font-family: var(--fuente-utilidad);
    font-variant-numeric: tabular-nums;
    /* Halo de papel: legible sobre cualquier banda, clara u oscura, sin caja
       que tape el color — mismo recurso que Anotacion.svelte. */
    paint-order: stroke;
    stroke: var(--color-papel);
    stroke-width: 3.5px;
    stroke-linejoin: round;
  }

  .etiqueta-region {
    font-size: var(--tipo-xs);
    font-weight: var(--peso-media);
    fill: var(--color-tinta);
  }

  .etiqueta-valor {
    font-size: var(--tipo-xs);
    fill: var(--color-tinta);
  }

  @media (prefers-reduced-motion: reduce) {
    .banda rect {
      transition: none;
    }
  }
</style>
