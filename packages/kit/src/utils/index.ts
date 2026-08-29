export {
  formatoCLP, numero, porcentaje, delta, formatoFecha, formatoMesAno,
  fechaISO, duracion, tamano, hashCorto,
} from './formato.js';

export {
  legibilidad, nivelDeLegibilidad, detectarSiglas, contarSilabas,
  palabras, frases, tiempoLectura, PALABRAS_POR_MINUTO,
  type Legibilidad, type Siglas,
} from './legibilidad.js';

export {
  escalaCategorica, escalaDestacado, escalaSecuencial, colorDivergente,
  necesitaFilete, grafico, MAX_CATEGORICA,
} from './escalas.js';

export { enVista } from './interaccion.js';

export { observarAncho } from './redimension.js';
