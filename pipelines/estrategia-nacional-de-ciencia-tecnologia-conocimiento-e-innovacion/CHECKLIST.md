# Checklist de publicación — Estrategia Nacional de CTCI 2026

Bloquea el merge (§10). Marcá cada ítem cuando esté hecho de verdad.

- [x] `hallazgo` escrito en una frase, sin jerga. *("6 de cada 10
      investigadores de Chile trabajan en la Región Metropolitana, pero la
      que más doctorados tiene...", 165 caracteres, dentro del rango 20-180.)*
- [x] Fuente con URL, fecha de descarga y hash registrados. *(Con una
      salvedad real: la URL que el propio documento declara como versión
      digital —`https://estrategia.consejoctci.cl`— no resolvió por DNS al
      momento de escribir este pipeline, y `docs.consejoctci.cl` respondió
      con certificado TLS vencido. El sha256 se calculó sobre el archivo que
      subió el usuario, no sobre una descarga verificada en vivo. Antes de
      publicar, vale la pena reintentar la URL o pedirle al Consejo CTCI el
      enlace correcto.)*
- [x] Datos verificados contra el documento original **por una segunda
      pasada**. *(Los 16 valores por región NO se pudieron extraer por
      script: la infografía de las páginas 112-113 es un mapa circular, y
      `pdfplumber.extract_text()` devuelve los nombres de región literalmente
      al revés y los números fuera de orden. Se renderizaron esas dos
      páginas como imagen (PyMuPDF, 3x de zoom) y se leyeron visualmente,
      dos veces, para transcribir universidades/investigadores/doctorados
      por cada región — ver el comentario de origen en `10_extraer.py`.)*
- [x] Tests del pipeline en verde (6/6,
      `just -f pipelines/estrategia-nacional-de-ciencia-tecnologia-conocimiento-e-innovacion/justfile test`).
- [x] Todo gráfico tiene título, unidades, fuente y anotación. *(2 gráficos:
      `ConcentracionInvestigadores` —mapa de calor, nuevo tipo en el kit— y
      `DoctoradosPorRegion` —barras, con momento de deleite en cascada.)*
- [x] Tabla equivalente accesible presente en cada gráfico. *(3 `<table>` en
      el HTML de build: Etiqueta Nutricional + una por gráfico.)*
- [x] Todo gráfico tiene un nivel real de interacción (scroll o clic) — nunca
      es una imagen estática (referencia: pudding.cool). *(Tooltip por
      hover/foco en las 16 regiones de cada gráfico — 32 elementos con
      `tabindex="0"` en total.)*
- [x] Si el hallazgo trata directamente de personas (no de instituciones ni
      montos abstractos), se evaluó un `Pictograma`. *(El hallazgo es sobre
      distribución geográfica de investigadores, no personas individuales —
      se optó por un mapa de calor regional nuevo (`MapaCalorRegional`,
      reutilizable), pedido explícitamente por el usuario para no dejar
      fuera la metáfora visual que el propio texto invitaba a usar — ver
      memoria "digerido-documentos-extensos".)*
- [ ] Probado en móvil real, no solo en el emulador. *(El usuario decidió
      publicar sin esperar esta verificación.)*
- [x] Presupuesto de rendimiento respetado (`pnpm build && pnpm presupuesto`).
      *(42,2/50 KB shell, 16% de holgura; 58,1/150 KB total; 65,8/500 KB
      primera vista. Los tres en verde.)*
- [x] Datasets publicados en `/datos/` con licencia. *(`datos.json`/`.csv`,
      CC BY 4.0 —la licencia que aplica digerido a los datos que publica,
      no la CC BY-NC-ND del documento original, que protege la expresión
      del documento, no las cifras en sí—, 16 filas.)*
- [x] Errores conocidos y limitaciones declarados al final. *(5 puntos,
      incluida la salvedad de la URL de fuente sin verificar y que los
      datos regionales se transcribieron a mano.)*

## Antes de empezar a escribir

Alcance fijado (§13): **1 hallazgo, 1 gráfico principal, máximo 3 de apoyo.**
*(Con la excepción explícita para documentos extensos: ver memoria
"digerido-documentos-extensos" — acá van 2 gráficos, ambos con peso de
"principal", cada uno sirviendo un momento distinto del argumento.)*

- Hallazgo en una frase: 6 de cada 10 investigadores de Chile trabajan en la
  Región Metropolitana, pero la que más doctorados tiene por cada 1.000
  trabajadores no es la capital: es Los Ríos.
- Gráfico principal (qué muestra): (1) mapa de calor de investigadores por
  región, norte a sur — la concentración; (2) barras de doctorados por
  cada 1.000 trabajadores, ordenadas — la contradicción.
- Qué queda deliberadamente afuera: las otras ~278 páginas del documento
  (visión, objetivos, iniciativas de política pública), la serie histórica
  de esta distribución regional, y el origen/movilidad de los
  investigadores (si nacieron en la región donde trabajan o llegaron de
  otra parte).

## Notas de escala (documento mucho más grande que los anteriores)

- 280 páginas, 92.886 palabras, legibilidad 40/100 ("difícil"), 439 siglas
  sin definir, ~464 minutos de lectura del original — varias veces el
  tamaño de cualquier pieza publicada hasta ahora.
- Es mayormente prosa de política pública (visión, ejes, objetivos,
  iniciativas), no un boletín estadístico: el único dataset numérico limpio
  que se pudo rescatar es el mapa de capacidades CTCI por región.
- Candidato de hallazgo fuerte, verificado en los datos: la Región
  Metropolitana concentra el 61% de los investigadores del país
  (6.139 de 10.045), pero la región con MÁS doctorados trabajando por cada
  1.000 trabajadores no es la Metropolitana (2,6) sino Los Ríos (4,3) — una
  región chica y austral, por encima incluso de Biobío (2,7) y Valparaíso
  (2,5). O'Higgins, en cambio, tiene la tasa más baja del país (0,3) pese a
  estar pegada a la capital.

## Verificación manual

- [x] Con `prefers-reduced-motion`, el scrollytelling degrada a gráficos
      apilados legibles — no a una pantalla en blanco. *(No aplica: ninguno
      de los dos gráficos usa Scrolly — son fotografías de las 16 regiones,
      no una secuencia.)*
- [x] Sin JavaScript, el texto y los gráficos siguen ahí. *(Confirmado en
      `apps/web/dist/.../index.html`: las 5 secciones y los dos SVG están en
      el HTML servido, sin depender de hidratación.)*
- [x] Toda la página se recorre con teclado, con foco visible. *(32
      elementos con `tabindex="0"` en el HTML estático — 16 bandas del mapa
      de calor + 16 barras del segundo gráfico.)*
- [x] Ningún dato se comunica solo por color. *(Mapa de calor: nombre de
      región + valor como texto directo en cada banda, no solo el color de
      fondo. Barras: etiqueta de valor directa al final de cada una.)*
