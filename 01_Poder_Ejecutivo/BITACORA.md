# Bitácora — Poder Ejecutivo

<!-- huella: 5f6f039323ca -->

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-09-18_

Resumen: Eje Ejecutivo (30%) — DNU vs Leyes (InfoLEG), discrecionalidad presupuestaria (OPC+BO), transparencia AIP (AAIP) y ATN a provincias (DGSIAF).

## Buscar acá si

- DNU, decretos o leyes; la marca oficial `clase_norma` de InfoLEG → `scraper_01_dnu_leyes.py`
- presupuesto aprobado vs prórroga, o modificaciones por DA/DNU (OPC) → `scraper_04_discrecionalidad.py` (tabla `PRESUPUESTO_APROBADO`, actualizar cada año)
- pedidos de acceso a la información, tasa de respuesta o en plazo → `scraper_11_transparencia_v2.py` (fechado por mes de RESOLUCIÓN)
- ATN, reparto discrecional a provincias, share del gasto → `scraper_16_atn.py` (inmutabilidad en `atn_obs_mensual.csv`; fallback por Jurisdicción 30/Programa 19 para 2003-2016 sin etiqueta de texto)
- una variable del eje quedó plana durante meses → revisar cachés ANTES de concluir "sin novedades" (regla de frescura, AGENTS.md)

## DNU vs Leyes  (`scraper_01_dnu_leyes.py`)
- **Estado:** OK.
- **Fuente:** InfoLeg
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Discrecionalidad presupuestaria  (`scraper_04_discrecionalidad.py`)
- **Estado:** OK. Ojo: en mes en curso el flujo parcial distorsiona (ver muestra de junio).
- **Fuente:** DGSIAF (IP AR)
- **Última actualización:** 2026-06-25
- **Pendientes:** Marcar/avisar cuando el mes está incompleto.

## Transparencia (AIP)  (`scraper_11_transparencia_v2.py`)
- **Estado:** OK (redefinida 2026-07-29). Ahora fecha por **mes de RESOLUCIÓN** (`fecha_ultimo_pase`
  de los expedientes terminales), no por mes de INICIO del pedido. Cuenta lo que se CERRÓ en el mes
  (Resuelto/Vencido); los abiertos entran cuando se resuelven o vencen. Se eliminó el gate de
  madurez (ya no hace falta) → la variable queda disponible para el mes en curso (nowcast). Sigue
  publicando `tasa_respuesta` y `tasa_en_plazo` (mismas columnas que lee variables.yaml).
- **Fuente:** AAIP (microdato sip.csv)
- **Última actualización:** 2026-07-29
- **Pendientes:** al re-correr con IP AR, chequear que las anclas (0,95/0,30 y 0,90/0,20) sigan
  razonables con la serie fechada por resolución.

## ATN (federalismo)  (`scraper_16_atn.py`)
- **Estado:** OK. El índice usa el **share MENSUAL** (`atn_share_mensual`, crédito mensual DGSIAF),
  no el anual: refleja la discrecionalidad mes a mes. Columnas extra: `atn_share` (anual, referencia)
  y `atn_var_mom_pp` (variación vs mes anterior). **Inmutabilidad de publicación**: los meses
  cerrados quedan fijos en `output/atn_obs_mensual.csv` (versionado) y no se recalculan en corridas
  futuras. **Fallback** al share anual donde no hay mensual (años viejos) → no rompe el núcleo.
  Caché solo de años CERRADOS (el año en curso se recalcula).
  **CORREGIDO 2026-09-17** (tres bugs, ver registro): «sin dato» ya no se publica como 0,0;
  el mes EN CURSO ya no se congela con su devengado parcial; las cachés envenenadas se
  auto-descartan. **CORREGIDO 2026-09-18**: identificación por texto + fallback por código de
  estructura programática para 2003-2016 (ver registro) → serie completa 2003-2026, sin
  huecos de SIN DATO.
- **Fuente:** DGSIAF crédito mensual y anual
- **Última actualización:** 2026-09-18
- **Pendientes:** ninguno abierto. Si en el futuro un año nuevo vuelve a dar SIN DATO (el
  fallback no encuentra Jurisdicción 30/Programa 19, o su dominancia cae debajo de 70%),
  correr `--diagnostico <año>` y revisar a mano — puede ser otra reorganización ministerial.

## Registro de cambios
- 2026-09-18 — **ATN: fallback por código de estructura programática para 2003-2016.**
  Los `--diagnostico` de 2005/2010/2015 no encontraron ninguna etiqueta de texto reconocible
  para el ATN en esos ejercicios (confirmado luego para los 14 años 2003-2016). Investigación
  de fuentes alternativas (API de presupuestoabierto.gob.ar, Tesorería General, OPC) no dio
  un dataset estructurado utilizable — el hallazgo real vino de abrir el ZIP crudo de DGSIAF
  con sus columnas de ID: el ATN vive siempre en **Jurisdicción 30** (Ministerio del Interior,
  con sus distintos nombres a través del tiempo) → **Programa 19**, estable 2003-2024. Dentro
  de ese programa, la actividad de mayor devengado es el ATN en el 88%-100% del programa en
  los 14 años 2003-2016 (nunca ambiguo en esa ventana). Validado contra una fuente
  independiente: el Informe 78 de Jefatura de Gabinete al Congreso (15/09/2010) reporta
  "TOTAL DISTRIBUIDO A LAS PROVINCIAS EN 2010 = $215.705.000" con desglose por provincia que
  coincide fila por fila (varias con match exacto) contra esa actividad en el ZIP de 2010.
  Se agregó `_mask_fallback_programa19()`: se activa SOLO cuando el matcheo de texto no
  encuentra nada (nunca reemplaza al texto cuando este funciona, que es más robusto — el
  Ministerio del Interior fue absorbido por Jefatura de Gabinete en 2025 y la etiqueta de
  texto ATN siguió matcheando igual, mientras que el código de jurisdicción si se movió) y
  exige dominancia ≥70% dentro del programa para confiar en el resultado sin revisión humana.
  Resultado: `atn_obs_mensual.csv` pasó de 115 a 284 filas (cobertura completa 2003-2026, sin
  huecos). El MIA Núcleo se recalculó completo con esto — el eje Ejecutivo de 2003-2016 cambia
  (antes excluía el ATN por falta de dato; ahora lo incluye con valor real).
  **Descartado en el camino:** la fuente "Aportes y remanentes del Tesoro Nacional" de
  Tesorería (`argentina.gob.ar/economia/tesoreria-general-de-la-nacion`) NO sirve — es el
  sistema COTENA, organismos devolviendo remanentes AL Tesoro, la dirección opuesta al ATN.
  El clasificador económico genérico "Transferencias a Gobiernos Provinciales" tampoco sirve:
  para 2010 da $26.909M contra un ATN real de ~$300M (83x más grande) — es un agregado de
  TODAS las transferencias a provincias, no solo el ATN discrecional.
- 2026-09-17 — **Tres bugs del ATN corregidos** (los tres del mismo tipo: un valor que no se
  pudo medir se estaba publicando como si fuera una medición).
  1. **SIN DATO publicado como CERO.** Si ninguna fila del ejercicio matcheaba la etiqueta
     «Aportes del Tesoro Nacional», el scraper devolvía `share = 0,0`. Con anclas
     `mejor=0,001 / peor=0,007`, un 0 normaliza a **100 = federalismo ideal**. Así quedaron
     **2003–2016 completos en 0,0** (168 meses), inflando el eje Ejecutivo del **MIA Núcleo**
     en toda la serie larga. Ahora, 0 filas matcheadas sobre un devengado total > 0 devuelve
     **SIN DATO** (`None`), avisa por log y sugiere `--diagnostico`.
  2. **El mes en curso quedaba congelado en su valor PARCIAL.** `atn_obs_mensual.csv` es
     inmutable por diseño, pero persistía también el mes corriente; al cerrar ese mes, la
     regla de inmutabilidad lo dejaba fijo con el devengado parcial de la última corrida.
     **2026-08 estaba en 0,0 observado el 19-ago** (mes a medio transcurrir) y se habría
     publicado así para siempre. Ahora el mes en curso **nunca** entra al store: se usa sólo
     en memoria para el nowcast de la serie y se observa recién en la primera corrida del mes
     siguiente. Mismo patrón que el bug de caché de `scraper_02_calidad_normativa.py`.
  3. **Cachés envenenadas.** Los 0,0 de (1) quedaban guardados en `_cache_atn_{año}.csv` y
     `_cache_atn_mensual_{año}.csv` como dato definitivo, así que arreglar el patrón no
     alcanzaba: la caché los seguía sirviendo. Ahora una caché anual con `atn_dev = 0`, o una
     mensual con los 12 meses en 0, se **descarta y recalcula**.
  Además se amplió `PATRON` a «Aporte(s) [no reintegrables] del Tesoro [Nacional]» (la
  redacción varía entre ejercicios) sin matchear la FUENTE de financiamiento «Tesoro Nacional».
  Purga aplicada a `output/atn_obs_mensual.csv`: se borraron los 168 ceros artificiales de
  2003-01..2016-12 y el parcial congelado de 2026-08. **Requiere re-correr desde IP AR.**
  OJO: los ceros de 2020-01, 2021-04/05, 2022-08/10, 2024-07/08/09/12, 2025-11, 2026-05/06
  **son reales** (meses sin ATN) y se conservan: el año tiene matches, el mes no tiene monto.
- 2026-08-19 — `scraper_01_dnu_leyes.py` ahora usa la fuente compartida `00_Comun/infoleg_source.py`
  (antes duplicaba adentro la descarga/parseo/fechas). La copia local `infoleg_source.py` de esta
  carpeta se retiró; `scraper_04` la importa de 00_Comun vía `sys.path`. Comportamiento verificado
  con un ZIP sintético (clasificación, agregado mensual y `_fecha_origen` idénticos).
- 2026-07-29 — Transparencia (AIP): reescrito el fechado — de mes de INICIO del pedido a **mes de
  RESOLUCIÓN** (`fecha_ultimo_pase`). Mide "la tasa del mes" (cerrados = Resuelto/Vencido) y se sacó
  el gate de madurez. Cambia retroactivamente la serie de esta variable (y levemente el eje Ejecutivo
  y el MIA histórico). Requiere re-correr con IP AR. Probado en seco (test sintético OK).
- 2026-06-25 — Bitácora creada.
