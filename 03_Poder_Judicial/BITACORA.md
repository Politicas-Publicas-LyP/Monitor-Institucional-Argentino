# Bitácora — Poder Judicial

<!-- huella: 5c3e86b4f3ef -->

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-08-19_

Resumen: Eje Judicial (20%) — cobertura/titularidad de jueces (dataset oficial + padrón vivo + radar del BORA) y desempeño de la CSJN (anuarios); PIA/OA queda como exploración.

Cobertura = independencia (titularidad) + funcional (vacantes sin cubrir) + flujo (nombramientos).

## Buscar acá si

- titularidad, subrogancia, vacancia o el padrón de cargos de jueces → `padron_judicial.py` (`--construir` / `--actualizar`; estimado vs oficial)
- meses sin nombramiento, puente con el radar del BORA → `scraper_05_cobertura_judicial.py` (`fechas_radar()`, env `MIA_RADAR_CSV_URL`)
- tasa de resolución, mediana de días, vacantes de la Corte → `scraper_06_resolucion_csjn.py` (cifras verificadas + `CSJN_MIEMBROS_REGLAS`; cadencia ANUAL: constante entre anuarios es normal)
- un evento del BORA no se aplicó al padrón → `output/padron_revision.csv` (cola de revisión humana)
- integridad / PIA / OA (NO pondera en el índice) → `scraper_10_integridad.py`

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
- **Estado:** OK (revisado 2026-08-18). Variable **estructural de cadencia ANUAL**: la fuente son los
  Anuarios Estadísticos de la CSJN, y el scraper la lleva a serie mensual por forward-fill con contador
  `stale_meses`. Por eso está **constante en 30,0 desde nov-2025** (`stale_meses`=8; siempre el mismo
  anuario: tasa de resolución 0,454, mediana 364 días, originaria 2.082 días). No es un fallo del
  scraper. **DECISIÓN (2026-08-18): se deja así, es estructural** — se actualizará cuando la Corte
  publique el próximo anuario. Se evaluó y descartó bajar la tolerancia de alerta del QA (hoy 14 meses).
- **Fuente:** CSJN (Anuarios Estadísticos, PDF — anual)
- **Última actualización:** 2026-08-18
- **Pendientes:** al salir el anuario nuevo, re-correr para descongelar la variable.

## Integridad (secundaria)  (`scraper_10_integridad.py`)
- **Estado:** Secundaria / no pondera en el valor.
- **Fuente:** OA
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Registro de cambios
- 2026-08-19 — `scraper_10_integridad.py`: marcado en el propio docstring como SECUNDARIO /
  EXPLORATORIO (no alimenta variables.yaml ni está en los orquestadores), para que la
  correspondencia quede explícita en el archivo y no solo acá.
- 2026-08-18 — Auditoría del eje: se verificó que la escasa variación NO es un error. «Cobertura
  Judicial» sí se mueve (68,8 jun → 67,7 jul → 67,4 ago); «Desempeño de la Corte» está congelada por
  la cadencia anual del anuario CSJN (ver arriba), y pesa 15% dentro del eje, lo que amortigua el
  Judicial mientras no salga anuario nuevo.
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
