# Checklist de publicación — Informe de Percepciones de Negocios (IPN) agosto 2026

Bloquea el merge (§10). Marcá cada ítem cuando esté hecho de verdad.

- [x] `hallazgo` escrito en una frase, sin jerga.
- [x] Fuente con URL, fecha de descarga y hash registrados.
- [x] Datos verificados contra el documento original **por una segunda pasada**
      (cifras de `datos.json` recalculadas desde cero contra el Excel crudo:
      3% / 3,5% / 3,5% a 24 meses y 78,88% de combustible coinciden exacto).
- [x] Tests del pipeline en verde (12/12; `just` no está disponible en esta
      máquina, se corrió `python -m pytest pipelines/.../tests` directo).
- [x] Todo gráfico tiene título, unidades, fuente y anotación.
- [x] Tabla equivalente accesible presente en cada gráfico.
- [x] Todo gráfico tiene un nivel real de interacción (scroll o clic) — nunca
      es una imagen estática (referencia: pudding.cool).
- [x] Si el hallazgo trata directamente de personas (no de instituciones ni
      montos abstractos), se evaluó un `Pictograma`. *(El hallazgo principal
      es una tasa de inflación, no personas — se usó línea de tiempo. El
      gráfico de apoyo de combustibles usó Pictograma en una primera
      versión; se cambió a barras con color divergente para no repetir el
      mismo recurso visual que ya usa la digestión de la encuesta de
      empleo — ver `correcciones` más abajo si aplica.)*
- [x] Probado en móvil real, no solo en el emulador. Confirmado por el
      usuario ("me gusta").
- [x] Presupuesto de rendimiento respetado (`DIGERIDO_EJEMPLOS=1 pnpm -F
      @digerido/web build && pnpm presupuesto`): JS del shell 31,4/40 KB, JS
      total con islas 45,5/150 KB, primera vista 53,1/500 KB — los tres en
      verde. (`pnpm build` sin esa variable falla en `/og/portal.png` por
      falta de fuentes de marca en esta máquina; es una limitación local
      documentada en el README, no de esta pieza — CI sí tiene las fuentes.)
- [x] Datasets publicados en `/datos/` con licencia.
- [x] Errores conocidos y limitaciones declarados al final.

## Antes de empezar a escribir

Alcance fijado (§13): **1 hallazgo, 1 gráfico principal, máximo 3 de apoyo.**

- Hallazgo en una frase: La inflación esperada a dos años tocó su mínimo histórico a inicios de 2026 y subió después de que un conflicto en Medio Oriente disparara el precio del petróleo.
- Gráfico principal (qué muestra): Serie mensual 2023-2026 de expectativas de inflación EDEP (12 y 24 meses), con scrollytelling de 3 pasos que revela el mínimo de febrero 2026 y el repunte de mayo-junio.
- Qué queda deliberadamente afuera: Desempeño de las empresas, empleo, condiciones crediticias y diferencias detalladas por macrozona — el informe los cubre, esta pieza no.

## Verificación manual

- [x] Con `prefers-reduced-motion`, el scrollytelling degrada a gráficos
      apilados legibles — no a una pantalla en blanco. *(Verificado por
      construcción: el snippet `estaticos` de `ExpectativasInflacionScrolly`
      renderiza las 3 instancias apiladas; confirmado en el HTML estático de
      `pnpm build` que las 3 aparecen completas.)*
- [x] Sin JavaScript, el texto y los gráficos siguen ahí. *(Confirmado
      directamente en `apps/web/dist/.../index.html`: las 5 secciones, las 3
      instancias del gráfico de líneas y los 100 íconos del pictograma están
      en el HTML servido, sin depender de hidratación.)*
- [x] Toda la página se recorre con teclado, con foco visible. *(132
      elementos con `tabindex="0"` en el HTML estático — 42 puntos × 3
      instancias del gráfico de líneas + 6 barras del gráfico de
      combustibles — todos con `:focus-visible` definido en el CSS de cada
      componente.)*
- [x] Ningún dato se comunica solo por color. *(Etiquetas directas "12
      meses"/"24 meses" al final de cada línea y valor numérico directo al
      final de cada barra, además de `aria-label` por elemento y anotaciones
      de texto — el color nunca es la única señal.)*
