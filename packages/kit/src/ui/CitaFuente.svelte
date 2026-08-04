<!--
  CitaFuente.svelte — la trazabilidad del documento original, visible (§7, §8).

  "Método y fuentes — siempre visible, nunca escondido" (§10). El hash sha256 no
  es decoración: cuando un organismo reemplaza un PDF sin aviso —pasa seguido—
  este es el registro de qué versión se digirió.
-->
<script lang="ts">
  import { fechaISO, formatoFecha, hashCorto, numero } from '../utils/formato.js';

  interface Props {
    titulo: string;
    organismo: string;
    url: string;
    fechaPublicacion: Date | string;
    fechaDescarga: Date | string;
    sha256: string;
    // `| undefined` explícito: estas props se esparcen desde tipos inferidos
    // por Zod, donde opcional significa `T | undefined`. Sin esto,
    // exactOptionalPropertyTypes rechaza `{...fuente}`.
    paginas?: number | undefined;
    formato: 'pdf' | 'xlsx' | 'csv' | 'api' | 'html';
    /** Compacta: para la lista de fuentes al pie del artículo. */
    compacta?: boolean;
  }

  let {
    titulo, organismo, url, fechaPublicacion, fechaDescarga,
    sha256, paginas, formato, compacta = false,
  }: Props = $props();
</script>

<article class="fuente" class:compacta>
  <p class="organismo">
    <span class="sigla">{organismo}</span>
    <span class="formato">{formato.toUpperCase()}</span>
    {#if paginas}<span class="paginas">{numero(paginas)} pp.</span>{/if}
  </p>

  <h4>
    <!--
      `rel="noopener"` y target en blanco: el lector vuelve al artículo. No se
      usa `nofollow`: citar la fuente original es parte del punto.
    -->
    <a href={url} target="_blank" rel="noopener">{titulo}</a>
  </h4>

  <dl class="meta">
    <div>
      <dt>Publicado</dt>
      <dd><time datetime={fechaISO(fechaPublicacion)}>{formatoFecha(fechaPublicacion)}</time></dd>
    </div>
    <div>
      <dt>Descargado</dt>
      <dd><time datetime={fechaISO(fechaDescarga)}>{formatoFecha(fechaDescarga)}</time></dd>
    </div>
    <div class="hash">
      <dt>SHA-256</dt>
      <!-- `title` con el hash completo: verificable con copiar y pegar. -->
      <dd><code title={sha256}>{hashCorto(sha256)}</code></dd>
    </div>
  </dl>
</article>

<style>
  .fuente {
    font-family: var(--fuente-utilidad);
    font-size: var(--tipo-2xs);
    color: var(--color-tinta);
    padding: var(--espacio-md);
    background: var(--color-papel-alto);
    /* Filete izquierdo grueso: cita de documento, no cita de persona. */
    border-inline-start: 4px solid var(--color-tinta);
    border-block: 1px solid var(--color-borde);
    border-inline-end: 1px solid var(--color-borde);
  }

  .organismo {
    display: flex;
    flex-wrap: wrap;
    gap: var(--espacio-xs);
    align-items: baseline;
    margin: 0 0 var(--espacio-xs);
    font-size: var(--tipo-3xs);
    letter-spacing: var(--tracking-versalita);
    text-transform: uppercase;
  }

  .sigla {
    font-weight: var(--peso-bold);
  }

  .formato,
  .paginas {
    color: var(--color-sello);
  }

  .formato {
    border: 1px solid var(--color-borde-fuerte);
    padding-inline: var(--espacio-2xs);
  }

  h4 {
    font-family: var(--fuente-cuerpo);
    font-size: var(--tipo-sm);
    font-weight: var(--peso-semi);
    line-height: var(--interlinea-corta);
    margin: 0 0 var(--espacio-sm);
    text-wrap: balance;
  }

  a {
    color: var(--color-tinta);
    text-decoration-color: var(--color-borde-fuerte);
    text-decoration-thickness: 1px;
    text-underline-offset: 3px;
  }

  a:hover {
    text-decoration-color: var(--color-bilis);
  }

  a:focus-visible {
    outline: 2px solid var(--color-enzima);
    outline-offset: 3px;
    text-decoration: none;
  }

  .meta {
    display: flex;
    flex-wrap: wrap;
    gap: var(--espacio-xs) var(--espacio-lg);
    margin: 0;
    font-size: var(--tipo-3xs);
  }

  dt {
    color: var(--color-sello);
    letter-spacing: var(--tracking-amplio);
    text-transform: uppercase;
  }

  dd {
    margin: 0;
    font-variant-numeric: tabular-nums;
  }

  code {
    font-family: inherit;
    /* Fondo suave para que el hash lea como dato bruto y no como prosa. */
    background: var(--color-papel-bajo);
    padding-inline: var(--espacio-2xs);
    cursor: help;
  }

  .compacta {
    padding: var(--espacio-sm);
    border-inline-start-width: 3px;
  }

  .compacta h4 {
    font-size: var(--tipo-xs);
    margin-block-end: var(--espacio-xs);
  }
</style>
