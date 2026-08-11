# Cómo agregar una digestión nueva (y que aparezca en la Despensa)

Guía paso a paso, sin dar por sabido nada. Al final vas a tener una pieza
publicada en **https://digerido.cl** con sus datos descargables en
**https://digerido.cl/datos/** (la Despensa).

**Tiempo:** varía mucho según el documento (de un día a varias semanas si hay
que extraer tablas de un PDF complicado). El propio checklist del proyecto fija
el alcance para que no se vuelva un proyecto eterno: **1 hallazgo, 1 gráfico
principal, máximo 3 de apoyo.**

---

## Lo primero que hay que entender: la Despensa no se llena a mano

No existe un botón ni un formulario para "agregar un dataset". La Despensa
(`/datos/`) se arma **automáticamente** a partir del campo `datasets:` del
frontmatter de cada digestión, leyendo solo las que están `estado: 'publicada'`
(`apps/web/src/lib/digestiones.ts`, función `despensa()`). Así que:

```
No hay forma de que la Despensa y los artículos discrepen,
porque la Despensa ES una vista de los artículos.
```

Para que algo aparezca ahí, tenés que publicar una digestión completa que
declare ese dataset en su frontmatter. Esta guía cubre el camino entero.

---

## El camino completo, de un vistazo

```
pnpm nueva-digestion "Título"    → crea el andamiaje (MDX + pipeline)
        ↓
completar pipelines/<slug>/*.py  → 00 descargar · 10 extraer · 20 limpiar · 30 publicar
        ↓
30_publicar.py escribe            apps/web/public/data/<slug>/*.json|csv
                                   apps/web/src/content/digestiones/<slug>/meta.json
        ↓
completar el frontmatter del MDX  (copiando del meta.json, nunca a mano)
        ↓
just -f pipelines/<slug>/justfile redactar   → agente redactor-digestion propone
                                                pipelines/<slug>/PROPUESTA-ARTICULO.md
                                                (3 opciones por sección; solo corre
                                                dentro de una sesión de Claude Code)
        ↓
elegir opciones y escribir el artículo   (el hallazgo, el gráfico, la exploración)
        ↓
verificar en local                pnpm dev · pnpm test · pnpm build · presupuesto
        ↓
estado: 'publicada'  +  checklist cumplido
        ↓
git push a main                   → CI construye, testea, mide Lighthouse y despliega
        ↓
https://digerido.cl/datos/ tiene el dataset nuevo (~3 minutos después del push)
```

---

## Paso 1 · Preparar el entorno (una sola vez)

### -1. El proyecto NO puede vivir en una carpeta sincronizada (Google Drive, OneDrive, Dropbox)

Esto no es una preferencia, es un bloqueo real: `apps/web` depende de
`packages/tokens` y `packages/kit` del mismo monorepo, y `pnpm` **siempre**
crea un symlink de directorio para esas dependencias internas al instalar —
no hay ninguna combinación de `node-linker`, `injectWorkspacePackages` ni
`dependenciesMeta.injected` que lo evite (se probaron las tres). Las unidades
virtuales de Google Drive (y similares) no soportan symlinks de directorio, y
`pnpm install` termina siempre con `EISDIR: illegal operation on a directory,
symlink`.

Cloná o movés el proyecto a una carpeta en un disco local de verdad, por
ejemplo `C:\Users\<vos>\Desarrollos\digerido`. El repo sigue viviendo en
GitHub igual — mover la carpeta local no pierde nada, solo deja de
sincronizarse con Drive.

### 0. Instalar `just`

Todos los comandos de esta guía usan **`just`**, el ejecutor de tareas del
proyecto (no es el `pnpm` de siempre — es un programa aparte, chiquito, que
lee los archivos `justfile`). Comprobá si ya lo tenés:

```bash
just --version
```

Si da "no se reconoce el término" o "command not found", instalalo:

- **Windows (PowerShell):** `winget install --id Casey.Just -e`
- **Mac:** `brew install just`
- **Linux:** `cargo install just`, o el paquete `just` de tu distro

**Importante:** después de instalarlo, **cerrá la terminal y abrí una
nueva** (o abrí una pestaña nueva). Windows no actualiza el `PATH` de una
ventana que ya estaba abierta antes de la instalación — si corrés `just` en
la misma ventana donde lo instalaste, va a seguir sin encontrarlo aunque la
instalación haya sido exitosa.

### 0.1. Windows además necesita `sh` y un Python de verdad en el PATH

`just` corre cada receta con un shell POSIX (`sh`), que no viene con Windows
pero sí con Git for Windows — solo que en una carpeta que la instalación no
agrega al `PATH` por defecto. Si `just instalar` falla con `program not
found: sh`, agregá `C:\Program Files\Git\bin` al PATH de tu usuario
(Configuración → Variables de entorno, o `[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;C:\Program Files\Git\bin", "User")`
en PowerShell) y abrí una terminal nueva.

Por separado, comprobá que `python3 --version` devuelve una versión real y no
un mensaje sobre instalar desde la Microsoft Store — ese acceso directo
("alias de ejecución de aplicaciones") es un placeholder, no Python. Si te
pasa eso, instalá Python 3.11+ de verdad (`winget install Python.Python.3.13`
o desde python.org) y asegurate de que su carpeta quede **antes** que
`AppData\Local\Microsoft\WindowsApps` en el PATH — si no, el alias falso
sigue ganando aunque Python ya esté instalado.

### 1. Instalar las dependencias del proyecto

```bash
cd "C:/Users/<vos>/Desarrollos/digerido"
just instalar
```

Esto corre `pnpm install` y `pip install -e '.[dev]'`.

Comprobá que el pipeline corre:

```bash
just verificar
```

**Deberías ver** `todo en verde` al final. Si algo falla acá, arreglalo antes
de seguir — son los mismos checks que corre GitHub Actions.

---

## Paso 2 · Crear el andamiaje

```bash
pnpm nueva-digestion "Título de la digestión"
```

El título es libre, en español, tal como va a aparecer publicado. El script
deriva un `slug` (sin tildes, en minúsculas, con guiones) y crea:

```
apps/web/src/content/digestiones/<slug>/
  index.mdx                  frontmatter completo + estructura narrativa
  components/<Slug>.svelte   gráfico principal, patrón D3-calcula/Svelte-renderiza

pipelines/<slug>/
  00_descargar.py            baja el documento original, con caché y hash
  10_extraer.py               texto y tablas crudas + métricas de legibilidad
  20_limpiar.py                redondeo y validación; no escribe nada si falla
  30_publicar.py                único paso que escribe dentro de apps/web
  tests/test_invariantes.py    bloquea la publicación si los datos no cuadran
  justfile                      just -f pipelines/<slug>/justfile todo
  CHECKLIST.md                  el checklist de §10, con el slug ya puesto
```

**Deberías ver** un mensaje con los próximos pasos y la rama sugerida. Creala
si vas a trabajar más de una sesión:

```bash
git checkout -b digestion/<slug>
```

---

## Paso 3 · Completar el pipeline

Los cuatro pasos son plantillas con `TODO` explícitos. En orden:

### 00 — descargar

Abrí `pipelines/<slug>/00_descargar.py` y poné la `URL` del documento
original. Es lo único obligatorio en este paso; el resto (caché, reintentos,
hash) ya está resuelto por `pipelines/_common/descarga.py`.

### 10 — extraer

Implementá `extraer_texto()` y `extraer_tablas()`. Para PDF, el comentario del
archivo trae el ejemplo con `pdfplumber` (`pip install -e '.[pdf]'`); para
tablas con líneas visibles, a veces `camelot` da mejor resultado que
`pdfplumber.extract_tables()`. Este paso también mide la legibilidad del
documento original — no hay que tocar esa parte.

### 20 — limpiar

Acá va la normalización real: nombres, códigos territoriales, unidades, año
base. **Todo redondeo ocurre acá, nunca en el front.** Agregá las invariantes
propias del dataset usando `pipelines/_common/invariantes.py`:

| Función | Para qué |
|---|---|
| `sin_nulos_en(filas, llaves)` | Ninguna llave clave puede venir vacía |
| `sin_duplicados_en(filas, llaves)` | La llave compuesta debe ser única |
| `total_cuadra(filas, campo, total)` | La suma de las partes contra el total declarado |
| `en_rango(filas, campo, min, max)` | Valores dentro de un rango plausible |
| `codigos_comuna_validos(filas, campo)` | Códigos de la división político-administrativa chilena |
| `fechas_en_ventana(filas, campo, desde, hasta)` | Fechas dentro de un rango razonable |

Si las invariantes fallan, el script **no escribe nada**: un dato que no pasa
el test no llega al sitio.

### 30 — publicar

Declará la `unidad` y el año base de los datos. Este paso llama a
`publicar_json()` / `publicar_csv()`, que escriben en
`apps/web/public/data/<slug>/` y devuelven tamaño, filas y hash de cada
archivo — y a `escribir_meta()`, que junta todo eso en el `meta.json` de la
digestión. **No copies tamaños ni hashes a mano en ningún lado**: es
exactamente así como se cuela un error factual (§13).

### Correrlo

```bash
just -f pipelines/<slug>/justfile todo
```

Corre los cuatro pasos en orden y los tests. **Deberías ver** al final algo
como:

```
listo. Copiá al frontmatter: palabrasOriginal=171605, legibilidadOriginal=37,
siglasSinDefinir=4, tiempoLectura.original=858
```

Guardá esos números — van al frontmatter en el paso siguiente.

---

## Paso 4 · Completar el frontmatter — esta es la parte que llena la Despensa

Abrí `apps/web/src/content/digestiones/<slug>/index.mdx` y completá cada
campo. El esquema completo está en `apps/web/src/content.config.ts`; los
puntos que importan:

- **`hallazgo`**: UNA frase (el esquema rechaza más de un punto final), entre
  20 y 180 caracteres. Si no sale en una frase, todavía no hay pieza.
- **`etiqueta`**: los números que imprimió `just ... todo` en el paso
  anterior. `legibilidadDigerido` tiene que ser mayor que
  `legibilidadOriginal`, y `tiempoLectura.digerido` menor que `.original` — el
  esquema lo exige.
- **`fuentes`**: al menos una, con `sha256` de 64 caracteres hex (lo escribió
  `00_descargar.py` en `pipelines/<slug>/raw/registro.json`).

### El bloque que importa para esta guía: `datasets`

Abrí `apps/web/src/content/digestiones/<slug>/meta.json` (lo escribió
`30_publicar.py`) y mirá su array `artefactos`. Cada entrada trae `archivo`,
`bytes`, `filas` y `sha256`. Por cada artefacto que quieras ofrecer para
descarga en la Despensa, agregá una entrada en `datasets:` del frontmatter:

```yaml
datasets:
  - nombre: 'Partidas de ejemplo'          # nombre legible, lo elegís vos
    archivo: 'ejemplo/partidas.json'       # el mismo "archivo" del meta.json
    licencia: 'CC BY 4.0'                  # default si no lo ponés
    descripcion: 'Ocho partidas sintéticas con monto y variación anual.'
    filas: 8                               # copiado del meta.json
    bytes: 1134                            # copiado del meta.json
```

`nombre`, `licencia` y `descripcion` los escribís vos (son criterio editorial,
no algo que el pipeline pueda inferir); `archivo`, `filas` y `bytes` se copian
tal cual del `meta.json` — no se inventan ni se recalculan a mano. Un dataset
que no está en este array **no aparece en la Despensa**, aunque el archivo
exista en `public/data/`.

---

## Paso 5 · Escribir el artículo

Antes de escribir a mano, podés pedirle una propuesta al agente
`redactor-digestion` (`.claude/agents/redactor-digestion.md`):

```bash
just -f pipelines/<slug>/justfile redactar
```

Esto solo imprime instrucciones — el agente vive en `.claude/agents/` y
corre dentro de una sesión de Claude Code, no desde una terminal sola. Ahí
adentro, pedile:

```
Usa el agente redactor-digestion para el slug <slug>
```

El agente lee el documento original en `raw/` y los datos ya limpios en
`interim/`, y escribe `pipelines/<slug>/PROPUESTA-ARTICULO.md` con una
propuesta de `hallazgo`, `bajada` y `limitaciones`, más **3 versiones
distintas de cada una de las cinco secciones narrativas** para que elijas
antes de que toque `index.mdx`. Nunca inventa cifras (todo número sale de
`interim/` o de una cita textual del documento) y nunca marca la pieza como
`estado: 'publicada'` — sigue siendo un borrador para revisión humana, igual
que si lo hubieras escrito vos.

El MDX generado ya trae la estructura narrativa estándar como comentario:

1. **El plato de entrada** — la cifra o contradicción que obliga a seguir
   leyendo.
2. **La materia prima** — cómo se ve el documento tal cual (mostrarlo feo es
   parte del argumento).
3. **El plato de fondo** — el gráfico principal, con scrollytelling si aporta.
4. **Los aperitivos** — el momento en que el lector busca lo suyo.
5. **El postre** — qué significa, qué no se sabe, qué habría que preguntar.

El método y las fuentes los agrega el layout solo; no los escribas en el MDX.

Reglas que el sistema impone (no hace falta memorizarlas, avisan si algo
falta):

- El componente `<Figura>` del kit exige título, unidades, fuente y una
  descripción que comunique el **hallazgo**, no el tipo de gráfico (avisa en
  desarrollo si el texto empieza con «gráfico de…»).
- Todo gráfico necesita su tabla equivalente accesible (`<TablaEquivalente>`).
- El scrollytelling **no se escribe en el MDX** — MDX es JSX y la sintaxis de
  snippets de Svelte no es válida ahí. Vive en un `.svelte` propio de la pieza
  (mirá `ejemplo-partidas/components/FlujoScrolly.svelte`) y el artículo lo
  invoca con una sola etiqueta. Máximo 6 pasos; `<Scrolly>` avisa si te pasás.
- Máximo 5 series categóricas en un gráfico (`escalaCategorica()` lanza sobre
  5 — es donde los colores dejan de distinguirse bajo dicromacia).

### El gráfico principal: siempre interactivo, nunca estático

digerido.cl toma como referencia www.pudding.cool: ningún gráfico es una
imagen quieta al lado del texto. El agente `disenador-visualizaciones`
(`.claude/agents/disenador-visualizaciones.md`) diseña el componente
Svelte/D3 de la pieza a partir del hallazgo que ya eligió `redactor-digestion`
(lee `PROPUESTA-ARTICULO.md` o el `index.mdx`), con dos reglas que no se
negocian:

- **Interacción real**, por scrollytelling (`Scrolly`/`Paso` del kit) o por
  hover/clic con tooltip accesible por teclado (mirá
  `FlujoPartidas.svelte`) — nunca un SVG sin ningún `onfocus`/`onmouseenter`.
- **Dibujos de personas cuando el hallazgo es sobre gente**:
  `@digerido/kit/charts/Pictograma.svelte` dibuja una grilla de figuras
  humanas (isotype), con un grupo destacado sobre el resto en gris, para
  cifras como personas desempleadas, afiliadas o afectadas. No reemplaza
  todo gráfico —para instituciones, montos o territorios seguí con
  barras/líneas— pero es la primera opción a evaluar cuando la unidad del
  hallazgo es la persona.

Invocalo con:

```
Usa el agente disenador-visualizaciones para el slug <slug>
```

---

## Paso 6 · Verificar en local antes de publicar

```bash
pnpm dev
```

En desarrollo se muestra **todo**, incluidos borradores — así que podés
revisar `/datos/` en `http://localhost:4321/datos/` y confirmar que tu dataset
aparece, aunque la digestión siga en `estado: 'borrador'`. Es la forma más
rápida de comprobar que el bloque `datasets:` quedó bien escrito, antes de
tocar el estado de publicación.

Después, corré lo mismo que corre CI:

```bash
just verificar
```

(`lint`, `test` de JS y de pipelines, `typecheck`, `build`, `presupuesto`).

> **Sin las fuentes de marca, `build` falla al generar `/og/portal.png`** —
> es esperado, no un bug: las fuentes con licencia no viajan en el repo (ver
> README). `lint`, `test` y `typecheck` sí corren completos sin ellas, que es
> lo que de verdad hace falta para escribir contenido. El build real (con
> fuentes) lo hace CI en cada push a `main`.

Si querés medir el presupuesto de rendimiento con una isla hidratada de tu
pieza nueva (las piezas en borrador no se incluyen en un build normal):

```bash
DIGERIDO_EJEMPLOS=1 pnpm build && pnpm presupuesto
```

Y lo que ninguna prueba automática reemplaza — está en el
`CHECKLIST.md` que se generó junto con tu pipeline:

- [ ] Datos verificados contra el documento original **por una segunda
      pasada** (no la misma persona que extrajo).
- [ ] `prefers-reduced-motion` activo: el scrollytelling se convierte en
      gráficos apilados legibles, nunca en una pantalla en blanco.
- [ ] Sin JavaScript, el texto y los gráficos siguen ahí.
- [ ] Toda la página se recorre con teclado, con foco visible.
- [ ] Probado en un teléfono real, no solo en el emulador.
- [ ] Ningún dato se comunica solo por color.

---

## Paso 7 · Marcar como publicada

Cuando el checklist esté cumplido de verdad, en el frontmatter:

```yaml
estado: 'publicada'
```

El esquema exige, solo para este estado, que además tengas:

- `etiqueta` completa (no puede faltar).
- Al menos una entrada en `limitaciones` (si de verdad no hay ninguna, hay
  que decirlo explícitamente ahí en vez de dejar la lista vacía).
- `demo` en `false` (u omitido) — una pieza con datos sintéticos no puede
  quedar publicada, el esquema la rechaza.

Si algo falta, `pnpm build` (o el CI) va a fallar señalando exactamente qué
campo es.

---

## Paso 8 · Publicar

```bash
git add apps/web/src/content/digestiones/<slug> \
        apps/web/public/data/<slug> \
        pipelines/<slug>
git commit -m "feat(digestion): <slug>"
git push -u origin digestion/<slug>
```

Abrí un PR a `main` (o pusheá directo a `main` si trabajás solo — el mismo
flujo que ya usamos para el deploy). El workflow `verificar y desplegar`
corre automáticamente:

```
✓ tests de pipeline   (pytest sobre pipelines/, incluida tu carpeta nueva)
✓ build y presupuesto (typecheck, tests de JS, build, presupuesto de rendimiento)
✓ lighthouse          (LCP, CLS, accesibilidad, sobre tu pieza si es la destacada)
✓ desplegar al VPS    (rsync + symlink atómico, ~3 minutos desde el push a main)
```

Si algún paso falla, el sitio en vivo **no se toca** — queda la versión
anterior intacta hasta que se corrija y se vuelva a pushear.

---

## Paso 9 · Confirmar en producción

```bash
curl -s https://digerido.cl/datos/ | grep -o '<h2>Datasets</h2>'
```

O simplemente abrí **https://digerido.cl/datos/** y buscá el nombre que le
pusiste en `datasets[].nombre`. También podés correr el diagnóstico general
del servidor si algo se ve raro:

```bash
ssh root@<IP> "cd /opt/digerido && sudo ./infra/verificar-vps.sh digerido.cl"
```

---

## Si el organismo reemplaza el documento después

El job semanal `revalidar-fuentes.yml` compara el hash contra el registrado y
abre un *issue* si cambió (y notifica por `NTFY_URL` si está configurado). No
se corrige el dato en silencio: se agrega una entrada a `correcciones:` en el
frontmatter, con fecha y descripción — es el log público de correcciones de
§13.

Para revalidar a mano:

```bash
just -f pipelines/<slug>/justfile revalidar
# o, para todas las fuentes del sitio:
python3 scripts/revalidar_fuentes.py
```

---

## Errores comunes

| Lo que ves | Qué pasa | Cómo se arregla |
|---|---|---|
| El build falla: «el hallazgo debe ser UNA frase» | Hay más de un punto final en `hallazgo` | Reescribilo como una sola oración |
| El build falla: «una digestión publicada necesita las métricas de la Etiqueta Nutricional» | `etiqueta` falta o está incompleta con `estado: 'publicada'` | Completá los 5 campos, copiados del `meta.json` |
| El build falla: «una pieza con datos sintéticos no puede quedar en estado "publicada"» | `demo: true` junto con `estado: 'publicada'` | Es una regla, no un bug: sacá `demo` o dejá `estado: 'borrador'` |
| El build falla: «el texto digerido debería ser más legible que el original» | `etiqueta.legibilidadDigerido <= legibilidadOriginal` | Revisá que copiaste los números del pipeline correcto y no al revés |
| El dataset no aparece en `/datos/` en producción, aunque el archivo existe en `public/data/` | Falta la entrada en `datasets:` del frontmatter, o la digestión no está `estado: 'publicada'` | La Despensa lee el frontmatter, no la carpeta `public/data/` directamente |
| El dataset aparece en local pero no en producción | La pieza sigue en `borrador` — en `pnpm dev` se ve todo, en build de producción no | Cambiá a `estado: 'publicada'` cuando esté lista |
| `pytest pipelines` falla con invariantes | Los datos no cumplen una regla que vos mismo definiste en `20_limpiar.py` o en los tests | Es el sistema funcionando: revisá la extracción antes de forzar el dato |
| `sha256` del frontmatter no tiene 64 caracteres | Se copió a mano en vez de leerlo de `raw/registro.json` | Copialo tal cual de ahí; nunca se escribe a ojo |

---

## Referencia rápida de comandos

| Comando | Qué hace |
|---|---|
| `pnpm nueva-digestion "Título"` | Crea el andamiaje completo |
| `just -f pipelines/<slug>/justfile todo` | Corre el pipeline de punta a punta |
| `just -f pipelines/<slug>/justfile test` | Solo las invariantes de esa digestión |
| `just -f pipelines/<slug>/justfile revalidar` | Vuelve a chequear el hash de la fuente |
| `just -f pipelines/<slug>/justfile redactar` | Explica cómo pedirle al agente `redactor-digestion` la propuesta de artículo (solo dentro de Claude Code) |
| `pnpm dev` | Previsualiza todo, incluidos borradores |
| `just verificar` | Lo mismo que corre CI, local |
| `DIGERIDO_EJEMPLOS=1 pnpm build` | Build que incluye piezas de andamiaje/borrador |
