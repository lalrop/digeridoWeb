<!--
  ExpectativasInflacionScrolly.svelte — la secuencia de scrollytelling del
  gráfico principal.

  MDX es JSX: la sintaxis de snippets de Svelte no es válida ahí, así que el
  `<Scrolly>` se arma en un componente propio de la digestión y ESE se usa en
  el MDX (mismo patrón que FlujoScrolly.svelte, ejemplo-partidas).
-->
<script lang="ts">
  import Paso from '@digerido/kit/scroll/Paso.svelte';
  import Scrolly from '@digerido/kit/scroll/Scrolly.svelte';

  import ExpectativasInflacion from './ExpectativasInflacion.svelte';

  interface Fila {
    horizonte: '12 meses' | '24 meses';
    periodo: string;
    media: number;
    mediana: number;
  }

  let { datos }: { datos: Fila[] } = $props();
</script>

<!-- Tres pasos: bien bajo el máximo de 6 que fija §6.2. -->
<Scrolly total={3}>
  {#snippet grafico(paso)}
    <ExpectativasInflacion {datos} {paso} />
  {/snippet}

  {#snippet pasos()}
    <Paso indice={0}>
      <p>
        Así se mueve normalmente la inflación que las empresas esperan para
        dentro de dos años: sube y baja unas décimas, trimestre a trimestre,
        desde 2023.
      </p>
    </Paso>

    <Paso indice={1}>
      <p>
        A comienzos de 2026 tocó su <strong>mínimo histórico: 3%</strong>. Nunca,
        desde que existe esta encuesta, las empresas habían esperado una
        inflación tan baja a dos años de plazo.
      </p>
    </Paso>

    <Paso indice={2}>
      <p>
        Cuatro meses después, tras el shock de costos que trajo el conflicto
        en Medio Oriente, la expectativa <strong>subió a 3,5%</strong> — y ahí
        se quedó en junio. La línea de 12 meses (gris) reaccionó todavía más:
        pasó de 3% a 4% en el mismo período.
      </p>
    </Paso>
  {/snippet}

  <!--
    Degradación de §6.4: con `prefers-reduced-motion` o sin JS, el mismo
    contenido se apila, cada bloque congelado en el paso que describe.
  -->
  {#snippet estaticos(i)}
    <ExpectativasInflacion {datos} paso={i} />
    {#if i === 0}
      <p class="estatico">
        Así se mueve normalmente la inflación esperada a dos años: sube y baja
        unas décimas, trimestre a trimestre, desde 2023.
      </p>
    {:else if i === 1}
      <p class="estatico">
        A comienzos de 2026 tocó su mínimo histórico: 3%, nunca visto desde
        que existe esta encuesta.
      </p>
    {:else}
      <p class="estatico">
        Cuatro meses después subió a 3,5%, tras el shock de costos del
        conflicto en Medio Oriente — y ahí se quedó en junio.
      </p>
    {/if}
  {/snippet}
</Scrolly>

<style>
  .estatico {
    font-family: var(--fuente-cuerpo);
    font-size: var(--tipo-sm);
    line-height: var(--interlinea-cuerpo);
    max-width: var(--medida-angosta);
    margin-inline: auto;
    padding-inline-start: var(--espacio-md);
    border-inline-start: 2px solid var(--color-borde);
  }
</style>
