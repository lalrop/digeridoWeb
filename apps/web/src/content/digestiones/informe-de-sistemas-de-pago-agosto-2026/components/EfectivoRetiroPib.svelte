<!--
  EfectivoRetiroPib.svelte — comparador tipográfico, en "Los aperitivos".

  No es un `<Figura>`: son 2 cifras (2019 y 2025), citadas tal cual del
  cuerpo del Informe (§ "La materia prima" ya explica que sus gráficos son
  imágenes sin datos detrás — ver `limitaciones` del frontmatter). Envolverlo
  en Figura pediría una tabla equivalente y una interacción que no aportan
  nada con solo 2 números: es el mismo criterio que ya usa el layout para el
  pull-quote del `hallazgo`, tipografía grande en vez de un gráfico de barras
  de 2 columnas.

  Sigue siendo accesible sin necesitar foco/hover: los dos números y el
  delta están en el DOM como texto normal, con `aria-hidden` solo en la
  flecha decorativa.

  Momento de deleite: los dos números "cuentan" desde 0 hasta su valor real
  la primera vez que el comparador entra en pantalla — como un odómetro.
  Progresivo (acción `enVista` del kit, sin dependencias nuevas: un contador
  con requestAnimationFrame a mano en vez de `svelte/motion`, para no sumar
  peso a un componente que hoy no manda nada de JS): sin JS, con
  `prefers-reduced-motion`, o si ya está visible al cargar, se muestran
  directo los valores finales — nunca dependen de la animación para existir.
-->
<script lang="ts">
  import { enVista, numero } from '@digerido/kit/utils';

  interface Props {
    desde: { anio: number; valor: number };
    hasta: { anio: number; valor: number };
    unidad: string;
  }

  let { desde, hasta, unidad }: Props = $props();

  const delta = $derived(Math.round((hasta.valor - desde.valor) * 10) / 10);

  let mostradoDesde = $state(desde.valor);
  let mostradoHasta = $state(hasta.valor);

  const DURACION_MS = 900;

  function animarConteo(destinoDesde: number, destinoHasta: number) {
    const origenDesde = mostradoDesde;
    const origenHasta = mostradoHasta;
    const inicio = performance.now();

    function paso(ahora: number) {
      const t = Math.min(1, (ahora - inicio) / DURACION_MS);
      const suavizado = 1 - (1 - t) ** 3; // ease-out cúbico
      mostradoDesde = origenDesde + (destinoDesde - origenDesde) * suavizado;
      mostradoHasta = origenHasta + (destinoHasta - origenHasta) * suavizado;
      if (t < 1) requestAnimationFrame(paso);
    }
    requestAnimationFrame(paso);
  }

  function alCambiar(estado: 'oculto' | 'revelado') {
    if (estado === 'oculto') {
      mostradoDesde = 0;
      mostradoHasta = 0;
    } else {
      animarConteo(desde.valor, hasta.valor);
    }
  }
</script>

<figure class="comparador" use:enVista={alCambiar}>
  <div class="cifras">
    <div class="cifra">
      <p class="cifra__valor">{numero(mostradoDesde, 1)}%</p>
      <p class="cifra__etiqueta">{desde.anio}</p>
    </div>

    <span class="flecha" aria-hidden="true">→</span>

    <div class="cifra">
      <p class="cifra__valor cifra__valor--actual">{numero(mostradoHasta, 1)}%</p>
      <p class="cifra__etiqueta">{hasta.anio}</p>
    </div>
  </div>

  <figcaption>
    <p class="unidad">{unidad}</p>
    <p class="delta">{delta} puntos porcentuales en {hasta.anio - desde.anio} años</p>
  </figcaption>
</figure>

<style>
  .comparador {
    margin: var(--espacio-lg) 0;
    padding: var(--espacio-md) var(--espacio-lg);
    border: 1px solid var(--color-borde);
    border-radius: var(--radio-md);
    width: fit-content;
    max-width: 100%;
  }

  .cifras {
    display: flex;
    align-items: baseline;
    gap: var(--espacio-md);
    flex-wrap: wrap;
  }

  .cifra {
    text-align: center;
  }

  .cifra__valor {
    font-family: var(--fuente-display);
    font-size: var(--tipo-3xl);
    font-weight: var(--peso-semi);
    color: var(--color-tinta-suave);
    margin: 0;
    font-variant-numeric: tabular-nums;
  }

  .cifra__valor--actual {
    color: var(--color-bilis);
  }

  .cifra__etiqueta {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-2xs);
    color: var(--color-sello);
    margin: 0;
  }

  .flecha {
    font-size: var(--tipo-xl);
    color: var(--color-borde-fuerte);
  }

  figcaption {
    margin-block-start: var(--espacio-sm);
    padding-block-start: var(--espacio-sm);
    border-block-start: 1px solid var(--color-borde);
  }

  .unidad {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-3xs);
    letter-spacing: var(--tracking-amplio);
    text-transform: uppercase;
    color: var(--color-sello);
    margin: 0;
  }

  .delta {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-xs);
    color: var(--color-tinta);
    margin: var(--espacio-2xs) 0 0;
  }
</style>
