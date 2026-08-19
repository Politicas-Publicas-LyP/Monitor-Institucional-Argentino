# Bitácora — Poder Ejecutivo

<!-- huella: 4fada65713a7 -->

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-08-19_

Resumen: Eje Ejecutivo (30%) — DNU vs Leyes (InfoLEG), discrecionalidad presupuestaria (OPC+BO), transparencia AIP (AAIP) y ATN a provincias (DGSIAF).

## Buscar acá si

- DNU, decretos o leyes; la marca oficial `clase_norma` de InfoLEG → `scraper_01_dnu_leyes.py`
- presupuesto aprobado vs prórroga, o modificaciones por DA/DNU (OPC) → `scraper_04_discrecionalidad.py` (tabla `PRESUPUESTO_APROBADO`, actualizar cada año)
- pedidos de acceso a la información, tasa de respuesta o en plazo → `scraper_11_transparencia_v2.py` (fechado por mes de RESOLUCIÓN)
- ATN, reparto discrecional a provincias, share del gasto → `scraper_16_atn.py` (inmutabilidad en `atn_obs_mensual.csv`)
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
- **Fuente:** DGSIAF crédito mensual y anual
- **Última actualización:** 2026-06-29
- **Pendientes:** ATN histórico para llegar a Macri (parqueado).

## Registro de cambios
- 2026-08-19 — `scraper_01_dnu_leyes.py` ahora usa la fuente compartida `00_Comun/infoleg_source.py`
  (antes duplicaba adentro la descarga/parseo/fechas). La copia local `infoleg_source.py` de esta
  carpeta se retiró; `scraper_04` la importa de 00_Comun vía `sys.path`. Comportamiento verificado
  con un ZIP sintético (clasificación, agregado mensual y `_fecha_origen` idénticos).
- 2026-07-29 — Transparencia (AIP): reescrito el fechado — de mes de INICIO del pedido a **mes de
  RESOLUCIÓN** (`fecha_ultimo_pase`). Mide "la tasa del mes" (cerrados = Resuelto/Vencido) y se sacó
  el gate de madurez. Cambia retroactivamente la serie de esta variable (y levemente el eje Ejecutivo
  y el MIA histórico). Requiere re-correr con IP AR. Probado en seco (test sintético OK).
- 2026-06-25 — Bitácora creada.
