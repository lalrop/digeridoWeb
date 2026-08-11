<!--
  TiempoParcialPictograma.svelte — el tiempo parcial involuntario, en personas.

  El hallazgo de esta pieza (§gancho del artículo) es sobre gente, no sobre una
  institución ni un monto: 647.379 personas trabajan menos horas de las que
  quieren. Una barra más en el gráfico de sectores diluye ese dato entre
  siete categorías; un pictograma lo deja solo, como corresponde a lo que
  realmente es — el agente disenador-visualizaciones evalúa esto para todo
  hallazgo centrado en personas (ver .claude/agents/).

  Origen de las cifras: NO están en pipelines/…/interim/ — ese pipeline solo
  extrajo la tabla de variación por sector (10_extraer.py). Estas dos cifras
  (tiempo parcial total y su tramo involuntario) están citadas tal cual en el
  cuerpo del artículo publicado («Los aperitivos» → «Por horas trabajadas»),
  ya verificadas contra el boletín del INE antes de que la pieza pasara a
  `estado: 'publicada'`. Se declaran acá como constantes, no como prop, para
  que quede explícito que no dependen de datos.json ni de un cálculo nuevo.

  Sin scrollytelling, a propósito: es UNA proporción (personas con/sin jornada
  elegida), no una secuencia de varios momentos — la propia guía del agente
  disenador-visualizaciones separa "hay una secuencia que contar" (Scrolly) de
  "el dato es más una fotografía" (hover/clic). Esto es lo segundo. La primera
  versión usaba Scrolly con una apertura neutra (todo gris hasta el paso 1,
  igual que FlujoPartidas.svelte) — correcta en el patrón, pero acá generaba
  confusión real: quien no scrolleaba exactamente por el gráfico veía un
  pictograma sin contraste, como si estuviera roto. El dato real está siempre
  a la vista; la exploración por ícono es lo que queda interactivo.
-->
<script lang="ts">
  import Figura from '@digerido/kit/charts/Figura.svelte';
  import Pictograma from '@digerido/kit/charts/Pictograma.svelte';
  import TablaEquivalente from '@digerido/kit/charts/TablaEquivalente.svelte';
  import Tooltip from '@digerido/kit/charts/Tooltip.svelte';
  import { numero } from '@digerido/kit/utils';

  // INE, Boletín Estadístico: Empleo Trimestral n°333 — citadas en el cuerpo
  // del artículo, no recalculadas acá.
  const TIEMPO_PARCIAL_TOTAL = 2_000_000;
  const TIEMPO_PARCIAL_INVOLUNTARIO = 647_379;
  const PERSONAS_POR_ICONO = 20_000;

  const cantidadIconos = TIEMPO_PARCIAL_TOTAL / PERSONAS_POR_ICONO;
  const destacadosIconos = TIEMPO_PARCIAL_INVOLUNTARIO / PERSONAS_POR_ICONO;

  // ── Estado del tooltip ────────────────────────────────────────────────────
  let activo = $state<number | null>(null);
  let lienzo = $state<HTMLDivElement | null>(null);

  /** Posición aproximada del ícono `i` dentro del contenedor, para el tooltip. */
  function posicionIcono(i: number) {
    const cols = Math.ceil(Math.sqrt(cantidadIconos));
    const ancho = lienzo?.clientWidth ?? 0;
    const iconoPx = ancho / cols;
    return {
      x: (i % cols) * iconoPx + iconoPx / 2,
      y: Math.floor(i / cols) * iconoPx,
    };
  }

  function etiquetaIcono(i: number, destacado: boolean): string {
    const desde = numero(i * PERSONAS_POR_ICONO + 1);
    const hasta = numero(Math.min((i + 1) * PERSONAS_POR_ICONO, TIEMPO_PARCIAL_TOTAL));
    return destacado
      ? `Personas ${desde} a ${hasta} de ${numero(TIEMPO_PARCIAL_TOTAL)}: parte del tiempo parcial involuntario`
      : `Personas ${desde} a ${hasta} de ${numero(TIEMPO_PARCIAL_TOTAL)}: eligieron trabajar tiempo parcial`;
  }
</script>

<Figura
  id="tiempo-parcial-involuntario"
  titulo="Una de cada tres personas con jornada parcial no la eligió"
  descripcion="De los 2 millones de personas que trabajan tiempo parcial, 647.379 —una de cada tres— no eligieron esa jornada: quieren trabajar más horas y no consiguen."
  unidades="Cada figura representa 20.000 personas"
  fuente="INE, Boletín Estadístico: Empleo Trimestral, edición n°333 (31 julio 2026)"
  sangria="ancho"
>
  <div class="lienzo" bind:this={lienzo}>
    <Pictograma
      cantidad={cantidadIconos}
      destacados={destacadosIconos}
      descripcion="De los 2 millones de personas que trabajan tiempo parcial, 647.379 no eligieron esa jornada"
      {activo}
      alActivar={(i) => (activo = i)}
      alDesactivar={() => (activo = null)}
      {etiquetaIcono}
    />

    <Tooltip
      visible={activo !== null}
      x={activo !== null ? posicionIcono(activo).x : 0}
      y={activo !== null ? posicionIcono(activo).y : 0}
      anchoContenedor={lienzo?.clientWidth ?? 0}
      altoContenedor={lienzo?.clientHeight ?? 0}
    >
      {#if activo !== null}
        {etiquetaIcono(activo, destacadosIconos - activo > 0)}
      {/if}
    </Tooltip>
  </div>

  {#snippet tabla()}
    <TablaEquivalente
      datos={[
        { grupo: 'Tiempo parcial, total', personas: TIEMPO_PARCIAL_TOTAL },
        { grupo: 'De ese total, involuntario', personas: TIEMPO_PARCIAL_INVOLUNTARIO },
      ]}
      resumen="Personas ocupadas con jornada de tiempo parcial (1 a 30 horas semanales), total y tramo involuntario."
      columnas={[
        { llave: 'grupo', titulo: 'Grupo' },
        {
          llave: 'personas',
          titulo: 'Personas',
          numerica: true,
          formato: (v) => numero(v as number),
        },
      ]}
    />
  {/snippet}
</Figura>

<style>
  .lienzo {
    position: relative;
    max-width: 26rem;
    margin-inline: auto;
  }
</style>
