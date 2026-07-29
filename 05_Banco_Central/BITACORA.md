# Bitácora — Banco Central

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-06-25_

Eje 15%.

## Financiamiento al Tesoro  (`scraper_18_bcra_balance.py`)
- **Estado:** OK (corregido 2026-07-29). El CSV `bcra_financiamiento_mensual` lo genera
  **`scraper_18_bcra_balance.py`** (Adelantos/Base). El `scraper_18_bcra_financiamiento.py` es
  solo un script de descubrimiento (vuelca `panhis.xls`, no produce serie) → candidato a retirar
  del orquestador. BUG resuelto: el balance quedaba congelado (abril) porque el scraper solo
  descargaba si NO existía la caché `_balbcrhis.xls`; ahora descarga siempre y refresca la caché
  (usa la copia local solo con `--offline` o si la descarga falla).
- **Fuente:** BCRA — balance histórico `balbcrhis.xls`
- **Última actualización:** 2026-07-29
- **Pendientes:** re-correr con IP AR para traer mayo/junio; evaluar retirar el `_financiamiento.py` del pipeline.

## Letras intransferibles  (`scraper_18_bcra_balance.py`)
- **Estado:** OK (corregido 2026-07-29). Misma fuente y mismo fix de caché que Financiamiento
  (las dos salen del balance); también estaba congelada en abril.
- **Fuente:** BCRA — balance histórico `balbcrhis.xls`
- **Última actualización:** 2026-07-29
- **Pendientes:** re-correr con IP AR para traer mayo/junio.

## Respeto de la Carta Orgánica (art. 20)  (`scraper_21_carta_organica.py`)
- **Estado:** OK. Recaudación vía API de Series de Tiempo.
- **Fuente:** BCRA + apis.datos.gob.ar/series
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Designación del Presidente del BCRA  (`scraper_17_bcra_designacion.py`)
- **Estado:** OK. Es un ESTADO (`sin_suavizar`): vale 0 mientras el Presidente esté «en comisión»
  (sin acuerdo del Senado) y 1 con acuerdo. El ensamblador ahora lo PERSISTE por ffill, así que
  ya no se cae de la renormalización ni infla el eje en meses parciales (antes jun-2026 saltaba
  a 83,3 por esa caída; corregido vuelve a ~66,8).
- **Fuente:** BORA / decreto PEN + acuerdo del Senado
- **Última actualización:** 2026-06-26
- **Pendientes:** Tras una alerta confirmada del radar (radar_bcra.py), actualizar el estado.

## Radar de la Presidencia del BCRA  (`radar_bcra.py`)
- **Estado:** NUEVO y OK (test 7/7). Solo-alerta: escanea el BORA y avisa designación
  (distingue «en comisión» vs «con acuerdo del Senado»), renuncia y fin de mandato del
  Presidente del BCRA. Evita trampas (Director/Vicepresidente y el boilerplate «Presidente
  de la Nación»). Corre en el workflow diario junto al radar de jueces.
- **Fuente:** BORA (`/seccion/primera/AAAAMMDD`, decisión por el cuerpo del decreto).
- **Salida:** `output/bcra_presidencia_eventos.csv` (alerta, no toca el valor publicado).
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Registro de cambios
- 2026-07-29 — FIX: `scraper_18_bcra_balance.py` descargaba el balance solo si no existía la caché
  `_balbcrhis.xls`; como el snapshot era del 8-jun (datos hasta abril), Financiamiento al Tesoro y
  Letras intransferibles quedaban congeladas en abril en cada corrida. Ahora descarga siempre y
  refresca la caché; `--offline` fuerza el uso de la copia local. Requiere re-correr con IP AR.
- 2026-06-25 — Bitácora creada.
- 2026-06-25 — Creado `radar_bcra.py` (alerta de designación/renuncia/fin de mandato del Presidente del BCRA) e integrado al workflow diario de Actions.
