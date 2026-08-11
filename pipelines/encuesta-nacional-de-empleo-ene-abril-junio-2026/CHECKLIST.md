# Checklist de publicación — Encuesta nacional de empleo (ENE) abril - junio 2026

Bloquea el merge (§10). Marcá cada ítem cuando esté hecho de verdad.

- [ ] `hallazgo` escrito en una frase, sin jerga.
- [ ] Fuente con URL, fecha de descarga y hash registrados.
- [ ] Datos verificados contra el documento original **por una segunda pasada**.
- [ ] Tests del pipeline en verde (`just -f pipelines/encuesta-nacional-de-empleo-ene-abril-junio-2026/justfile test`).
- [ ] Todo gráfico tiene título, unidades, fuente y anotación.
- [ ] Tabla equivalente accesible presente en cada gráfico.
- [ ] Todo gráfico tiene un nivel real de interacción (scroll o clic) — nunca
      es una imagen estática (referencia: pudding.cool).
- [ ] Si el hallazgo trata directamente de personas (no de instituciones ni
      montos abstractos), se evaluó un `Pictograma` (dibujos de personas)
      además de o en vez del gráfico de barras/líneas por defecto.
- [ ] Probado en móvil real, no solo en el emulador.
- [ ] Presupuesto de rendimiento respetado (`pnpm build && pnpm presupuesto`).
- [ ] Datasets publicados en `/datos/` con licencia.
- [ ] Errores conocidos y limitaciones declarados al final.

## Antes de empezar a escribir

Alcance fijado (§13): **1 hallazgo, 1 gráfico principal, máximo 3 de apoyo.**

- Hallazgo en una frase: ______________________________________________
- Gráfico principal (qué muestra): ____________________________________
- Qué queda deliberadamente afuera: ___________________________________

## Verificación manual

- [ ] Con `prefers-reduced-motion`, el scrollytelling degrada a gráficos
      apilados legibles — no a una pantalla en blanco.
- [ ] Sin JavaScript, el texto y los gráficos siguen ahí.
- [ ] Toda la página se recorre con teclado, con foco visible.
- [ ] Ningún dato se comunica solo por color.
