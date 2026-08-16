# Checklist de publicación — Informe de Sistemas de Pago (ISP) agosto 2026

Bloquea el merge (§10). Marcá cada ítem cuando esté hecho de verdad.

- [x] `hallazgo` escrito en una frase, sin jerga.
- [x] Fuente con URL, fecha de descarga y hash registrados.
- [x] Datos verificados contra el documento original **por una segunda pasada**
      (las 15 filas de `datos.json` y las 2 de `acceso-efectivo.json` se
      recalcularon desde cero contra una re-extracción independiente de las
      páginas 21 y 22 del PDF con `pdfplumber` — coinciden exacto: Tabla I.2
      completa y 77 %/47 % del Recuadro I.2).
- [x] Tests del pipeline en verde (12/12; `just` no está disponible en esta
      máquina, se corrió `python -m pytest pipelines/.../tests` directo).
- [x] Todo gráfico tiene título, unidades, fuente y anotación.
- [x] Tabla equivalente accesible presente en cada gráfico.
- [x] Todo gráfico tiene un nivel real de interacción (scroll o clic) — nunca
      es una imagen estática (referencia: pudding.cool).
- [x] Si el hallazgo trata directamente de personas (no de instituciones ni
      montos abstractos), se evaluó un `Pictograma`. *(El hallazgo principal
      es sobre comisiones que cobran proveedores a comercios, no personas —
      se usó un gráfico de líneas/slope, con leyenda en HTML para que el
      nombre de cada proveedor se lea bien en cualquier ancho de pantalla.
      El gráfico de apoyo de acceso a efectivo sí trata de personas (% de la
      población): se rediseñó de barras a `Pictograma` —dos grillas de 100
      figuras, una por canal— siguiendo la regla del agente
      disenador-visualizaciones. Se reusa el mismo componente que la
      encuesta de empleo, pero acá el criterio es que el hallazgo ES gente,
      no evitar repetir un recurso visual.)*
- [x] Probado en móvil real, no solo en el emulador. Confirmado por el
      usuario (el reporte inicial — "el gráfico se ve muy pequeño, apenas es
      posible leer qué dice en cada punto" — vino de probarlo en el celular;
      corregido con la leyenda en HTML y validado con "estamos ok con todas
      las modificaciones").
- [x] Presupuesto de rendimiento respetado. Medido dos veces: en borrador
      (`DIGERIDO_EJEMPLOS=1 pnpm -F @digerido/web build && pnpm presupuesto`)
      y en el build de producción real, ya con `estado: 'publicada'`
      (`pnpm -F @digerido/web build && pnpm presupuesto`, sin necesitar la
      variable): JS del shell 36,0/40 KB, JS total con islas 46,9/150 KB,
      primera vista 58,0/500 KB — los tres en verde, incluyendo el tercer
      elemento visual (`EfectivoRetiroPib`, un comparador tipográfico sin JS:
      no cuenta ni un byte en el presupuesto). (`/og/portal.png` falla en
      ambos builds por falta de fuentes de marca en esta máquina; es una
      limitación local documentada en el README, no de esta pieza — CI sí
      tiene las fuentes.)
- [x] Datasets publicados en `/datos/` con licencia.
- [x] Errores conocidos y limitaciones declarados al final.

## Antes de empezar a escribir

Alcance fijado (§13): **1 hallazgo, 1 gráfico principal, máximo 3 de apoyo.**

- Hallazgo en una frase: Aceptar un pago de $1.000 por transferencia puede
  costarle a un almacén hasta 42,1% de esa venta, según qué proveedor use.
- Gráfico principal (qué muestra): Costo de aceptar un pago vía TEF, como %
  del monto, para 5 proveedores y 3 montos ($1.000/$20.000/$50.000), con
  scrollytelling de 3 pasos que revela la brecha máxima y el contraste con
  el proveedor más barato (Tabla I.2 del Informe).
- Qué queda deliberadamente afuera: Fraude, remesas, infraestructuras de
  mercados financieros y el capítulo completo sobre stablecoins — el
  informe los cubre en detalle, esta pieza no.

## Verificación manual

- [x] Con `prefers-reduced-motion`, el scrollytelling degrada a gráficos
      apilados legibles — no a una pantalla en blanco. *(Verificado en el
      HTML estático de `pnpm build`: el snippet `estaticos` de
      `CostoTefScrolly` renderiza las 3 instancias apiladas de la figura
      `g-costo-tef`, cada una con su párrafo congelado en el paso que
      describe.)*
- [x] Sin JavaScript, el texto y los gráficos siguen ahí. *(Confirmado
      directamente en `apps/web/dist/.../index.html`: las 5 secciones, las 3
      instancias del gráfico principal y la del gráfico de apoyo están en el
      HTML servido, sin depender de hidratación.)*
- [x] Toda la página se recorre con teclado, con foco visible. *(245
      elementos con `tabindex="0"` en el HTML estático — 15 puntos × 3
      instancias del gráfico principal + 200 figuras del Pictograma (2
      grillas de 100) del gráfico de acceso a efectivo — todos con
      `:focus-visible` definido en el CSS de cada componente.)*
- [x] Ningún dato se comunica solo por color. *(Etiquetas directas por
      entidad en $1.000 y valor numérico directo al final de cada barra,
      además de `aria-label` por elemento y anotaciones de texto — el color
      nunca es la única señal.)*
