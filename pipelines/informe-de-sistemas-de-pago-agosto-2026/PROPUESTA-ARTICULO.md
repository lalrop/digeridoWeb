# Propuesta de artículo — Informe de Sistemas de Pago (ISP), agosto 2026

Fase 1 del redactor: una versión de `hallazgo`, `bajada` y `limitaciones`, y
tres opciones (A/B/C) por sección narrativa. Todos los números citados acá
salen de `pipelines/informe-de-sistemas-de-pago-agosto-2026/interim/*.json`
(ya limpios y validados) o son citas textuales del PDF original, verificadas
línea por línea contra `interim/texto-completo.txt`.

## Campos cortos

**hallazgo:**

> Aceptar un pago de $1.000 por transferencia puede costarle a un almacén
> hasta 42,1% de esa venta, según qué proveedor use.

**bajada:**

> El Banco Central revisó cómo paga Chile: cobrar una transferencia le sale
> carísimo a algunos comercios chicos según el proveedor que usen, y el
> efectivo, aunque en baja, sigue siendo indispensable en regiones y ferias.

**limitaciones:**

- Esta pieza usa 2 de las decenas de datos que trae el Informe de Sistemas de
  Pago (el costo de aceptar TEF y el acceso a efectivo): no cubre fraude,
  remesas, infraestructuras de mercados financieros ni el capítulo completo
  sobre stablecoins, que también forman parte del documento.
- Los gráficos del PDF son imágenes, igual que en el IPN antes de recibir su
  Excel de apoyo: acá no hubo un Excel adjunto, así que los datos usados son
  las dos tablas que el Informe sí publica como texto (Tabla I.2 y el
  Recuadro I.2), transcritas y verificadas a mano contra el PDF original.
- El Banco Central anonimiza a los 5 proveedores de la Tabla I.2 por tipo
  ("Iniciador de Pagos 1", "SAG 1", "Banco 1"): no identifica qué empresa
  real cobra cada comisión.
- El cierre estadístico del Informe fue el 31 de marzo de 2026: las cifras
  pueden no reflejar cambios de precio o de mercado posteriores a esa fecha.
- La caída del retiro de efectivo en cajeros (de 14,6% a 6,1% del PIB entre
  2019 y 2025, citada en el texto) no está en el dataset publicado: el
  Informe la menciona en el cuerpo del texto, pero el gráfico que la muestra
  es una imagen sin serie de datos detrás.

---

## 1. El plato de entrada

### Opción A — directa

Imaginá que atendés un almacén y alguien te paga $1.000 por una bebida con
el celular, por transferencia. Según qué aplicación o proveedor use esa
transferencia, a usted —el almacén— le puede llegar bastante menos de esos
$1.000. El Banco Central revisó cinco proveedores que ofrecen este servicio
a los comercios, y encontró que uno de ellos se queda con 42,1% del monto en
comisión. El más barato cobra 1%. Es la misma transferencia, el mismo
monto, y una diferencia de más de 40 puntos porcentuales según a quién le
compraste el servicio.

### Opción B — comparación cotidiana

Es como si por cambiar un billete de $1.000 en dos kioscos distintos, uno te
devolviera $580 y el otro $990. Suena absurdo, pero es más o menos lo que
pasa cuando un almacén acepta un pago de $1.000 por transferencia
electrónica (TEF): según el Banco Central, el proveedor más caro de este
servicio se queda con 42,1% de esa venta en comisión; el más barato, con
apenas 1%. La plata no desaparece por accidente: alguien decide cobrar
mucho más por exactamente el mismo trámite.

### Opción C — pregunta

¿Por qué a veces pagar con la aplicación del banco sale más caro para el
almacén que pagar en efectivo? El Informe de Sistemas de Pago del Banco
Central tiene una respuesta incómoda: depende del proveedor. Aceptar una
transferencia de $1.000 le cuesta a un comercio 42,1% de esa venta con el
proveedor más caro de los cinco que revisó el Banco Central, y apenas 1%
con el más barato. Nadie le avisa al almacén cuál eligió.

---

## 2. La materia prima

### Opción A — directa

El Informe de Sistemas de Pago es el documento con el que el Banco Central
de Chile rinde cuentas, una vez al año, de cómo funcionan los pagos en el
país. Esta edición tiene 63 páginas y, según nuestra medición, es "difícil"
de leer (45 sobre 100 en la escala Fernández-Huerta): usa 103 siglas sin
definir la primera vez que aparecen, entre ellas TEF (Transferencia
Electrónica de Fondos), IMF (Infraestructuras del Mercado Financiero) y CMF
(Comisión para el Mercado Financiero). Es, de los tres informes que hemos
digerido, el más denso de leer. Sus gráficos, como en el resto de estos
documentos, son solo dibujos en el PDF: esta vez el Banco Central no publicó
un Excel aparte, así que los datos de esta pieza salen de las dos tablas que
el Informe sí trae en formato texto.

### Opción B — el búho de la portada

Antes de la primera página con números, el Informe de Sistemas de Pago
tiene una portada dedicada al tucúquere, el búho más grande de Chile: mide
hasta 55 centímetros, tiene ojos amarillos enormes y caza roedores al
atardecer. Es una costumbre del Banco Central —cada informe institucional
abre con una especie nativa— tan fija como la dificultad del texto que
viene después. Esta edición, 63 páginas más adelante, resultó "difícil" de
leer (45 sobre 100), con 103 siglas sin definir. Entre el búho de la
portada y el cierre, el documento cruza tres temas casi sin parentesco:
cómo paga la gente, cómo funcionan las bolsas y bancos por dentro, y qué son
las stablecoins. Esta pieza se queda con uno de esos tres platos.

### Opción C — tres platos, un festín raro

El Informe de Sistemas de Pago no es un documento, son tres: un capítulo
sobre cómo paga la gente el día a día (tarjetas, transferencias, efectivo),
uno sobre cómo funcionan por dentro los mercados financieros, y uno sobre
stablecoins —una moneda digital que promete valer siempre lo mismo que un
dólar—. Los tres conviven en 63 páginas que, medidas con nuestra fórmula de
legibilidad, salen "difíciles" (45 sobre 100), con 103 siglas que nadie le
explica al lector antes de usarlas. Como en los otros informes del Banco
Central, los gráficos son imágenes fijas: acá no llegó un Excel de apoyo,
así que se rescataron las dos tablas que sí vienen en texto plano.

---

## 3. El plato de fondo

### Opción A — directa

La Tabla I.2 del Informe compara lo que cobran cinco proveedores por
aceptar un pago con transferencia (TEF), en tres montos distintos: $1.000,
$20.000 y $50.000. El patrón es el mismo en los cinco: cobran mucho más,
en proporción, por los pagos chicos. Pero el tamaño de esa diferencia varía
muchísimo. "Iniciador de Pagos 1" cobra 42,1% en un pago de $1.000 y baja a
1,5% en uno de $50.000. "Banco 1", en cambio, cobra 1% siempre, sin importar
el monto. En el gráfico de abajo podés recorrer esa historia paso a paso.

{/* El gráfico principal va a ancho de figura, no de texto. */}
<div class="carril-ancho">
  <CostoTefScrolly datos={datosCostoTef.filas} client:visible />
</div>

### Opción B — comparación de panaderías

Es como comparar el precio del pan en cinco panaderías del mismo barrio:
todas cobran más caro la marraqueta suelta que el pan por kilo, pero una de
ellas cobra literalmente 40 veces más por unidad que las demás. Eso es lo
que muestra la Tabla I.2 del Informe: cinco proveedores de pagos por
transferencia (TEF), comparados en tres montos ($1.000, $20.000 y $50.000).
Todos cobran más, en proporción, por los pagos chicos —tiene sentido, hay
un costo fijo detrás de cada transacción—. Lo que no tiene una explicación
tan simple es que el más caro cobre 42,1% en un pago de $1.000 mientras el
más barato cobra 1% sin importar el monto. Desplazate por el gráfico para
ver cómo se acerca la brecha a medida que el pago crece.

{/* El gráfico principal va a ancho de figura, no de texto. */}
<div class="carril-ancho">
  <CostoTefScrolly datos={datosCostoTef.filas} client:visible />
</div>

### Opción C — desde el mostrador del almacén

Ponete en el lugar de quien tiene que elegir, para su almacén, qué
aplicación de pago instalar. La Tabla I.2 del Informe de Sistemas de Pago
compara cinco opciones para aceptar transferencias (TEF), en pagos de
$1.000, $20.000 y $50.000. La decisión importa: con el proveedor más caro,
un vuelto de $1.000 pierde 42,1% en comisión: casi la mitad se la queda el
intermediario. Con el más barato, se pierde apenas 1%, siempre, no importa
cuánto pague el cliente. El gráfico de abajo lo recorre en tres pasos, de
la diferencia máxima a la mínima.

{/* El gráfico principal va a ancho de figura, no de texto. */}
<div class="carril-ancho">
  <CostoTefScrolly datos={datosCostoTef.filas} client:visible />
</div>

---

## 4. Los aperitivos

### Opción A — directa

El efectivo no desapareció, aunque el Informe dice que los retiros en
cajero cayeron de 14,6% del PIB en 2019 a 6,1% en 2025 —menos de la mitad
en seis años—. Sigue siendo clave en regiones, ferias libres, transporte
público y pagos bajo $10.000. ¿Cómo se consigue ese efectivo? El 77% de la
población usa cajeros automáticos como canal principal, y un 47% usa las
Cajas Vecinas —esos negocios de barrio donde también se puede sacar plata—,
que cumplen un rol complementario donde hay menos bancos.

<div class="carril-ancho">
  <AccesoEfectivo datos={datosAccesoEfectivo.filas} client:visible />
</div>

### Opción B — la contradicción del propio resumen

El resumen del Informe dice, casi con las mismas palabras, dos cosas que
parecen contradecirse: que los pagos digitales son "cada vez más
relevantes" y que el efectivo "continúa siendo utilizado con mayor
frecuencia" en ciertos contextos. Ambas son ciertas. Los retiros de
efectivo en cajero cayeron de 14,6% del PIB en 2019 a 6,1% en 2025, pero
persisten fuerte en regiones, ferias y transporte público. Y para
conseguir ese efectivo, el país todavía depende sobre todo de los cajeros
automáticos (77% de la población los usa como canal principal), aunque las
Cajas Vecinas —los negocios de barrio que también entregan efectivo— ya
llegan al 47%.

<div class="carril-ancho">
  <AccesoEfectivo datos={datosAccesoEfectivo.filas} client:visible />
</div>

### Opción C — el rol de las cajas vecinas

Hay un personaje secundario en esta historia: la Caja Vecina, ese
mostrador dentro de un almacén o botillería donde también se puede sacar
plata. El Informe cuenta que un 47% de la población ya la usa como canal
principal de acceso a efectivo, cerca de la mitad de quienes usan cajeros
automáticos (77%). No reemplaza al cajero —tiene montos máximos por
transacción y depende de que el comercio tenga plata disponible—, pero
amplía la cobertura en zonas con menos bancos. Tiene sentido: mientras los
retiros de efectivo en cajero cayeron de 14,6% del PIB en 2019 a 6,1% en
2025, alguien tiene que seguir entregando esos billetes en el resto del
país.

<div class="carril-ancho">
  <AccesoEfectivo datos={datosAccesoEfectivo.filas} client:visible />
</div>

---

## 5. El postre

### Opción A — directa

Ninguna ley obliga hoy a un almacén a mostrar cuánto le cobra cada
proveedor de pagos antes de elegir uno. El Informe muestra que esa
elección, para un comercio chico, puede significar perder 1% o 42% de cada
venta digital —una diferencia que ni el cliente ni, muchas veces, el propio
almacén alcanzan a ver. El Banco Central prioriza para su próxima agenda
cambios normativos que faciliten usar la transferencia como medio de pago
a comercios. Queda por verse si eso incluye más transparencia sobre estas
comisiones, o solo más adopción del medio de pago en sí.

### Opción B — mirando hacia adelante

Si los pagos digitales siguen creciendo —y todo indica que sí— esta brecha
de comisiones importa cada vez más. Hoy afecta sobre todo a comercios
chicos que recién empiezan a aceptar transferencias; mañana, si el efectivo
sigue retrocediendo al ritmo de los últimos seis años (de 14,6% a 6,1% del
PIB en retiros), podría convertirse en el costo estructural de vender algo
en Chile. El Informe no dice qué proveedor elegir ni cuánto debería costar
esto: solo deja la foto de cómo está hoy, con comisiones que van de 1% a
42,1% por la misma transacción.

### Opción C — cerrando el círculo

Volvamos al almacén del principio. La persona que lo atiende probablemente
no eligió su proveedor de pagos comparando tablas del Banco Central —eligió
el que le ofreció instalar alguien, o el que ya traía el POS que le
prestaron—. El Informe de Sistemas de Pago no la culpa: muestra un mercado
donde el costo de aceptar plata digital varía 40 veces entre opciones, sin
que eso sea obvio para quien decide. Mientras tanto, el efectivo —aunque
cada vez menos, de 14,6% a 6,1% del PIB en seis años— sigue ahí como red de
respaldo, sobre todo donde ese vendedor no tiene forma de comparar.

---

## [FALTA: ...]

- Nada pendiente del lado de datos: `datos.json` (costo TEF, 15 filas) y
  `acceso-efectivo.json` (2 filas) ya están publicados, validados por 12
  tests de invariantes, y los componentes `CostoTefScrolly.svelte` /
  `AccesoEfectivo.svelte` ya existen en `components/`.
- Falta elegir la opción (o mezcla) de cada sección para escribir el
  `index.mdx` final.
- Falta calcular `tiempoLectura.digerido` y `etiqueta.legibilidadDigerido`
  con `pipelines/_common/legibilidad.py` sobre el texto final ya elegido —no
  se estiman a mano.
- Falta la segunda pasada de verificación de cifras contra el PDF original
  (§10), la prueba en teléfono real, y el resto del checklist de
  `pipelines/informe-de-sistemas-de-pago-agosto-2026/CHECKLIST.md`.
