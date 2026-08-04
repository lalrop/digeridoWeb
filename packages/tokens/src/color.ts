/**
 * Paleta de marca (§5).
 *
 * Sale del material original: oficios fotocopiados, timbres, folios.
 * `enzima` es de uso QUIRÚRGICO — hover, foco, el elemento que el lector
 * controla. Un verde ácido en superficies grandes arruina la lectura larga.
 *
 * ─── Desviación respecto del plan, deliberada ───────────────────────────────
 * El plan fija `--sello: #8A9088`. Ese valor da 2.80:1 sobre `papel`, y §8
 * asigna a `sello` justamente el texto chico (metadatos, folios, etiquetas de
 * eje), que exige 4.5:1. Como §8 declara el contraste AA "no negociable", la
 * regla del plan gana sobre el hex del plan: `sello` se oscurece a #676D65
 * (4.56:1), que conserva el gris-oliva. Verificado en `color.test.ts`.
 */
export const marca = {
  papel: '#EDEEE9', // papel de oficio reciclado, gris-verdoso frío
  tinta: '#1A1D1B', // negro de fotocopia, no negro puro
  enzima: '#A8E10C', // verde ácido: el reactivo. Solo interacción y estado activo
  bilis: '#E4572E', // naranja quemado: alertas, deltas negativos, énfasis
  pulpa: '#5B4B8A', // violeta apagado: segunda serie categórica
  sello: '#676D65', // gris-oliva: metadatos, folios, texto de utilidad (ver nota)
} as const;

/**
 * Superficies derivadas. Se mantienen a un paso de `papel`/`tinta` para que la
 * jerarquía sea de espaciado y tipografía, no de cajas de colores distintos.
 */
export const superficie = {
  papelAlto: '#F6F7F3', // tarjetas sobre el papel
  papelBajo: '#DFE1DA', // franjas, filas alternas de tabla
  borde: '#C9CCC3',
  bordeFuerte: '#9BA096',
  tintaSuave: '#3D423F', // texto secundario que aún debe pasar AA
} as const;

/**
 * ═══ Escalas de gráfico ═══════════════════════════════════════════════════
 *
 * Sistema APARTE de la paleta de marca (§5). No se deriva de la marca: el
 * verde ácido y el naranja quemado se confunden entre sí al simular
 * deuteranopía, y el violeta `pulpa` colisiona con el azul bajo protanopía.
 * Esas dos colisiones se descubrieron ejecutando `color.test.ts`, no a ojo.
 *
 * ─── Por qué la categórica tope es 5 ───────────────────────────────────────
 * Bajo dicromacia el espacio perceptual colapsa a un eje azul-amarillo más
 * luminancia. Con el piso de 3:1 sobre papel claro y una familia de tono por
 * serie, la búsqueda exhaustiva (`pnpm -F @digerido/tokens explorar`, 29
 * candidatos) da:
 *
 *   k=3 → minΔE 54.8      k=5 → minΔE 25.9
 *   k=4 → minΔE 34.9      k=6 → minΔE 19.0      k=7 → sin solución
 *
 * El tope es 5 por decisión, no por imposibilidad. k=6 existe, pero su sexto
 * color es un casi-negro (#2B2D30) que queda a 1 punto de ΔE del umbral y
 * compite con la tinta de ejes y texto: una serie de datos que se lee como
 * rotulado. k=7 sí es imposible.
 *
 * Así que a partir de la sexta serie el problema no se resuelve con color, se
 * resuelve con etiqueta directa, facetado o forma (§8, "nunca codificar
 * información solo por color"). `MAX_CATEGORICA` existe para que el kit lo
 * haga cumplir en tiempo de ejecución en vez de confiar en la buena memoria.
 */
export const MAX_CATEGORICA = 5;

export const grafico = {
  /**
   * Cinco familias de tono, ordenadas por prioridad de uso. Una serie de 2
   * usa `slice(0, 2)` — azul vs. bermellón, el par seguro clásico. Nunca se
   * eligen entradas salteadas a ojo.
   */
  categorica: [
    '#0072B2', // azul
    '#D55E00', // bermellón
    '#00563F', // verde profundo
    '#3B2F58', // violeta oscuro (pariente de `pulpa`, corrido para pasar CVD)
    '#B85C8A', // rosa
  ],
  /**
   * Secuencial de un solo tono, clara → oscura. Monótona en luminancia también
   * bajo dicromacia: en una escala secuencial el ORDEN es el dato, y si el
   * orden se rompe al simular CVD la escala miente.
   *
   * Los dos pasos más claros quedan bajo 2:1 contra `papel` — inevitable y
   * correcto en una secuencial. Las marcas que los usen llevan filete
   * `--color-borde` (ver `--viz-filete`), o el valor bajo desaparece.
   */
  secuencial: ['#BFD1DF', '#96B5CB', '#6D9AB6', '#44809F', '#1A6389', '#004E7A'],
  /**
   * Divergente para deltas (recorte vs. aumento). Punto medio en `papelBajo`,
   * no blanco puro, para no abrir un agujero en el papel. Cada brazo es
   * monótono hacia afuera desde el centro; los brazos son simétricos en
   * cantidad de pasos, así el cero cae en el medio y no se corre.
   */
  divergente: ['#8C3A17', '#C25A0A', '#E0A075', '#DFE1DA', '#8FB4CB', '#2E8CC4', '#004E7A'],
  /** Marca sin valor asignado: "sin dato" es un estado, no un cero. */
  sinDato: '#C9CCC3',
  /** La marca que el lector está mirando. Un solo destacado por gráfico. */
  destacado: marca.bilis,
  /** El resto del conjunto cuando hay un destacado. */
  contexto: marca.sello,
  /** Filete para marcas de baja luminancia sobre papel. */
  filete: superficie.bordeFuerte,
} as const;

export const color = { ...marca, ...superficie } as const;
