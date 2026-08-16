<!--
  CostoTefScrolly.svelte — la secuencia de scrollytelling del gráfico
  principal.

  MDX es JSX: la sintaxis de snippets de Svelte no es válida ahí, así que el
  `<Scrolly>` se arma en un componente propio de la digestión y ESE se usa en
  el MDX (mismo patrón que ExpectativasInflacionScrolly, IPN agosto 2026).
-->
<script lang="ts">
  import Paso from '@digerido/kit/scroll/Paso.svelte';
  import Scrolly from '@digerido/kit/scroll/Scrolly.svelte';

  import CostoTef from './CostoTef.svelte';

  interface Fila {
    entidad: string;
    monto: number;
    porcentaje: number;
  }

  let { datos }: { datos: Fila[] } = $props();
</script>

<!-- Tres pasos: bien bajo el máximo de 6 que fija §6.2. -->
<Scrolly total={3}>
  {#snippet grafico(paso)}
    <CostoTef {datos} {paso} />
  {/snippet}

  {#snippet pasos()}
    <Paso indice={0}>
      <p>
        Cinco proveedores permiten a un comercio aceptar pagos por
        transferencia (TEF). Cobran comisiones muy distintas — y la
        diferencia es más grande mientras más chico es el pago.
      </p>
    </Paso>

    <Paso indice={1}>
      <p>
        Si le pagan <strong>$1.000</strong> a un almacén y paga con
        transferencia usando el proveedor más caro, <strong
          >42,1% de esa venta se va en la comisión</strong
        >. Con el más barato, apenas 1%.
      </p>
    </Paso>

    <Paso indice={2}>
      <p>
        Ese proveedor más barato, <strong>Banco 1</strong>, cobra
        <strong>siempre 1%</strong>, sin importar si el pago es de $1.000 o de
        $50.000. Los demás bajan su comisión a medida que el monto crece —
        prueba de que el 42,1% inicial no es un límite técnico, es una
        decisión comercial.
      </p>
    </Paso>
  {/snippet}

  <!--
    Degradación de §6.4: con `prefers-reduced-motion` o sin JS, el mismo
    contenido se apila, cada bloque congelado en el paso que describe.
  -->
  {#snippet estaticos(i)}
    <CostoTef {datos} paso={i} />
    {#if i === 0}
      <p class="estatico">
        Cinco proveedores permiten aceptar pagos por transferencia (TEF), con
        comisiones muy distintas entre sí.
      </p>
    {:else if i === 1}
      <p class="estatico">
        Con el proveedor más caro, un pago de $1.000 pierde 42,1% en
        comisión. Con el más barato, apenas 1%.
      </p>
    {:else}
      <p class="estatico">
        Banco 1 cobra siempre 1%, sin importar el monto — los demás bajan su
        comisión a medida que el pago crece.
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
