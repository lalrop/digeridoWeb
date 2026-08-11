<!--
  Pictograma.svelte — grilla de figuras humanas (isotype) para cifras sobre
  personas.

  digerido.cl toma como referencia www.pudding.cool: un gráfico de barras
  nunca es el único recurso posible cuando el dato ES gente (personas
  desempleadas, afiliadas, afectadas). Un icon array donde cada figura pesa
  lo mismo y el grupo que importa se resalta comunica una cantidad humana de
  forma más inmediata que una barra — y es el mismo patrón destacado/contexto
  que ya usa `escalaDestacado()`, aplicado a íconos en vez de color de barra.

  Principios de isotype (Neurath): cada ícono representa una cantidad FIJA
  (declarala en la `bajada` o `unidades` de <Figura>: "Cada figura representa
  10.000 personas"). Un resto que no completa un ícono entero se CORTA con un
  clip-path, nunca se estira ni se redondea — es la misma lógica de
  `escalaCategorica()`: no deformar la unidad para que "cierre" visualmente.

  Es una PIEZA, no un gráfico completo: como <Eje> o <Anotacion>, se usa
  dentro del `children` de <Figura>, con su propia <TablaEquivalente> en el
  snippet `tabla`. No importa `d3`: la grilla es aritmética simple, no una
  escala continua.

  Interactivo por diseño, no decorativo: cada ícono es alcanzable con Tab y
  responde a foco igual que a mouse (mismo patrón que las barras de
  FlujoPartidas.svelte) — nunca es una imagen estática.
-->
<script lang="ts">
  import { grafico } from '../utils/escalas.js';

  interface Props {
    /**
     * Cuántos íconos dibujar. Puede ser fraccionario: el último ícono se
     * corta a esa fracción en vez de redondear (§ isotype: no deformar la
     * unidad). Quien usa el componente decide cuánto vale un ícono entero
     * (100 personas, 10.000 personas) y hace la división antes de pasarla acá.
     */
    cantidad: number;
    /**
     * Desde el ícono 0, cuántos —también fraccionario— van en el color
     * destacado. Sin este prop, todos los íconos quedan en `colorContexto`.
     */
    destacados?: number;
    /** Lector de pantalla: el HALLAZGO, no "pictograma de personas" (§8). */
    descripcion: string;
    /** Columnas de la grilla. Por defecto se acerca a un cuadrado. */
    columnas?: number;
    colorDestacado?: string;
    colorContexto?: string;
    /** Ícono resaltado, controlado por quien usa el componente (para
     *  sincronizar con un <Tooltip> externo, igual que en FlujoPartidas). */
    activo?: number | null;
    alActivar?: (i: number) => void;
    alDesactivar?: () => void;
    /** Etiqueta accesible por ícono individual. */
    etiquetaIcono?: (i: number, destacado: boolean) => string;
  }

  let {
    cantidad,
    destacados,
    descripcion,
    columnas,
    colorDestacado = grafico.destacado,
    colorContexto = grafico.contexto,
    activo = null,
    alActivar,
    alDesactivar,
    etiquetaIcono,
  }: Props = $props();

  const ANCHO_ICONO = 10;
  const ALTO_ICONO = 16;
  const ESPACIO = 5;

  const enteros = $derived(Math.max(0, Math.ceil(cantidad)));
  const cols = $derived(Math.max(1, columnas ?? Math.ceil(Math.sqrt(enteros || 1))));
  const filas = $derived(Math.max(1, Math.ceil(enteros / cols)));

  const anchoTotal = $derived(cols * ANCHO_ICONO + (cols - 1) * ESPACIO);
  const altoTotal = $derived(filas * ALTO_ICONO + (filas - 1) * ESPACIO);

  function posicion(i: number): { x: number; y: number } {
    const fila = Math.floor(i / cols);
    const col = i % cols;
    return { x: col * (ANCHO_ICONO + ESPACIO), y: fila * (ALTO_ICONO + ESPACIO) };
  }

  /** Fracción (0–1) de destacado que le toca al ícono `i`. */
  function fraccion(i: number): number {
    if (destacados === undefined) return 0;
    return Math.max(0, Math.min(1, destacados - i));
  }

  function etiqueta(i: number): string {
    if (etiquetaIcono) return etiquetaIcono(i, fraccion(i) > 0);
    return `Figura ${i + 1} de ${enteros}`;
  }

  /** Id único: puede haber más de un Pictograma en la misma página. */
  const idBase = `pictograma-${Math.random().toString(36).slice(2, 9)}`;

  // Demasiadas figuras individuales pesan en el DOM y dejan de leerse como
  // grupo — es el mismo tipo de guardia que MAX_CATEGORICA en escalas.ts.
  $effect(() => {
    if (import.meta.env.DEV && enteros > 200) {
      console.warn(
        `[kit] Pictograma con ${enteros} íconos. Subí el valor que representa cada ` +
          'figura (de a 100, de a 1.000...) en vez de dibujar una por unidad real.',
      );
    }
  });

  /** Silueta simple: cabeza + torso redondeado, en la caja local 10×16. */
  const RUTA_CUERPO =
    'M5 6.6C2.4 6.6 0.8 9 0.8 12.2V16H9.2V12.2C9.2 9 7.6 6.6 5 6.6Z';
</script>

<svg
  viewBox="0 0 {anchoTotal} {altoTotal}"
  role="img"
  aria-label={descripcion}
  class="pictograma"
>
  {#each Array.from({ length: enteros }, (_, i) => i) as i (i)}
    {@const pos = posicion(i)}
    {@const frac = fraccion(i)}
    <!-- svelte-ignore a11y_no_noninteractive_tabindex -- "graphics-symbol" (ARIA
         Graphics Module) es el rol correcto para un punto de datos enfocable;
         el linter de Svelte todavía no lo reconoce como interactivo. -->
    <g
      transform="translate({pos.x} {pos.y})"
      class="icono"
      class:activo={activo === i}
      role="graphics-symbol"
      tabindex="0"
      aria-label={etiqueta(i)}
      onmouseenter={() => alActivar?.(i)}
      onmouseleave={() => alDesactivar?.()}
      onfocus={() => alActivar?.(i)}
      onblur={() => alDesactivar?.()}
    >
      <g fill={colorContexto}>
        <circle cx="5" cy="3" r="2.8" />
        <path d={RUTA_CUERPO} />
      </g>
      {#if frac > 0}
        <clipPath id="{idBase}-{i}">
          <rect x="0" y="0" width={ANCHO_ICONO * frac} height={ALTO_ICONO} />
        </clipPath>
        <g fill={colorDestacado} clip-path="url(#{idBase}-{i})">
          <circle cx="5" cy="3" r="2.8" />
          <path d={RUTA_CUERPO} />
        </g>
      {/if}
    </g>
  {/each}
</svg>

<style>
  .pictograma {
    display: block;
    width: 100%;
    height: auto;
    overflow: visible;
  }

  .icono {
    cursor: pointer;
    transition: opacity var(--duracion-rapida) var(--curva-salida);
  }

  .icono:focus-visible {
    outline: none;
  }

  /* Mismo patrón que las barras de FlujoPartidas: el foco se dibuja sobre la
     figura misma, no con el outline por defecto del navegador. */
  .icono:focus-visible :global(circle),
  .icono:focus-visible :global(path) {
    stroke: var(--color-enzima);
    stroke-width: 1.5;
    paint-order: stroke;
  }

  .icono.activo :global(circle),
  .icono.activo :global(path) {
    stroke: var(--color-tinta);
    stroke-width: 1;
    paint-order: stroke;
  }

  @media (prefers-reduced-motion: reduce) {
    .icono {
      transition: none;
    }
  }
</style>
