# digerido

Portal editorial que digiere documentos públicos ilegibles y los devuelve como
historias visuales navegables.

Chile publica una enorme cantidad de información pública que es técnicamente
accesible y prácticamente inutilizable: PDFs de 400 páginas, planillas sin
diccionario de variables, informes en jerga administrativa. El problema no es la
disponibilidad. Es la **digestibilidad**.

`digerido` no es un dashboard ni un repositorio de datos. Es una **publicación**.
Cada pieza tiene un ángulo, un hallazgo y un cierre. Si una digestión no puede
resumirse en una frase que le importe a alguien, no se publica.

**Estado:** Fase 0 (fundaciones) completa. No hay ninguna digestión real
publicada todavía; la pieza `ejemplo-partidas` es andamiaje con datos sintéticos
y se borra cuando exista la primera de verdad.

---

## Arrancar

```bash
pnpm install
pnpm -F @digerido/tokens build   # genera dist/tokens.css desde los módulos TS
pnpm dev                         # http://localhost:4321
```

Para los pipelines de datos:

```bash
pip install -e '.[dev]'
pytest pipelines -q
```

`just` es opcional pero recomendado (`cargo install just` o el gestor de tu
sistema): los pipelines lo usan como corredor de tareas.

### Fuentes tipográficas

Las tres familias son autoalojadas y **no viajan en el repo** por licencia.
Antes de publicar hay que dejarlas en `apps/web/public/fuentes/`:

| Archivo | Familia | Para qué |
|---|---|---|
| `archivo-expanded-var.woff2` | Archivo Expanded (variable) | Titulares |
| `literata-var.woff2` | Literata (variable) | Cuerpo |
| `ibm-plex-mono-regular.woff2` | IBM Plex Mono | Cifras, ejes, folios |
| `ArchivoExpanded-Bold.ttf` | ídem, en TTF | Imágenes OG |
| `IBMPlexMono-Regular.ttf` | ídem, en TTF | Imágenes OG |

Los TTF son aparte porque Satori —que genera las imágenes OG— no lee WOFF2. Sin
ellos el build funciona igual, cayendo a una fuente del sistema, y avisa fuerte
en la consola.

---

## Estructura

```
apps/web/            Astro: contenido, layouts, páginas, estilos
packages/tokens/     Fuente única de color/tipo/espacio → CSS + TS
packages/kit/        Design system y primitivas de visualización
pipelines/           Python: descargar → extraer → limpiar → validar → publicar
scripts/             Scaffolding, presupuesto de rendimiento, revalidación
infra/nginx/         Configuración de producción
```

**La frontera que importa:** `pipelines/` y `apps/web/` se comunican **solo** por
archivos en `apps/web/public/data/`. El front nunca lee un PDF ni un Excel en
runtime, y `30_publicar.py` es el único paso del pipeline autorizado a escribir
dentro de `apps/web`.

---

## Crear una digestión

Guía completa paso a paso, incluido cómo queda un dataset publicado en la
Despensa: **[`docs/AGREGAR-DIGESTIONES.md`](docs/AGREGAR-DIGESTIONES.md)**.

```bash
pnpm nueva-digestion "Presupuesto 2027"
```

Crea el MDX con el frontmatter completo, el componente base del gráfico, los
cuatro pasos del pipeline, sus tests y un `CHECKLIST.md`. Después:

```bash
# 1. poné la URL del documento en pipelines/<slug>/00_descargar.py
just -f pipelines/<slug>/justfile todo
# 2. copiá las métricas del meta.json al frontmatter
# 3. escribí el hallazgo ANTES del artículo
```

Si el hallazgo no sale en una frase, todavía no hay pieza.

---

## Las reglas viven en el código

Un plan que solo existe en un documento se erosiona en la tercera digestión.
Estas reglas están puestas donde fallan solas:

| Regla | Dónde se impone |
|---|---|
| Sin fuente verificable ni `hallazgo`, no hay pieza | Esquemas Zod en `apps/web/src/content.config.ts` — el build falla |
| El `hallazgo` es UNA frase | Mismo esquema: rechaza más de un punto final |
| Digerir reduce el tiempo de lectura | Mismo esquema: rechaza digerido ≥ original |
| Toda pieza publicada declara limitaciones | Mismo esquema, solo para `estado: publicada` |
| La paleta funciona bajo deuteranopía y protanopía | `packages/tokens/src/color.test.ts`, en CI |
| Máximo 5 series categóricas | `escalaCategorica()` lanza sobre 5 |
| Todo gráfico tiene tabla equivalente | `<Figura>` avisa en desarrollo si falta |
| La descripción comunica el hallazgo, no el tipo de gráfico | `<Figura>` avisa si empieza con «gráfico de…» |
| Máximo 6 pasos de scrollytelling | `<Scrolly>` avisa en desarrollo |
| Los datos que no pasan las invariantes no se publican | `20_limpiar.py` no escribe nada si fallan |
| El presupuesto de rendimiento se respeta | `pnpm presupuesto` falla el CI |
| Cuando una fuente cambia en origen, se sabe | Job semanal `revalidar-fuentes.yml` |

Lo que **no** se puede automatizar, y por eso está en el checklist de cada
pieza: la verificación de las cifras contra el documento original en una segunda
pasada, y la prueba en un teléfono real.

---

## Comandos

| Comando | Qué hace |
|---|---|
| `pnpm dev` | Servidor de desarrollo |
| `pnpm build` | Tokens + sitio estático en `apps/web/dist` |
| `pnpm test` | Tests de todos los paquetes |
| `pnpm typecheck` | TypeScript + `svelte-check` + `astro check` |
| `pnpm presupuesto` | Presupuesto de rendimiento sobre `dist/` |
| `DIGERIDO_EJEMPLOS=1 pnpm build` | Build que incluye el andamiaje, para medir con una isla hidratada |
| `pnpm nueva-digestion "…"` | Andamiaje de una pieza nueva |
| `pnpm -F @digerido/tokens explorar` | Busca paletas categóricas CVD-seguras |
| `pytest pipelines -q` | Invariantes de los datos |
| `python3 scripts/revalidar_fuentes.py` | Compara hashes contra los registrados |

---

## Decisiones de arquitectura

**Astro + Svelte, no Next.js.** El sitio es 95 % estático con picos de
interactividad localizados. Pagar el runtime de React en todas las páginas para
hidratar tres gráficos es lo que hace que los sitios de data storytelling pesen
4 MB. Medido en este repo: **15 KB de JS de shell contra un techo de 40 KB**, y
30,8 KB de JS total con una isla de gráfico y el scrollytelling hidratados.

**D3 calcula, Svelte renderiza.** Se importan solo `d3-scale`, `d3-shape`,
`d3-array`, `d3-geo`. Nunca `d3` completo, nunca `.append()`. Svelte es dueño del
DOM; D3 aporta escalas, formas y geografías. Es lo que hace que los gráficos sean
animables, testeables y renderizables en el servidor.

**Referencia editorial: pudding.cool, no un dashboard.** Ningún gráfico es una
imagen estática al lado del texto — todos tienen scrollytelling
(`@digerido/kit/scroll/Scrolly.svelte`) o exploración por hover/clic con
tooltip accesible por teclado. Cuando el hallazgo es directamente sobre
personas, `@digerido/kit/charts/Pictograma.svelte` las dibuja como grupo de
figuras (isotype) en vez de reducirlas a una barra. Lo diseña el agente
`disenador-visualizaciones` (`.claude/agents/`), a partir del ángulo que ya
eligió `redactor-digestion` para esa pieza.

**CSS nativo con `@layer`, no Tailwind.** Un sitio editorial necesita un sistema
tipográfico sólido y control fino del grid, no utilidades. El orden de capas se
declara una vez (`tokens, base, layout, components, utilities`) y elimina las
guerras de especificidad sin un solo `!important`.

**La legibilidad se calcula dos veces, a propósito.** `legibilidad.py` mide el
documento original; `legibilidad.ts` mide el texto digerido en build. Es la única
duplicación deliberada del repo —el pipeline no puede importar TS, y el front no
puede leer un PDF— y los dos comparten los mismos casos de prueba como contrato.

---

## Notas de implementación

Cosas que se descubrieron construyendo esto y conviene saber antes de tropezar:

- **Los snippets de Svelte no funcionan en MDX.** MDX es JSX. Cada secuencia de
  scrollytelling vive en un `.svelte` propio de la pieza (ver
  `ejemplo-partidas/components/FlujoScrolly.svelte`) y el artículo lo invoca con
  una etiqueta.
- **Satori no lee WOFF2** y no puede maquetar sin al menos un buffer de fuente.
- **Astro 7 usa el Content Layer API.** El plan describe `src/content/config.ts`
  con `type: 'content'`; eso se reemplazó por `src/content.config.ts` con un
  `loader: glob()`. Los esquemas son los mismos.
- **`sello` se oscureció** de `#8A9088` a `#676D65`. El valor del plan da 2,80:1
  sobre papel y su uso asignado es texto chico, que exige 4,5:1.
- **El violeta de marca no sirve como serie de gráfico:** colisiona con el azul
  bajo protanopía. Por eso las escalas de gráfico son un sistema aparte.
- **`astro build` fija `import.meta.env.PROD = true` siempre,** incluso con
  `--mode development`. Para decidir qué contenido entra al build hay que usar
  una variable propia: `DIGERIDO_EJEMPLOS` (ver `src/lib/entorno.ts`).
- **Excluir una página de `getStaticPaths` no la saca del bundle.** Mientras su
  entrada siga en la colección, Astro compila y emite el JS de sus islas. Las
  piezas de andamiaje se excluyen en el `loader`.

---

## Desplegar

Guía completa paso a paso en **[`infra/DESPLIEGUE.md`](infra/DESPLIEGUE.md)**.

```bash
# en el VPS, una sola vez
sudo ./infra/instalar-vps.sh digerido.cl deploy

# para diagnosticar cuando algo no funciona
sudo ./infra/verificar-vps.sh digerido.cl
```

El instalador detecta la versión de Nginx y los módulos disponibles antes de
escribir la configuración: tres directivas del vhost dependen de eso, y con la
variante equivocada Nginx no arranca.

**El despliegue automático se dispara con un push a `main`.** Si esa rama no
existe, el workflow nunca corre — es lo primero que hay que resolver en un
repositorio nuevo.

---

## Licencia

Texto y gráficos bajo [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es).
Los datos procesados declaran su licencia caso a caso en `/datos/`. Los
documentos originales pertenecen a sus organismos emisores: se enlazan y se
citan con hash, no se rehospedan.
