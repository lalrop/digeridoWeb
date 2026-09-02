<!--
  ConcentracionInvestigadores.svelte — gráfico en "El plato de entrada".

  Mapa de calor de las 16 regiones de Chile (norte a sur), coloreado por
  cantidad de investigadores — la métrica de VOLUMEN que abre la pieza ("6
  de cada 10 investigadores trabajan en la Región Metropolitana"). Es
  deliberadamente distinto del gráfico de "El plato de fondo" (barras de
  doctorados por cada 1.000 trabajadores, la métrica de INTENSIDAD que da
  vuelta la pregunta): dos vistas del mismo dataset, cada una sirviendo a un
  momento distinto del argumento — ver memoria de proceso
  "digerido-documentos-extensos": documentos extensos sostienen más de un
  momento visual sin que se sienta relleno.

  Usa <MapaCalorRegional> del kit (mismo patrón que AccesoEfectivo.svelte
  con <Pictograma>): la pieza dibuja, este componente arma el <Figura>, el
  <Tooltip> y la <TablaEquivalente> alrededor.
-->
<script lang="ts">
  import Figura from '@digerido/kit/charts/Figura.svelte';
  import MapaCalorRegional, {
    ALTO_BANDA,
    ESPACIO_BANDA,
  } from '@digerido/kit/charts/MapaCalorRegional.svelte';
  import TablaEquivalente from '@digerido/kit/charts/TablaEquivalente.svelte';
  import Tooltip from '@digerido/kit/charts/Tooltip.svelte';
  import { numero, observarAncho, porcentaje } from '@digerido/kit/utils';

  interface Fila {
    region: string;
    universidades: number;
    investigadores: number;
    doctoradosPor1000: number;
  }

  let { datos }: { datos: Fila[] } = $props();

  const totalInvestigadores = $derived(datos.reduce((acc, d) => acc + d.investigadores, 0));

  // ── Estado del tooltip ────────────────────────────────────────────────────
  let activo = $state<number | null>(null);
  let lienzo = $state<HTMLDivElement | null>(null);

  // Ancho real del contenedor, medido en vivo: alimenta el factor de posición
  // del tooltip y el de compensación de texto de MapaCalorRegional
  // (§ "el SVG se encoge en móvil").
  let anchoLienzo = $state(720);
  const ANCHO = 720;
  const factorTexto = $derived(ANCHO / Math.max(1, anchoLienzo));

  const posicionTooltip = $derived.by(() => {
    if (activo === null) return { x: 0, y: 0 };
    const factor = anchoLienzo / ANCHO;
    return {
      x: ANCHO * 0.6 * factor,
      y: (activo * (ALTO_BANDA + ESPACIO_BANDA) + ALTO_BANDA / 2) * factor,
    };
  });
</script>

<Figura
  id="concentracion-investigadores"
  titulo="6 de cada 10 investigadores de Chile trabajan en la Región Metropolitana"
  descripcion="La Región Metropolitana concentra 6.139 de los 10.045 investigadores del país (61%), muy por encima de cualquier otra región."
  unidades="Investigadores por región (estimación ANID/CORFO)"
  fuente="Consejo Nacional de CTCI, Estrategia Nacional de Ciencia, Tecnología, Conocimiento e Innovación para el Desarrollo de Chile 2026"
  nota="Cada banda es una región, de norte (arriba) a sur (abajo). El color y el número indican cuántos investigadores trabajan ahí."
>
  <div class="lienzo" bind:this={lienzo} use:observarAncho={(a) => (anchoLienzo = a)}>
    <MapaCalorRegional
      datos={datos.map((d) => ({ region: d.region, valor: d.investigadores }))}
      formato={(v) => numero(v)}
      {activo}
      alActivar={(i) => (activo = i)}
      alDesactivar={() => (activo = null)}
      etiquetaAria={(f) =>
        `${f.region}: ${numero(f.valor)} investigadores, ${porcentaje((f.valor / totalInvestigadores) * 100, 0)} del total del país`}
      factor={factorTexto}
    />

    <Tooltip
      visible={activo !== null}
      x={posicionTooltip.x}
      y={posicionTooltip.y}
      anchoContenedor={lienzo?.clientWidth ?? 0}
      altoContenedor={lienzo?.clientHeight ?? 0}
    >
      {#if activo !== null}
        {@const fila = datos[activo]}
        {#if fila}
          <strong>{fila.region}</strong><br />
          {numero(fila.investigadores)} investigadores ({porcentaje(
            (fila.investigadores / totalInvestigadores) * 100,
            0,
          )} del país)<br />
          {fila.universidades} universidades · {numero(fila.doctoradosPor1000, 1)} doctorados/1.000 trabajadores
        {/if}
      {/if}
    </Tooltip>
  </div>

  {#snippet tabla()}
    <TablaEquivalente
      {datos}
      resumen="Universidades, investigadores y doctorados trabajando cada 1.000 trabajadores, por región. Estimaciones del Consejo CTCI en base a información administrativa de ANID (Agencia Nacional de Investigación y Desarrollo) y de la Gerencia de Capacidades Tecnológicas de CORFO (Corporación de Fomento de la Producción)."
      columnas={[
        { llave: 'region', titulo: 'Región' },
        { llave: 'universidades', titulo: 'Universidades', numerica: true, formato: (v) => numero(v as number) },
        {
          llave: 'investigadores',
          titulo: 'Investigadores',
          numerica: true,
          formato: (v) => numero(v as number),
        },
        {
          llave: 'doctoradosPor1000',
          titulo: 'Doctorados/1.000 trab.',
          numerica: true,
          formato: (v) => numero(v as number, 1),
        },
      ]}
    />
  {/snippet}
</Figura>

<style>
  .lienzo {
    position: relative;
  }
</style>
