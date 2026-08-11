/**
 * Scaffolding de una digestión nueva (§10).  `pnpm nueva-digestion "Presupuesto 2027"`
 *
 * "El escalamiento del portal depende de que el costo marginal de una pieza sea
 * bajo." Este script es el que baja ese costo: crea el MDX con el frontmatter
 * completo, el componente base del gráfico, los cuatro scripts del pipeline y su
 * justfile — todo con los comentarios que recuerdan las reglas editoriales.
 *
 * Lo que NO hace: crear la rama git. El plan lo menciona, pero un script que
 * cambia de rama sin avisar sorprende en el peor momento; imprime el comando al
 * final para que sea una decisión de quien escribe.
 */
import { existsSync } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';

const RAIZ = resolve(import.meta.dirname, '..');

/** Título → slug: sin tildes, sin puntuación, palabras unidas por guión. */
function aSlug(titulo: string): string {
  return titulo
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '') // quita diacríticos
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

const titulo = process.argv.slice(2).join(' ').trim();

if (!titulo) {
  console.error(`
Uso: pnpm nueva-digestion "Título de la digestión"

Crea:
  apps/web/src/content/digestiones/<slug>/   MDX, meta.json y componentes
  pipelines/<slug>/                          los cuatro pasos y su justfile
`);
  process.exit(1);
}

const slug = aSlug(titulo);
if (!slug) {
  console.error(`No pude derivar un slug de "${titulo}".`);
  process.exit(1);
}

const dirContenido = join(RAIZ, 'apps/web/src/content/digestiones', slug);
const dirPipeline = join(RAIZ, 'pipelines', slug);

for (const d of [dirContenido, dirPipeline]) {
  if (existsSync(d)) {
    console.error(`Ya existe ${d.replace(RAIZ + '/', '')}. Elegí otro título o borralo.`);
    process.exit(1);
  }
}

const hoy = new Date().toISOString().slice(0, 10);
const claseComponente = slug
  .split('-')
  .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
  .join('');

// ─────────────────────────── contenido ───────────────────────────

const mdx = `---
titulo: '${titulo.replace(/'/g, "''")}'
# Máximo 220 caracteres. Lo que se lee bajo el título y en los metadatos.
bajada: ''
# LA FRASE ÚNICA. Una sola oración, sin jerga. Si no existe, no se publica (§2).
# El esquema rechaza más de un punto final y más de 180 caracteres.
hallazgo: ''
fecha: ${hoy}
autores: ['digerido']
# presupuesto · economia · salud · educacion · medioambiente · legislativo ·
# compras-publicas · territorio
temas: []
# 1 = legible, 5 = ilegible. Alimenta la etiqueta nutricional.
dificultadOriginal: 3
# Minutos. El esquema exige que el digerido sea MENOR que el original.
tiempoLectura:
  original: 0
  digerido: 0
# Las escribe el pipeline (30_publicar.py) y se copian de pipelines/${slug}/…/meta.json.
# No las estimes a mano: es así como se cuela un error factual (§13).
etiqueta:
  palabrasOriginal: 0
  siglasSinDefinir: 0
  legibilidadOriginal: 0
  legibilidadDigerido: 0
  graficos: 0
# Sin fuente verificable el build falla. El sha256 lo registra 00_descargar.py.
fuentes:
  - titulo: ''
    organismo: ''
    url: ''
    fechaPublicacion: ${hoy}
    fechaDescarga: ${hoy}
    sha256: ''
    formato: 'pdf'
# Publicados en /datos/ con licencia. Los produce 30_publicar.py.
datasets: []
destacada: false
# 'borrador' hasta que pase el checklist de §10. 'publicada' exige etiqueta
# completa y al menos una limitación declarada.
estado: 'borrador'
# Qué NO dice esta digestión. Obligatorio antes de publicar (§10).
limitaciones: []
# Log de correcciones público, con fecha (§13). No se edita en silencio.
correcciones: []
---

import ${claseComponente} from './components/${claseComponente}.svelte';
// import datos from '../../../../public/data/${slug}/datos.json';

{/*
  ESTRUCTURA NARRATIVA ESTÁNDAR (§10) — adaptable, no rígida.
  Borrá estos comentarios a medida que escribas.

  1. EL PLATO DE ENTRADA — la cifra o contradicción que obliga a seguir leyendo.
  2. LA MATERIA PRIMA — cómo se ve el documento tal cual. Mostrarlo feo es
     parte del argumento.
  3. EL PLATO DE FONDO — el gráfico principal, con scrollytelling si aporta.
  4. LOS APERITIVOS — el momento en que el lector busca lo suyo: su comuna,
     su sector, su año.
  5. EL POSTRE — qué significa, qué no se sabe, qué habría que preguntar.

  El paso 6 (método y fuentes) lo pone el layout. No lo escribas acá.

  ALCANCE FIJADO ANTES DE EMPEZAR (§13): 1 hallazgo, 1 gráfico principal,
  máximo 3 de apoyo. Es la única defensa contra que la pieza se vuelva un
  proyecto de tres meses.
*/}

## El plato de entrada

## La materia prima

## El plato de fondo

{/* El gráfico principal va a ancho de figura, no de texto. */}
<div class="carril-ancho">
  {/* <${claseComponente} datos={datos.filas} unidad="" client:visible /> */}
</div>

## Los aperitivos

## El postre
`;

// ─────────────────────────── componente ───────────────────────────

const componente = `<!--
  ${claseComponente}.svelte — gráfico principal de la digestión "${titulo}".

  Patrón canónico: D3 CALCULA, SVELTE RENDERIZA.
  Sin select, sin append, sin enter/exit. Svelte es dueño del DOM; D3 aporta
  escalas, formas y geografías. Importá SOLO los módulos que uses
  (d3-scale, d3-shape, d3-array, d3-geo), nunca \`d3\` completo.

  <Figura> exige título, unidades, fuente y descripción del HALLAZGO, y avisa en
  desarrollo si falta la tabla equivalente. Eso convierte el checklist de §10 en
  algo estructural en vez de una lista que hay que recordar.
-->
<script lang="ts">
  import { max } from 'd3-array';
  import { scaleBand, scaleLinear } from 'd3-scale';

  import Eje from '@digerido/kit/charts/Eje.svelte';
  import Figura from '@digerido/kit/charts/Figura.svelte';
  import TablaEquivalente from '@digerido/kit/charts/TablaEquivalente.svelte';
  import { escalaDestacado, numero } from '@digerido/kit/utils';

  interface Fila {
    categoria: string;
    valor: number;
  }

  let { datos, unidad }: { datos: Fila[]; unidad: string } = $props();

  const ANCHO = 720;
  const ALTO = 420;
  const margen = { top: 24, right: 24, bottom: 44, left: 132 };

  // ── D3 calcula ──────────────────────────────────────────────────────────
  const x = $derived(
    scaleLinear()
      .domain([0, max(datos, (d) => d.valor) ?? 0])
      .nice()
      .range([margen.left, ANCHO - margen.right]),
  );

  const y = $derived(
    scaleBand()
      .domain(datos.map((d) => d.categoria))
      .range([margen.top, ALTO - margen.bottom])
      .padding(0.24),
  );

  // Un destacado y el resto en gris: más legible que N colores, y sin tope.
  // Si de verdad necesitás series de color, usá escalaCategorica(n) — lanza
  // sobre 5, que es donde los colores dejan de distinguirse bajo dicromacia.
  const colores = $derived(escalaDestacado(datos, (_, i) => i === 0));
</script>

<Figura
  id="${slug}"
  titulo="TODO: el título afirma algo, no nombra el tipo de gráfico"
  descripcion="TODO: el HALLAZGO. Mal: 'gráfico de barras de X'. Bien: 'Salud concentra el 31 % del aumento'."
  unidades={unidad}
  fuente="TODO: organismo y documento"
>
  <svg viewBox="0 0 {ANCHO} {ALTO}" role="img" aria-label="TODO: el hallazgo">
    <Eje
      escala={x}
      lado="abajo"
      ancho={ANCHO}
      alto={ALTO}
      {margen}
      grilla
      formato={(v) => numero(v as number)}
    />
    <Eje escala={y} lado="izquierda" ancho={ANCHO} alto={ALTO} {margen} />

    {#each datos as d, i (d.categoria)}
      <rect
        x={margen.left}
        y={y(d.categoria)}
        width={Math.max(0, x(d.valor) - margen.left)}
        height={y.bandwidth()}
        fill={colores[i]}
      />
    {/each}
  </svg>

  {#snippet tabla()}
    <TablaEquivalente
      {datos}
      resumen="TODO: el mismo hallazgo, en una frase"
      columnas={[
        { llave: 'categoria', titulo: 'Categoría' },
        {
          llave: 'valor',
          titulo: \`Valor (\${unidad})\`,
          numerica: true,
          formato: (v) => numero(v as number),
        },
      ]}
    />
  {/snippet}
</Figura>
`;

// ─────────────────────────── pipeline ───────────────────────────

const paso00 = `#!/usr/bin/env python3
"""Paso 00 — descargar (§7).

Idempotente y con caché: repetir no vuelve a golpear al organismo emisor.
La salida cruda va a 'raw/', que está gitignored.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

from pipelines._common.descarga import descargar, verificar_hash
from pipelines._common.log import log

AQUI = Path(__file__).resolve().parent
CRUDO = AQUI / "raw"
SLUG = "${slug}"

# TODO: la URL del documento original.
URL = ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forzar", action="store_true", help="ignora el caché")
    args = parser.parse_args()

    if not URL:
        log.error("definí URL en este script antes de correrlo")
        return 1

    # `URL.rsplit("/", 1)[-1]` se queda con el query string (?sfvrsn=...) pegado
    # al nombre: Windows rechaza el "?" en un nombre de archivo. urlsplit().path
    # descarta query y fragment antes de tomar el último segmento.
    destino = CRUDO / urlsplit(URL).path.rsplit("/", 1)[-1]
    reg = descargar(URL, destino, forzar=args.forzar)

    # Avisa si el organismo reemplazó el documento sin cambiar la URL (§13).
    meta = AQUI.parent.parent / "apps/web/src/content/digestiones" / SLUG / "meta.json"
    if not verificar_hash(meta, URL, reg.sha256):
        return 1

    (CRUDO / "registro.json").write_text(
        json.dumps(reg.como_dict(), ensure_ascii=False, indent=2) + "\\n", encoding="utf-8"
    )
    log.info("sha256 %s", reg.sha256)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
`;

const paso10 = `#!/usr/bin/env python3
"""Paso 10 — extraer (§7).

Extrae y NO corrige: limpiar es el paso 20. Mezclar los dos hace imposible saber
si un número raro venía del documento o lo produjo el script.

Mide también el documento original para la Etiqueta Nutricional.
"""

from __future__ import annotations

import json
from pathlib import Path

from pipelines._common.legibilidad import detectar_siglas, legibilidad, tiempo_lectura
from pipelines._common.log import log

AQUI = Path(__file__).resolve().parent
CRUDO = AQUI / "raw"
INTERMEDIO = AQUI / "interim"


def extraer_texto() -> str:
    """TODO: con pdfplumber, 'pip install '.[pdf]''.

    import pdfplumber
    with pdfplumber.open(CRUDO / "documento.pdf") as pdf:
        return "\\n".join(p.extract_text() or "" for p in pdf.pages)
    """
    raise NotImplementedError("implementá la extracción de texto")


def extraer_tablas() -> list[dict]:
    """TODO: pdfplumber.extract_tables() o camelot para tablas con líneas."""
    raise NotImplementedError("implementá la extracción de tablas")


def main() -> int:
    INTERMEDIO.mkdir(parents=True, exist_ok=True)

    filas = extraer_tablas()
    (INTERMEDIO / "tabla-cruda.json").write_text(
        json.dumps(filas, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8"
    )

    texto = extraer_texto()
    leg = legibilidad(texto)
    siglas = detectar_siglas(texto)

    (INTERMEDIO / "metricas-original.json").write_text(
        json.dumps(
            {
                "palabrasOriginal": leg.palabras,
                "siglasSinDefinir": siglas.sin_definir,
                "legibilidadOriginal": leg.indice,
                "nivelOriginal": leg.nivel,
                "tiempoLecturaOriginal": tiempo_lectura(leg.palabras),
                "detalle": leg.como_dict(),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\\n",
        encoding="utf-8",
    )

    log.info(
        "legibilidad %d/100 (%s) · %d palabras · %d siglas sin definir",
        leg.indice,
        leg.nivel,
        leg.palabras,
        siglas.sin_definir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
`;

const paso20 = `#!/usr/bin/env python3
"""Paso 20 — limpiar y validar (§7).

Todo redondeo ocurre acá, nunca en el front. Si las invariantes fallan, no se
escribe nada: un dato que no pasa el test no llega al sitio.
"""

from __future__ import annotations

import json
from pathlib import Path

from pipelines._common.invariantes import en_rango, sin_duplicados_en, sin_nulos_en
from pipelines._common.log import log

AQUI = Path(__file__).resolve().parent
INTERMEDIO = AQUI / "interim"


def main() -> int:
    cruda = INTERMEDIO / "tabla-cruda.json"
    if not cruda.exists():
        log.error("falta %s. Corré 10_extraer.py primero.", cruda.name)
        return 1

    filas = json.loads(cruda.read_text(encoding="utf-8"))

    # TODO: normalizar nombres, códigos territoriales, unidades y año base.
    limpias = [
        {
            "categoria": str(f["categoria"]).strip(),
            "valor": round(float(f["valor"]), 1),
        }
        for f in filas
    ]

    # TODO: agregá las invariantes propias de este dataset.
    #   total_cuadra(limpias, "valor", total_del_documento)
    #   codigos_comuna_validos(limpias, "comuna")
    #   fechas_en_ventana(limpias, "fecha", "2020-01-01", "2030-12-31")
    problemas: list[str] = []
    problemas += sin_nulos_en(limpias, ["categoria", "valor"])
    problemas += sin_duplicados_en(limpias, ["categoria"])
    problemas += en_rango(limpias, "valor", 0, float("inf"))

    if problemas:
        log.error("las invariantes fallaron; no se escribe nada:")
        for p in problemas[:20]:
            log.error("  %s", p)
        return 1

    (INTERMEDIO / "tabla-limpia.json").write_text(
        json.dumps(limpias, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8"
    )
    log.info("%d filas limpias, invariantes en verde", len(limpias))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
`;

const paso30 = `#!/usr/bin/env python3
"""Paso 30 — publicar (§7).

Único paso que escribe dentro de 'apps/web'. Los tamaños, hashes y conteos del
meta.json los escribe este script: copiarlos a mano es cómo se cuela el error
factual que §13 identifica como el riesgo más caro del proyecto.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from pipelines._common.log import log
from pipelines._common.publicar import escribir_meta, publicar_csv, publicar_json

AQUI = Path(__file__).resolve().parent
CRUDO = AQUI / "raw"
INTERMEDIO = AQUI / "interim"

SLUG = "${slug}"


def main() -> int:
    limpia = INTERMEDIO / "tabla-limpia.json"
    if not limpia.exists():
        log.error("falta %s. Corré 20_limpiar.py primero.", limpia.name)
        return 1

    filas = json.loads(limpia.read_text(encoding="utf-8"))
    metricas = json.loads((INTERMEDIO / "metricas-original.json").read_text(encoding="utf-8"))
    registro = json.loads((CRUDO / "registro.json").read_text(encoding="utf-8"))

    # TODO: declarar la unidad y el año base. Una cifra fiscal sin ellos no
    # significa nada, y el gráfico los muestra en el figcaption.
    datos = {"unidad": "TODO", "filas": filas}

    artefactos = [
        publicar_json(datos, f"{SLUG}/datos.json", filas=len(filas)),
        publicar_csv(filas, f"{SLUG}/datos.csv"),
    ]

    escribir_meta(
        SLUG,
        {
            "slug": SLUG,
            "generado": date.today().isoformat(),
            "fuente": registro,
            "etiqueta": metricas,
            "artefactos": [a.como_dict() for a in artefactos],
        },
    )

    log.info(
        "listo. Copiá al frontmatter: palabrasOriginal=%s, legibilidadOriginal=%s, "
        "siglasSinDefinir=%s, tiempoLectura.original=%s",
        metricas["palabrasOriginal"],
        metricas["legibilidadOriginal"],
        metricas["siglasSinDefinir"],
        metricas["tiempoLecturaOriginal"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
`;

const testsPipeline = `"""Invariantes del dataset de "${titulo}" (§7).

"Un dato que no pasa el test no llega al sitio."

Escribí acá lo que TIENE que ser cierto de estos datos, no lo que es cierto hoy.
Un test que solo confirma el output actual no protege de nada; uno que codifica
una regla del dominio atrapa el día que la fuente cambia de formato.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipelines._common.invariantes import (
    en_rango,
    reportar,
    sin_duplicados_en,
    sin_nulos_en,
)

RAIZ = Path(__file__).resolve().parents[3]
SLUG = "${slug}"
ARTEFACTO = RAIZ / "apps" / "web" / "public" / "data" / SLUG / "datos.json"


@pytest.fixture(scope="module")
def datos() -> dict:
    if not ARTEFACTO.exists():
        pytest.skip(f"falta {ARTEFACTO}; corré el pipeline")
    return json.loads(ARTEFACTO.read_text(encoding="utf-8"))


def test_declara_unidad(datos: dict) -> None:
    """Una cifra sin unidad ni año base no significa nada (§10)."""
    assert datos["unidad"] and datos["unidad"] != "TODO"


def test_llaves_completas(datos: dict) -> None:
    reportar(sin_nulos_en(datos["filas"], ["categoria", "valor"]), "datos.json")


def test_sin_duplicados(datos: dict) -> None:
    reportar(sin_duplicados_en(datos["filas"], ["categoria"]), "datos.json")


def test_valores_plausibles(datos: dict) -> None:
    # TODO: acotá al rango que este dominio admite de verdad.
    reportar(en_rango(datos["filas"], "valor", 0, float("inf")), "datos.json")


# TODO: el test que importa.
#
#   def test_total_cuadra_con_el_documento(datos):
#       reportar(total_cuadra(datos["filas"], "valor", TOTAL_DEL_DOCUMENTO))
#
# Es la comprobación que detecta una extracción mal alineada, y la que más veces
# salva una digestión de publicar una cifra equivocada.
`;

const justfile = `# Pipeline de la digestión \`${slug}\`.
#
# Correr desde la raíz:  just -f pipelines/${slug}/justfile todo

raiz := justfile_directory() / "../.."
py := "python3"

default:
    @just --list --unsorted -f "{{ justfile() }}"

# Pipeline completo: descargar → extraer → limpiar → validar → publicar.
todo: descargar extraer limpiar test publicar
    @echo "listo. Actualizá el frontmatter con las métricas del meta.json."
    @echo "próximo paso: just -f pipelines/${slug}/justfile redactar"

descargar *args:
    cd "{{ raiz }}" && {{ py }} -m pipelines.${slug}.00_descargar {{ args }}

extraer:
    cd "{{ raiz }}" && {{ py }} -m pipelines.${slug}.10_extraer

limpiar:
    cd "{{ raiz }}" && {{ py }} -m pipelines.${slug}.20_limpiar

publicar:
    cd "{{ raiz }}" && {{ py }} -m pipelines.${slug}.30_publicar

# Bloquean la publicación.
test:
    cd "{{ raiz }}" && {{ py }} -m pytest pipelines/${slug}/tests -q

# Revalida el hash de la fuente contra el registrado (§13).
revalidar:
    cd "{{ raiz }}" && {{ py }} -m pipelines.${slug}.00_descargar --forzar

# Paso final (asistido) — propuesta de artículo con el agente redactor-digestion.
# No es un script: el agente vive en .claude/agents/ y solo corre dentro de una
# sesión de Claude Code (no tiene forma de invocarse desde una terminal sola).
# Esta receta existe para que "el siguiente paso" quede documentado en el mismo
# lugar que el resto del pipeline, en vez de solo en la cabeza de quien escribe.
redactar:
    @echo "Este paso no corre solo: abrí una sesión de Claude Code en la raíz del repo y pedile"
    @echo ""
    @echo "  Usa el agente redactor-digestion para el slug ${slug}"
    @echo ""
    @echo "El agente lee pipelines/${slug}/raw/ e interim/, y te muestra 3 opciones de"
    @echo "cada sección narrativa en pipelines/${slug}/PROPUESTA-ARTICULO.md para que"
    @echo "elijas antes de que escriba el index.mdx definitivo."

# Borra intermedios, conserva las descargas crudas.
limpiar-cache:
    rm -rf "{{ justfile_directory() }}/interim"
`;

const checklist = `# Checklist de publicación — ${titulo}

Bloquea el merge (§10). Marcá cada ítem cuando esté hecho de verdad.

- [ ] \`hallazgo\` escrito en una frase, sin jerga.
- [ ] Fuente con URL, fecha de descarga y hash registrados.
- [ ] Datos verificados contra el documento original **por una segunda pasada**.
- [ ] Tests del pipeline en verde (\`just -f pipelines/${slug}/justfile test\`).
- [ ] Todo gráfico tiene título, unidades, fuente y anotación.
- [ ] Tabla equivalente accesible presente en cada gráfico.
- [ ] Todo gráfico tiene un nivel real de interacción (scroll o clic) — nunca
      es una imagen estática (referencia: pudding.cool).
- [ ] Si el hallazgo trata directamente de personas (no de instituciones ni
      montos abstractos), se evaluó un \`Pictograma\` (dibujos de personas)
      además de o en vez del gráfico de barras/líneas por defecto.
- [ ] Probado en móvil real, no solo en el emulador.
- [ ] Presupuesto de rendimiento respetado (\`pnpm build && pnpm presupuesto\`).
- [ ] Datasets publicados en \`/datos/\` con licencia.
- [ ] Errores conocidos y limitaciones declarados al final.

## Antes de empezar a escribir

Alcance fijado (§13): **1 hallazgo, 1 gráfico principal, máximo 3 de apoyo.**

- Hallazgo en una frase: ______________________________________________
- Gráfico principal (qué muestra): ____________________________________
- Qué queda deliberadamente afuera: ___________________________________

## Verificación manual

- [ ] Con \`prefers-reduced-motion\`, el scrollytelling degrada a gráficos
      apilados legibles — no a una pantalla en blanco.
- [ ] Sin JavaScript, el texto y los gráficos siguen ahí.
- [ ] Toda la página se recorre con teclado, con foco visible.
- [ ] Ningún dato se comunica solo por color.
`;

// ─────────────────────────── escritura ───────────────────────────

await mkdir(join(dirContenido, 'components'), { recursive: true });
await mkdir(join(dirPipeline, 'tests'), { recursive: true });

const archivos: Array<[string, string]> = [
  [join(dirContenido, 'index.mdx'), mdx],
  [join(dirContenido, 'components', `${claseComponente}.svelte`), componente],
  [join(dirPipeline, '__init__.py'), ''],
  [join(dirPipeline, '00_descargar.py'), paso00],
  [join(dirPipeline, '10_extraer.py'), paso10],
  [join(dirPipeline, '20_limpiar.py'), paso20],
  [join(dirPipeline, '30_publicar.py'), paso30],
  [join(dirPipeline, 'tests', 'test_invariantes.py'), testsPipeline],
  [join(dirPipeline, 'justfile'), justfile],
  [join(dirPipeline, 'CHECKLIST.md'), checklist],
];

for (const [ruta, contenido] of archivos) {
  await writeFile(ruta, contenido, 'utf8');
}

console.log(`
Digestión "${titulo}" creada.

  contenido   apps/web/src/content/digestiones/${slug}/
  pipeline    pipelines/${slug}/
  checklist   pipelines/${slug}/CHECKLIST.md

Siguiente:

  1. Poné la URL del documento en pipelines/${slug}/00_descargar.py
  2. just -f pipelines/${slug}/justfile todo
  3. Copiá las métricas del meta.json al frontmatter del MDX
  4. just -f pipelines/${slug}/justfile redactar
     (te dice cómo pedirle al agente redactor-digestion una propuesta de
     artículo en pipelines/${slug}/PROPUESTA-ARTICULO.md)
  5. Escribí el hallazgo ANTES del artículo. Si no sale en una frase,
     todavía no hay pieza.

Rama sugerida:

  git checkout -b digestion/${slug}
`);
