<!--
  AccesoEfectivo.svelte — gráfico de apoyo, en "Los aperitivos".

  El hallazgo de este gráfico ES sobre personas (qué % de la población usa
  cada canal para conseguir efectivo), no sobre instituciones ni montos: por
  regla del agente disenador-visualizaciones, ahí es donde un `Pictograma`
  (dibujos de personas) comunica mejor que una barra abstracta — y es más
  lúdico, que es justo lo que le faltaba a la primera versión de este gráfico
  (una barra horizontal plana).

  Sin scrollytelling, a propósito, siguiendo la misma lección que ya dejó
  documentada `TiempoParcialPictograma.svelte` (ENE): envolver un Pictograma
  en `Scrolly` deja el grupo destacado en gris hasta que alguien scrollea
  exactamente por encima, lo que se lee como un gráfico roto para quien no
  pasa por ahí. Acá las dos cifras están siempre a la vista, completas; lo
  que queda interactivo es explorar ícono por ícono.
-->
<script lang="ts">
  import Figura from '@digerido/kit/charts/Figura.svelte';
  import Pictograma from '@digerido/kit/charts/Pictograma.svelte';
  import TablaEquivalente from '@digerido/kit/charts/TablaEquivalente.svelte';
  import Tooltip from '@digerido/kit/charts/Tooltip.svelte';
  import { porcentaje } from '@digerido/kit/utils';

  interface Fila {
    canal: string;
    porcentaje: number;
  }

  let { datos }: { datos: Fila[] } = $props();

  const COLUMNAS = 10;

  // ── Estado del tooltip, uno por grilla (indexadas por posición) ────────────
  let activo = $state<{ grupo: number; icono: number } | null>(null);
  let lienzos = $state<(HTMLDivElement | null)[]>([]);

  function posicionIcono(grupo: number, i: number) {
    const ancho = lienzos[grupo]?.clientWidth ?? 0;
    const iconoPx = ancho / COLUMNAS;
    return {
      x: (i % COLUMNAS) * iconoPx + iconoPx / 2,
      y: Math.floor(i / COLUMNAS) * iconoPx,
    };
  }

  function etiquetaIcono(canal: string, i: number, destacado: boolean): string {
    return destacado
      ? `Persona ${i + 1} de 100: usa ${canal} como canal principal para obtener efectivo`
      : `Persona ${i + 1} de 100: no usa ${canal} como canal principal`;
  }
</script>

<Figura
  id="acceso-efectivo"
  titulo="Los cajeros siguen siendo la puerta principal al efectivo, pero las Cajas Vecinas ya llegan a casi la mitad"
  descripcion="El 77% de la población usa cajeros automáticos como canal principal para obtener efectivo; un 47% usa las Cajas Vecinas, que amplían la cobertura en zonas con menos bancos."
  unidades="Cada figura representa 1% de la población"
  fuente="Banco Central de Chile, ENUPE 2025, citada en el Informe de Sistemas de Pago, agosto 2026 (Recuadro I.2)"
  nota="Los canales no son excluyentes: una misma persona puede usar cajeros automáticos y Cajas Vecinas según el lugar."
  sangria="ancho"
>
  <div class="grillas">
    {#each datos as d, grupo (d.canal)}
      <div class="grupo">
        <p class="grupo__titulo">
          <span class="grupo__valor">{porcentaje(d.porcentaje, 0)}</span>
          {d.canal}
        </p>
        <div class="lienzo" bind:this={lienzos[grupo]}>
          <Pictograma
            cantidad={100}
            destacados={d.porcentaje}
            columnas={COLUMNAS}
            descripcion="{porcentaje(d.porcentaje, 0)} de la población usa {d.canal} como canal principal para obtener efectivo"
            activo={activo?.grupo === grupo ? activo.icono : null}
            alActivar={(icono) => (activo = { grupo, icono })}
            alDesactivar={() => (activo = null)}
            etiquetaIcono={(i, destacado) => etiquetaIcono(d.canal, i, destacado)}
          />

          <Tooltip
            visible={activo?.grupo === grupo}
            x={activo?.grupo === grupo ? posicionIcono(grupo, activo.icono).x : 0}
            y={activo?.grupo === grupo ? posicionIcono(grupo, activo.icono).y : 0}
            anchoContenedor={lienzos[grupo]?.clientWidth ?? 0}
            altoContenedor={lienzos[grupo]?.clientHeight ?? 0}
          >
            {#if activo?.grupo === grupo}
              {etiquetaIcono(d.canal, activo.icono, d.porcentaje - activo.icono > 0)}
            {/if}
          </Tooltip>
        </div>
      </div>
    {/each}
  </div>

  {#snippet tabla()}
    <TablaEquivalente
      {datos}
      resumen="Canal principal de obtención de efectivo, % de la población."
      columnas={[
        { llave: 'canal', titulo: 'Canal' },
        {
          llave: 'porcentaje',
          titulo: 'Población',
          numerica: true,
          formato: (v) => porcentaje(v as number, 0),
        },
      ]}
    />
  {/snippet}
</Figura>

<style>
  .grillas {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--espacio-xl);
  }

  @media (min-width: 40rem) {
    .grillas {
      grid-template-columns: 1fr 1fr;
    }
  }

  .grupo__titulo {
    display: flex;
    align-items: baseline;
    gap: var(--espacio-xs);
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-sm);
    color: var(--color-tinta-suave);
    margin: 0 0 var(--espacio-sm);
  }

  .grupo__valor {
    font-family: var(--fuente-display);
    font-size: var(--tipo-2xl);
    font-weight: var(--peso-semi);
    color: var(--color-tinta);
    font-variant-numeric: tabular-nums;
  }

  .lienzo {
    position: relative;
    max-width: 22rem;
  }
</style>
