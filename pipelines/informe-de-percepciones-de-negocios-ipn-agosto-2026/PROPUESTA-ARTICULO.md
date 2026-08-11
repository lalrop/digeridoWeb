# Propuesta de artículo — Informe de Percepciones de Negocios (IPN) agosto 2026

Fase 1 del agente redactor-digestion. No es el `index.mdx` final: es la base
para elegir, sección por sección, antes de escribir la versión definitiva.

**Segunda versión** — el usuario aportó el Excel "Gráficos EPN agosto
2026.xlsx" (una hoja por gráfico, con la serie mensual completa detrás de
cada uno). Esto reemplaza la primera versión, que solo tenía los 4 números
que el PDF citaba como texto. Ahora el gráfico principal usa los 42 meses
completos (2023-2026) de expectativas de inflación, con scrollytelling real,
y se sumó un segundo gráfico de apoyo (lúdico, tipo pictograma) sobre
expectativas de combustible — ambos ya construidos y funcionando
(`components/ExpectativasInflacionScrolly.svelte` y
`components/CombustiblesPictograma.svelte`).

## Frontmatter propuesto

**hallazgo** (162 caracteres, sin cambios — la serie completa lo confirma):

> La inflación esperada a dos años tocó su mínimo histórico a inicios de 2026 y subió después de que un conflicto en Medio Oriente disparara el precio del petróleo.

**bajada** (219 caracteres, sin cambios):

> El Banco Central preguntó a cientos de empresas por costos, ventas, crédito e inflación: el desempeño fue más débil de lo esperado, pero lo que más se movió es la inflación que las propias empresas anticipan a dos años.

**limitaciones**:

- Esta pieza usa 2 de los cerca de 24 gráficos que el Banco Central publica junto al IPN (expectativas de inflación y expectativas de precio de combustible): es un recorte deliberado —1 hallazgo, 1 gráfico principal, máximo 3 de apoyo— no un resumen completo del informe, que también cubre desempeño, empleo y condiciones crediticias en detalle.
- El IPN es un informe cualitativo y de percepciones, construido con entrevistas y dos encuestas (EPN y EDEP): los "índices de difusión" y las distribuciones de respuesta miden qué proporción de empresas percibe algo, no cuánto cambió realmente cada variable económica.
- Las citas de entrevistados que aparecen en el documento (y en esta pieza) son anónimas por cargo y rubro, tal como las publica el Banco Central: no identifican personas ni empresas específicas.
- El propio IPN aclara que las opiniones que recoge no representan la evaluación oficial del Consejo del Banco Central sobre la coyuntura económica.
- Esta pieza no desarrolla en detalle las diferencias entre las tres macrozonas (norte, centro, sur) que el informe sí distingue por separado.

---

## 1. El plato de entrada

### Opción A — el contraste directo

La desocupación y el precio del dólar son las cifras que suelen acaparar los
titulares. Pero hay un número más discreto que el Banco Central de Chile
también les pregunta a las empresas cada trimestre: cuánto esperan que suba
la inflación (el alza generalizada de precios) de acá a dos años. Desde que
existe esa medición, nunca había estado tan baja como a comienzos de 2026:
un 3%. Cuatro meses después, tras el estallido de un conflicto entre Estados
Unidos e Irán que disparó el precio del petróleo, subió a 3,5% y ahí se
quedó. La sorpresa no es solo el número: es lo rápido que las empresas
chilenas reacomodaron sus cálculos frente a algo que pasó a miles de
kilómetros de distancia, como cuando un temblor reordena los muebles de una
casa sin que nadie lo haya pedido.

### Opción B — la analogía de la receta

Cada empresa que el Banco Central entrevista para este informe tiene, en el
fondo, una misma pregunta que resolver: si sus costos —el aceite, el
transporte, la mano de obra— suben, ¿pueden subir también el precio de lo
que venden sin espantar a los clientes? Desde marzo de 2026 la respuesta ha
sido, mayoritariamente, que no: los márgenes se han ido angostando como una
salsa que se reduce de más. Y el ingrediente que más encareció la receta fue
externo: el conflicto entre Estados Unidos e Irán empujó al alza el precio
del petróleo, y con él, el de casi todo lo que se mueve en camión. La
consecuencia quedó registrada en un número concreto: la inflación que las
propias empresas esperan para dentro de dos años saltó de su mínimo
histórico (3%) a 3,5%, y ahí sigue.

### Opción C — la pregunta que abre

¿Qué tan rápido puede cambiar de opinión una economía entera? El Informe de
Percepciones de Negocios (IPN) del Banco Central le pregunta eso, en el
fondo, a cientos de empresas cuatro veces al año: gerentes de comercio,
industria, minería, banca, agro. En la edición de agosto 2026, la respuesta
tiene una fecha bastante precisa. A comienzos de año, la inflación que las
empresas esperaban para dentro de dos años había caído a su nivel más bajo
desde que se mide: 3%. Después de que estallara un conflicto entre Estados
Unidos e Irán y el petróleo se encareciera, ese número subió a 3,5% en mayo
— y se quedó ahí en junio. Es una cifra chica, pero es la huella que dejó un
evento internacional en el bolsillo (y en la calculadora) de las empresas
chilenas.

---

## 2. La materia prima

### Opción A — mostrarlo tal cual

Esta pieza digiere el *Informe de Percepciones de Negocios*, edición de
agosto de 2026, que el Banco Central de Chile publica cuatro veces al año
(febrero, mayo, agosto y noviembre). Son 36 páginas construidas a partir de
entrevistas a empresas de todo el país, más dos encuestas online: la
Encuesta de Percepciones de Negocios (EPN, sobre desempeño, costos y
expectativas) y la Encuesta de Determinantes y Expectativas de Precios
(EDEP, específicamente sobre inflación). Medimos qué tan fácil es leer el
documento y el resultado fue 56 sobre 100 — "bastante difícil" en la escala
que usamos. Encontramos 26 siglas que el informe usa sin explicarlas la
primera vez que aparecen (EPN, EDEP, entre otras). Los cerca de 24 gráficos
del PDF son dibujos, no datos que se puedan copiar y pegar directamente del
documento — pero el Banco Central sí publica, aparte, un Excel con la serie
completa detrás de cada uno. Es de ahí, no del PDF, de donde sale el
gráfico principal de esta pieza.

### Opción B — el archivo que faltaba

Un buen plato depende de que uno sepa exactamente qué le echó. La primera
lectura de este informe del Banco Central fue frustrante en ese sentido:
sus cerca de 24 gráficos, en el PDF, son imágenes —no números que se
puedan seleccionar y copiar—, así que el primer intento de esta digestión
solo pudo rescatar los pocos valores que el texto citaba de pasada. Pero el
Banco Central publica, junto al PDF, un segundo archivo: un Excel con una
hoja por gráfico y la serie mensual completa desde 2023. Es la diferencia
entre ver la foto de un plato y tener la receta con las cantidades exactas.
Con eso en mano, el gráfico de esta pieza deja de ser una aproximación:
son 42 meses de datos reales, mes a mes, sin adivinar nada. El texto en sí
sigue siendo denso —56 sobre 100 en nuestra medición de legibilidad, 26
siglas sin explicar la primera vez que aparecen—, pero los números detrás
de sus gráficos están completos.

### Opción C — quién habla en el documento

A diferencia de un boletín de cifras, este informe tiene voces: gerentes de
comercio, minería, banca, industria de alimentos, hotelería, agroindustria,
citados de forma anónima (por cargo y rubro, nunca por nombre) a lo largo
de sus 36 páginas. El Banco Central de Chile construye el *Informe de
Percepciones de Negocios* así cuatro veces al año, combinando entrevistas
con dos encuestas online (EPN y EDEP). El resultado es un documento
"bastante difícil" de leer (56 sobre 100 en nuestra medición), con 26
siglas sin definir la primera vez que aparecen. Sus gráficos, en el PDF,
son solo dibujos — pero el Banco Central también publica un Excel aparte
con la serie mensual completa detrás de cada uno, desde 2023. Entre tantas
opiniones y tantas líneas en un gráfico, hay una que se mueve distinto a
todas las demás: la de cuánto esperan las empresas que suba la inflación
en dos años. Esa es la que sostiene esta pieza.

---

## 3. El plato de fondo

*(Las tres opciones comparten el mismo gráfico principal —
`ExpectativasInflacionScrolly.svelte`, ya construido y funcionando—, con
scrollytelling de 3 pasos: la serie completa 2023-2026, el mínimo de
febrero 2026, y el repunte de mayo-junio. Lo que cambia entre las opciones
es el párrafo de contexto.)*

### Opción A

La cifra que abre esta pieza tiene una trayectoria completa detrás, mes a
mes desde 2023. A fines de 2025, la mediana de las expectativas de
inflación a dos años que mide la EDEP venía bajando. Tocó su mínimo
histórico —3%— en febrero de 2026. Dos meses después estalló el conflicto
entre Estados Unidos e Irán, el precio del petróleo subió y, con un poco de
rezago, la expectativa de inflación también: a 3,5% en mayo, cifra que se
repitió en junio. La expectativa a un plazo más corto (12 meses) reaccionó
todavía más fuerte: pasó de 3% a 4% en el mismo período.

### Opción B

Si uno pudiera ponerle un gráfico a la palabra "sobresalto", se parecería a
este. Entre febrero y mayo de 2026, la inflación que las empresas esperan
para dentro de dos años subió medio punto porcentual —de 3% a 3,5%—
después de tocar, en febrero, su nivel más bajo desde que existe la
medición. La línea de 12 meses, en el mismo gráfico, se mueve todavía más:
de 3% a 4%. Es como si el susto de corto plazo se hubiera sentido de
inmediato, mientras la duda sobre cuánto durará el conflicto recién se
estuviera cocinando a fuego lento en los cálculos de más largo plazo.

### Opción C

Dos horizontes, dos velocidades. La expectativa de inflación a 12 meses
tocó 3% en febrero de 2026 y saltó a 4% en abril, donde se ha mantenido
desde entonces. La de 24 meses se movió más despacio: del mismo mínimo de
3% en febrero subió gradualmente a 3,5% en mayo, nivel que se repitió en
junio. Las dos empiezan en el mismo punto mínimo y las dos suben — pero la
de más largo plazo lo hace con más cautela, como si las empresas todavía no
estuvieran seguras de cuánto va a durar el shock de costos.

---

## 4. Los aperitivos

*(Las opciones A y C incluyen el segundo gráfico ya construido,
`CombustiblesPictograma.svelte`: un pictograma interactivo —hover/clic,
sin scrollytelling porque es una fotografía, no una secuencia— que muestra
que el 78,9% de las empresas no espera que el combustible baje de precio
en los próximos seis meses.)*

### Opción A — por regiones y por combustible

Un par de datos más, para quien quiera mirar más de cerca. El IPN divide
al país en tres macrozonas, y no todas ven lo mismo: en el norte, dominado
por la minería, las empresas relatan un primer semestre flojo pero con
expectativas "fuertemente optimistas" de mediano plazo; en el centro, más
cauto, la mayoría espera que 2026 termine parecido a 2025. Y sobre el
propio combustible que disparó esta historia: casi 8 de cada 10 empresas
(78,9%) no espera que su precio baje en los próximos seis meses — la
mayoría cree que se mantendrá igual o seguirá subiendo.

{/* gráfico: CombustiblesPictograma */}

### Opción B — el detalle humano

Detrás de los números hay testimonios concretos. "No se ven razones para
que el IPC (el índice que mide la inflación) crezca significativamente en
los próximos meses, a menos que vuelva el tema de la guerra", dice un
gerente de comercio automotriz citado en el informe. Otro, del mismo
rubro, es más directo: "tengo miedo por nuevos bombardeos en Irán, que se
metan nuevos países". Esa misma incertidumbre aparece en el crédito: la
banca reporta más solicitudes —muchas para financiar el costo que no se
pudo traspasar a precios— pero también más rechazos. Y en algunos rubros,
como los call center, la automatización ya está cambiando la
conversación: "hemos reducido a la mitad los call center por reemplazo con
chatbots", cuenta un representante de una cámara regional de comercio.

### Opción C — el empleo, con matices, y el combustible

Sobre empleo, el informe no muestra grandes despidos, pero sí una cautela
que se nota: las empresas que ajustaron dotación se inclinaron levemente
hacia la baja, y la razón más mencionada para contratar en 2026 ya no es
"más ventas" sino reemplazar personal despedido por bajo desempeño — una
señal de que las empresas están siendo más exigentes con quién se queda.
Y sobre el ingrediente que encareció todo esto: casi 8 de cada 10 empresas
(78,9%) no espera que el precio del combustible baje en los próximos seis
meses. Como en una sobremesa donde todos coinciden en que "esto va a
mejorar", pero nadie se anima a decir exactamente cuándo — ni con qué.

{/* gráfico: CombustiblesPictograma */}

---

## 5. El postre

### Opción A

La inflación que las empresas anticipan para dentro de dos años sigue
apenas medio punto arriba de su mínimo histórico — no es una crisis, pero
tampoco es la calma con la que había arrancado 2026. Lo que este informe no
responde es cuánto va a durar el conflicto que la empujó para arriba, ni si
el próximo IPN, en noviembre, la va a mostrar bajando de nuevo o
consolidada en 3,5%. El propio Banco Central advierte que las opiniones
que recoge no son su evaluación oficial de la economía: son un termómetro
de lo que sienten quienes toman las decisiones de precios, sueldos e
inversión en el día a día.

### Opción B

Toda receta tiene un momento en que hay que decidir si el plato quedó bien
o si falta corregir algo. Para las empresas chilenas, ese momento llega
cada tres meses con un nuevo IPN. La edición de agosto muestra una
inflación esperada a dos años que subió, pero que se estabilizó ahí — ni
sigue disparándose ni vuelve a su mínimo de febrero. Casi 8 de cada 10
empresas tampoco espera que el combustible, el origen de todo esto, baje
de precio pronto. Lo que falta por ver es si el conflicto en Medio Oriente
se resuelve antes de que esa expectativa se afirme como "la nueva
normalidad", o si termina goteando hacia la inflación a 12 meses, que ya
subió de 3% a 4% en el mismo período.

### Opción C

Un conflicto que empezó a miles de kilómetros de Chile movió, en cuestión
de meses, la calculadora con la que las empresas chilenas planifican los
próximos dos años. Eso es lo que deja este informe: no una crisis, sino una
corrección de expectativas todavía en curso, visible mes a mes en la serie
completa que el propio Banco Central publica. Quedan preguntas abiertas que
el documento no contesta — si el shock de costos es transitorio o va a
quedar instalado, y qué va a pasar con las inversiones que muchas empresas
dijeron haber puesto en pausa hasta que haya más certeza, política y
externa. La respuesta, en parte, se va a ver recién en el IPN de
noviembre.

---

## [FALTA: ...]

- **`legibilidadDigerido` y `tiempoLectura.digerido`**: se completan recién
  cuando el texto final de `index.mdx` esté escrito (Fase 2), no antes.
- **Diferencias detalladas por macrozona** (norte/centro/sur): el documento
  las desarrolla en profundidad (10+ páginas), pero quedaron fuera del
  alcance de 1 hallazgo + 1 gráfico principal que fija el checklist del
  proyecto (§13). Si se quisiera una segunda pieza centrada en eso, sería
  una digestión aparte.
- Nada pendiente en los gráficos: `ExpectativasInflacionScrolly.svelte` y
  `CombustiblesPictograma.svelte` ya están construidos, tipados sin errores
  (`pnpm -F @digerido/web typecheck`) y conectados a los datasets reales
  publicados en `/data/informe-de-percepciones-de-negocios-ipn-agosto-2026/`.
