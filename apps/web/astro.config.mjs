import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import svelte from '@astrojs/svelte';
import { defineConfig } from 'astro/config';

/**
 * Configuración de Astro.
 *
 * §2.1: cero JS por defecto. Cada digestión hidrata solo las islas que
 * necesita. No hay integración de React: si alguna digestión llega a requerir
 * una librería que solo existe ahí, se agrega en ese momento y para esa pieza,
 * no de entrada para todas.
 */
export default defineConfig({
  // Dominio propio; se ajusta al desplegar. Alimenta canonical, RSS y sitemap.
  site: 'https://digerido.cl',

  // 95% estático (§2.1). Sin adaptador, sin runtime de servidor.
  output: 'static',

  integrations: [
    svelte(),
    mdx({
      // El MDX es el esqueleto del artículo; los componentes se insertan como
      // etiquetas dentro del texto (§2.1).
      optimize: true,
    }),
    sitemap({
      // Los borradores no se indexan: `estado` vive en el frontmatter, y
      // `getStaticPaths` ya los excluye del build de producción.
      filter: (pagina) => !pagina.includes('/borrador/'),
    }),
  ],

  build: {
    // Assets con hash → Cache-Control immutable a 1 año en Nginx (§9).
    assets: '_assets',
    // CSS en archivos, no inline: mejor cacheado entre digestiones, que
    // comparten casi todo el CSS del kit.
    inlineStylesheets: 'never',
  },

  image: {
    // AVIF vía astro:assets (§8).
    responsiveStyles: true,
  },

  vite: {
    build: {
      // El presupuesto de §8 se mide sobre archivos comprimidos; sourcemaps
      // en producción no cuentan, pero tampoco se sirven.
      sourcemap: false,
      // Avisa antes de que una isla se acerque al techo de 150 KB por
      // digestión. El chequeo duro está en scripts/presupuesto-rendimiento.ts.
      chunkSizeWarningLimit: 120,
    },
  },

  // Astro 5+ recorta los `<script>` de las islas no hidratadas; con
  // `prefetch` los índices precargan la digestión al pasar el cursor.
  prefetch: {
    prefetchAll: false,
    defaultStrategy: 'hover',
  },
});
