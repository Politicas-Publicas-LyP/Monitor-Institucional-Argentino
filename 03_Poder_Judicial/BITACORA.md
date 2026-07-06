# Bitácora — Poder Judicial

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-06-25_

Eje 20%. Cobertura = independencia (titularidad) + funcional (vacantes sin cubrir) + flujo (nombramientos).

## Cobertura e independencia judicial  (`scraper_05_cobertura_judicial.py`)
- **Estado:** OK. STOCK del snapshot oficial + FLUJO vía radar (meses sin nombramiento) + STOCK ESTIMADO del mes corriente desde el padrón vivo.
- **Fuente:** datos.jus (IP AR); puente nombramientos vía repo
- **Última actualización:** 2026-06-25
- **Pendientes:** — (la reconciliación con cada snapshot oficial nuevo es automática).

## Padrón judicial vivo  (`padron_judicial.py`)
- **Estado:** NUEVO y OK. --construir (base oficial, reconcilia exacto) y --actualizar (aplica ALTAS del radar — 46 designaciones de jun-2026, 0 a revisión — y BAJAS de `bajas_jueces.csv`, que liberan el cargo a Vacante).
- **Fuente:** datos.jus + nombramientos_jueces.csv + bajas_jueces.csv (puente del repo)
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Desempeño de la Corte (CSJN)  (`scraper_06_resolucion_csjn.py`)
- **Estado:** OK.
- **Fuente:** CSJN
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Integridad (secundaria)  (`scraper_10_integridad.py`)
- **Estado:** Secundaria / no pondera en el valor.
- **Fuente:** OA
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Registro de cambios
- 2026-07-06 — Radar de bajas verificado en producción: el workflow de GitHub Actions detectó
  las dos renuncias del BORA del 03-jul-2026 (Decreto 570/2026, Jueza Civil N° 58 CABA; Decreto
  569/2026, TOF N° 5 San Martín), ambas confianza ALTA, y las commiteó a `bajas_jueces.csv`
  (commit `20e8fd4`). Nota operativa: la corrida programada de las 09:30 ART no las había subido;
  entraron con una corrida posterior. Revisar la fiabilidad del cron de Actions (a veces se
  retrasa/saltea); pendiente evaluar un horario de respaldo o chequeo de "última fecha procesada".
- 2026-06-25 — Padrón judicial vivo creado y calibrado (matching por tokens+número; sinónimo CABA; parser del cuerpo del BORA).
- 2026-06-25 — Cobertura: override de STOCK estimado del mes corriente.
- 2026-06-25 — Verificado que las renuncias/ceses de jueces existen en el BORA (decretos 529/2025, 530/2025, etc.).
- 2026-06-25 — Detector de BAJAS integrado al radar; el padrón ahora aplica altas y bajas (ciclo completo).
