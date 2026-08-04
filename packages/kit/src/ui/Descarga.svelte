<!--
  Descarga.svelte — enlace a un dataset publicado en /datos/ (§8, §10).

  "Datasets publicados en /datos/ con licencia" es ítem del checklist que
  bloquea el merge. Este componente exige la licencia como prop: no hay forma
  de publicar un dato sin declarar bajo qué condiciones se puede reutilizar.
-->
<script lang="ts">
  import { tamano } from '../utils/formato.js';

  interface Props {
    /** Nombre legible del dataset. */
    nombre: string;
    /** Ruta bajo /data/. Ej: "presupuesto-2027/partidas.csv". */
    archivo: string;
    /** Licencia. Por defecto CC BY 4.0, como en el esquema de contenido. */
    licencia?: string;
    /** Bytes. Lo llena el pipeline al publicar; el lector merece saberlo. */
    // `| undefined` explícito en las opcionales: se esparcen desde tipos
    // inferidos por Zod, donde opcional significa `T | undefined`.
    bytes?: number | undefined;
    /** Filas, si aplica. */
    filas?: number | undefined;
    /** Descripción de una línea. */
    descripcion?: string | undefined;
  }

  let {
    nombre, archivo, licencia = 'CC BY 4.0', bytes, filas, descripcion,
  }: Props = $props();

  const extension = $derived(archivo.split('.').pop()?.toUpperCase() ?? 'DATO');
  const href = $derived(`/data/${archivo.replace(/^\/+/, '')}`);
</script>

<!--
  `download` fuerza la descarga en vez de que el navegador abra el CSV como
  texto. `type` ayuda a que el sistema lo asocie a una planilla.
-->
<a class="descarga" {href} download>
  <span class="formato" aria-hidden="true">{extension}</span>

  <span class="cuerpo">
    <span class="nombre">{nombre}</span>
    {#if descripcion}<span class="descripcion">{descripcion}</span>{/if}
    <span class="meta">
      {#if filas !== undefined}<span>{filas.toLocaleString('es-CL')} filas</span>{/if}
      {#if bytes !== undefined}<span>{tamano(bytes)}</span>{/if}
      <span class="licencia">{licencia}</span>
    </span>
  </span>

  <span class="flecha" aria-hidden="true">↓</span>
</a>

<style>
  .descarga {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: var(--espacio-md);
    align-items: center;
    padding: var(--espacio-sm) var(--espacio-md);
    background: var(--color-papel-alto);
    border: 1px solid var(--color-borde);
    color: var(--color-tinta);
    text-decoration: none;
    font-family: var(--fuente-utilidad);
    transition:
      border-color var(--duracion-rapida) var(--curva-salida),
      background var(--duracion-rapida) var(--curva-salida);
  }

  .descarga:hover {
    border-color: var(--color-tinta);
    background: var(--color-papel-bajo);
  }

  /* El verde ácido solo acá: el elemento que el lector acciona (§5). */
  .descarga:focus-visible {
    outline: 2px solid var(--color-enzima);
    outline-offset: 2px;
    border-color: var(--color-tinta);
  }

  .formato {
    font-size: var(--tipo-3xs);
    font-weight: var(--peso-bold);
    letter-spacing: var(--tracking-amplio);
    padding: var(--espacio-2xs) var(--espacio-xs);
    background: var(--color-tinta);
    color: var(--color-papel);
  }

  .cuerpo {
    display: grid;
    gap: var(--espacio-3xs);
    min-width: 0;
  }

  .nombre {
    font-size: var(--tipo-xs);
    font-weight: var(--peso-media);
  }

  .descripcion {
    font-size: var(--tipo-3xs);
    color: var(--color-tinta-suave);
    line-height: 1.4;
  }

  .meta {
    display: flex;
    flex-wrap: wrap;
    gap: var(--espacio-xs);
    font-size: var(--tipo-3xs);
    color: var(--color-sello);
    font-variant-numeric: tabular-nums;
  }

  /* La licencia se destaca del resto de los metadatos: es una condición de
     uso, no una estadística. */
  .licencia {
    border: 1px solid var(--color-borde-fuerte);
    padding-inline: var(--espacio-2xs);
  }

  .flecha {
    font-size: var(--tipo-lg);
    color: var(--color-sello);
    transition: transform var(--duracion-rapida) var(--curva-salida);
  }

  .descarga:hover .flecha {
    color: var(--color-bilis);
    transform: translateY(2px);
  }

  @media (prefers-reduced-motion: reduce) {
    .descarga,
    .flecha {
      transition: none;
    }

    .descarga:hover .flecha {
      transform: none;
    }
  }
</style>
