/**
 * El kit usa `import.meta.env.DEV` para los avisos editoriales de desarrollo
 * (paso máximo del Scrolly, descripción de Figura que no comunica el hallazgo).
 *
 * Se declara acá en vez de depender de `vite/client`: el kit no debe arrastrar
 * Vite como dependencia solo para tipar dos banderas. Astro provee los valores
 * reales en build.
 */
interface ImportMetaEnv {
  readonly DEV: boolean;
  readonly PROD: boolean;
  readonly SSR: boolean;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
