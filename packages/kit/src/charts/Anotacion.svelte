<!--
  Anotacion.svelte — "en data storytelling la anotación ES el contenido" (§2.2).

  Por eso es una primitiva del kit y no un `<text>` suelto en cada gráfico: si
  anotar cuesta, nadie anota, y el gráfico queda mudo.

  Compone tres cosas: el texto, un conector hasta el punto que señala, y un
  fondo que garantiza legibilidad sobre marcas de datos. El fondo se dimensiona
  desde el largo del texto (no se puede medir SVG en build sin layout), así que
  el ancho se declara y el texto se envuelve en líneas.
-->
<script lang="ts">
  interface Props {
    /** Punto anotado, en coordenadas del SVG. */
    x: number;
    y: number;
    /** Texto. Una o dos frases; si necesita tres, es un párrafo del artículo. */
    texto: string;
    /** Desplazamiento de la etiqueta respecto del punto. */
    dx?: number;
    dy?: number;
    /** Ancho de envoltura en px. */
    ancho?: number;
    /** Conector: línea al punto, con o sin punta. */
    conector?: 'linea' | 'ninguno';
    /** Marca el punto anotado con un círculo. */
    punto?: boolean;
    /** Énfasis: usa el color de alerta en vez de la tinta. */
    enfasis?: boolean;
    /** Alineación del texto respecto del ancla. */
    alinear?: 'inicio' | 'fin' | 'centro';
  }

  let {
    x, y, texto, dx = 16, dy = -28, ancho = 180,
    conector = 'linea', punto = true, enfasis = false, alinear = 'inicio',
  }: Props = $props();

  const INTERLINEA = 15;
  /** Ancho medio de carácter en IBM Plex Mono a var(--tipo-2xs) ≈ 6,4 px. */
  const CHAR = 6.4;

  /** Envoltura por palabras: sin medición de texto, se estima por caracteres. */
  const lineas = $derived.by(() => {
    const maxChars = Math.max(8, Math.floor(ancho / CHAR));
    const out: string[] = [];
    let actual = '';
    for (const palabra of texto.split(/\s+/)) {
      const tentativa = actual ? `${actual} ${palabra}` : palabra;
      if (tentativa.length > maxChars && actual) {
        out.push(actual);
        actual = palabra;
      } else {
        actual = tentativa;
      }
    }
    if (actual) out.push(actual);
    return out;
  });

  const anclaTexto = $derived(
    alinear === 'fin' ? 'end' : alinear === 'centro' ? 'middle' : 'start',
  );

  /** El conector termina en el borde de la etiqueta, no en su centro. */
  const finX = $derived(x + dx - (alinear === 'fin' ? -4 : alinear === 'centro' ? 0 : 4));
  const finY = $derived(y + dy + (dy < 0 ? 4 : -4));
</script>

<g class="anotacion" class:anotacion--enfasis={enfasis}>
  {#if conector === 'linea'}
    <line class="conector" x1={x} y1={y} x2={finX} y2={finY} />
  {/if}

  {#if punto}
    <circle class="punto" cx={x} cy={y} r="3.5" />
  {/if}

  <text x={x + dx} y={y + dy} text-anchor={anclaTexto}>
    {#each lineas as linea, i (i)}
      <!--
        `paint-order: stroke` pinta un halo del color del papel detrás de las
        letras: la anotación queda legible incluso encima de una marca oscura,
        sin caja rectangular que tape los datos.
      -->
      <tspan x={x + dx} dy={i === 0 ? 0 : INTERLINEA}>{linea}</tspan>
    {/each}
  </text>
</g>

<style>
  .conector {
    stroke: var(--color-tinta-suave);
    stroke-width: 1;
  }

  .punto {
    fill: none;
    stroke: var(--color-tinta-suave);
    stroke-width: 1.5;
  }

  text {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-2xs);
    line-height: 1.3;
    fill: var(--color-tinta);
    /* Halo de papel: legibilidad sobre cualquier marca, sin caja. */
    paint-order: stroke;
    stroke: var(--color-papel);
    stroke-width: 3.5px;
    stroke-linejoin: round;
  }

  .anotacion--enfasis text {
    fill: var(--color-bilis);
    font-weight: var(--peso-media);
  }

  .anotacion--enfasis .conector,
  .anotacion--enfasis .punto {
    stroke: var(--color-bilis);
  }
</style>
