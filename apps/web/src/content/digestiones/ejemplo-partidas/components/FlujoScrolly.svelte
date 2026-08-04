<!--
  FlujoScrolly.svelte — la secuencia de scrollytelling de esta pieza.

  ── Por qué este archivo existe ─────────────────────────────────────────────
  MDX es JSX: la sintaxis de snippets de Svelte (`{#snippet}` / `{@render}`) NO
  es válida ahí. Así que un `<Scrolly>` no se puede armar desde el artículo; hay
  que envolverlo en un componente Svelte propio de la digestión y usar ESE en el
  MDX:

      <FlujoScrolly datos={...} client:visible />

  Es un límite del stack que conviene conocer temprano, y encaja con la
  estructura de §3: cada pieza tiene su carpeta `components/` con las islas que
  solo le sirven a ella. El kit aporta Scrolly y Paso; el guión de los pasos —que
  es contenido editorial— vive con el artículo.
-->
<script lang="ts">
  import Paso from '@digerido/kit/scroll/Paso.svelte';
  import Scrolly from '@digerido/kit/scroll/Scrolly.svelte';

  import FlujoPartidas from './FlujoPartidas.svelte';

  interface Partida {
    partida: string;
    monto: number;
    variacion: number;
    destacado: boolean;
  }

  let { datos, unidad }: { datos: Partida[]; unidad: string } = $props();
</script>

<!-- Tres pasos: bien bajo el máximo de 6 que fija §6.2. -->
<Scrolly total={3}>
  {#snippet grafico(paso)}
    <FlujoPartidas {datos} {unidad} {paso} />
  {/snippet}

  {#snippet pasos()}
    <Paso indice={0}>
      <p>
        Ocho partidas, ordenadas por monto. Así llega el dato: una lista sin
        jerarquía, donde todo pesa lo mismo. <strong>Nada resalta porque nada se
        eligió.</strong>
      </p>
    </Paso>

    <Paso indice={1}>
      <p>
        Ahora sí. La partida mayor concentra <strong>un tercio del aumento
        total</strong>, y el color deja de ser decorativo: marca el único dato
        que la pieza quiere que te lleves.
      </p>
    </Paso>

    <Paso indice={2}>
      <p>
        Dos partidas <strong>caen</strong>. Es el hallazgo secundario, y por eso
        cambia de color en vez de aparecer en un gráfico nuevo: un artículo tiene
        un gráfico memorable, no doce.
      </p>
    </Paso>
  {/snippet}

  <!--
    Degradación de §6.4: con `prefers-reduced-motion` o sin JS, el mismo
    contenido se apila. El gráfico se congela en el paso que corresponde, así
    que cada bloque sigue mostrando lo que su texto describe.
  -->
  {#snippet estaticos(i)}
    <FlujoPartidas {datos} {unidad} paso={i} />
    {#if i === 0}
      <p class="estatico">
        Ocho partidas, ordenadas por monto. Una lista sin jerarquía, donde todo
        pesa lo mismo.
      </p>
    {:else if i === 1}
      <p class="estatico">
        La partida mayor concentra un tercio del aumento total. El color marca el
        dato que importa.
      </p>
    {:else}
      <p class="estatico">
        Dos partidas caen: el hallazgo secundario, en el mismo gráfico y no en uno
        nuevo.
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
