# Checklist de publicación — Encuesta nacional de empleo (ENE) mayo - julio 2026

Bloquea el merge (§10). Marcá cada ítem cuando esté hecho de verdad.

- [x] `hallazgo` escrito en una frase, sin jerga. *("Las personas que trabajan
      la jornada completa de 45 horas cayeron 48% en un año...", 145
      caracteres, dentro del rango 20-180 del esquema.)*
- [x] Fuente con URL, fecha de descarga y hash registrados. *(INE no bloquea
      la descarga por script como bcentral.cl: la URL en `00_descargar.py`
      se verificó contra el PDF que ya estaba en `raw/` — sha256 idéntico,
      `4b8aa4f9...5148`.)*
- [x] Datos verificados contra el documento original **por una segunda
      pasada**. *(Las 7 filas de `datos.json` se releyeron a mano contra el
      párrafo de "Actividad económica" (página 3) del PDF: coinciden exacto.
      También se verificaron una a una las cifras citadas en prosa —"Los
      aperitivos" y "El postre"— contra las tablas de la página 1 y 4; se
      corrigió un error propio de transcripción, 443→448 mil, antes de
      escribir el MDX final.)*
- [x] Tests del pipeline en verde (5/5,
      `just -f pipelines/encuesta-nacional-de-empleo-mayo-julio-2026/justfile test`).
- [x] Todo gráfico tiene título, unidades, fuente y anotación. *(`Figura`
      del kit lo exige estructuralmente; el único gráfico de esta pieza lo
      cumple — sin warnings de desarrollo en el build.)*
- [x] Tabla equivalente accesible presente en cada gráfico. *(Confirmado en
      el HTML de build: 2 `<table>` en la página — la Etiqueta Nutricional y
      la tabla equivalente del gráfico.)*
- [x] Todo gráfico tiene un nivel real de interacción (scroll o clic) — nunca
      es una imagen estática (referencia: pudding.cool). *(Tooltip por
      hover/foco en las 7 barras, igual patrón que la edición anterior.)*
- [x] Si el hallazgo trata directamente de personas (no de instituciones ni
      montos abstractos), se evaluó un `Pictograma` (dibujos de personas)
      además de o en vez del gráfico de barras/líneas por defecto. *(El
      gráfico es sobre sectores económicos, no personas — se mantiene la
      barra divergente, mismo criterio que la pieza anterior con este mismo
      shape de dato.)*
- [ ] Probado en móvil real, no solo en el emulador. *(El usuario decidió
      publicar sin esperar esta verificación.)*
- [x] Presupuesto de rendimiento respetado (`pnpm build && pnpm presupuesto`).
      *(Al publicar esta pieza el shell llegó a 40,0/40 KB —2 bytes de
      margen—: se subió el techo a 50 KB en `scripts/presupuesto-rendimiento.ts`
      §8, decisión del usuario, no algo que se ajustó en silencio. Con el
      techo nuevo: 40,0/50 KB shell (20% de holgura), 51,1/150 KB total,
      62,8/500 KB primera vista. Los tres
      en verde.)*
- [x] Datasets publicados en `/datos/` con licencia. *(`datos.json`/`.csv`,
      CC BY 4.0, 7 filas.)*
- [x] Errores conocidos y limitaciones declarados al final. *(5 puntos en el
      frontmatter, incluida la salvedad de la Ley 40 horas.)*

## Antes de empezar a escribir

Alcance fijado (§13): **1 hallazgo, 1 gráfico principal, máximo 3 de apoyo.**

- Hallazgo en una frase: Las personas que trabajan la jornada completa de 45
  horas cayeron 48% en un año: el mercado laboral se está reacomodando hacia
  turnos más cortos.
- Gráfico principal (qué muestra): Variación interanual de ocupados por
  sector económico, para los 7 sectores que el INE destacó en el trimestre
  (4 con caída, 3 con alza).
- Qué queda deliberadamente afuera: El resto de los ~20 sectores económicos
  sin variación destacada, la serie histórica completa de desocupación (es
  una imagen en el PDF), y la desagregación regional/comunal.

## Verificación manual

- [x] Con `prefers-reduced-motion`, el scrollytelling degrada a gráficos
      apilados legibles — no a una pantalla en blanco. *(No aplica: esta
      pieza no usa Scrolly — es una fotografía de un trimestre, no una
      secuencia, mismo criterio que la pieza anterior con este dato.)*
- [x] Sin JavaScript, el texto y los gráficos siguen ahí. *(Confirmado en
      `apps/web/dist/.../index.html`: las 5 secciones y el SVG del gráfico
      están en el HTML servido, sin depender de hidratación — solo el
      tooltip y la compensación de escala del texto necesitan JS.)*
- [x] Toda la página se recorre con teclado, con foco visible. *(7 elementos
      con `tabindex="0"` en el HTML estático — una por sector— con
      `:focus-visible` definido en el CSS del componente.)*
- [x] Ningún dato se comunica solo por color. *(Etiqueta de valor directa al
      final de cada barra, además de `aria-label` por elemento — el color
      nunca es la única señal.)*
