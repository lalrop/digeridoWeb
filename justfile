# digerido — tareas de la raíz.  `just` lista todo.
#
# Los pipelines tienen su propio justfile por digestión; este cubre el repo.

py := "python3"

default:
    @just --list --unsorted

# ── Desarrollo ──────────────────────────────────────────────────────────────

# Servidor de desarrollo.
dev: tokens
    pnpm dev

# Instala dependencias de JS y Python.
instalar:
    pnpm install
    {{ py }} -m pip install -e '.[dev]'

# Genera dist/tokens.css desde los módulos TS.
tokens:
    pnpm -F @digerido/tokens build

# ── Verificación ────────────────────────────────────────────────────────────

# Todo lo que corre en CI, en el mismo orden.
verificar: lint test typecheck build presupuesto
    @echo "todo en verde"

lint:
    ruff check pipelines scripts

# Tests de JS y de pipelines. Incluye la verificación de la paleta contra
# deuteranopía y protanopía.
test:
    pnpm -r test
    {{ py }} -m pytest pipelines -q

typecheck:
    pnpm -r typecheck

build: tokens
    pnpm -F @digerido/web build

# Presupuesto de §8 sobre dist/. Falla si se excede.
presupuesto:
    pnpm presupuesto

# Lighthouse: LCP y CLS, que solo se miden ejecutando.
lighthouse: build
    npx --yes @lhci/cli@0.14.x autorun

# ── Contenido ───────────────────────────────────────────────────────────────

# Andamiaje de una digestión nueva.
nueva titulo:
    pnpm nueva-digestion "{{ titulo }}"

# Compara el hash de cada fuente contra el registrado (§13).
revalidar:
    {{ py }} scripts/revalidar_fuentes.py

# Busca paletas categóricas seguras bajo dicromacia.
paleta:
    pnpm -F @digerido/tokens explorar

# ── Limpieza ────────────────────────────────────────────────────────────────

# Borra artefactos de build. NO toca pipelines/*/raw/: volver a bajar un
# documento de 400 páginas por limpiar un dist/ es un desperdicio.
limpiar:
    rm -rf apps/web/dist apps/web/.astro packages/tokens/dist .lighthouseci
    find . -name __pycache__ -not -path './node_modules/*' -exec rm -rf {} +
    @echo "dist/ y cachés borrados; pipelines/*/raw/ intacto"
