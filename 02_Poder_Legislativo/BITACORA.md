# Bitácora — Poder Legislativo

<!-- huella: a1d2f92de812 -->

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-08-19_

Resumen: Eje Legislativo (20%) — calidad normativa (leyes vs simbólicos), eficacia de control (art. 101, informes JGM), costo del Congreso y cumplimiento de sesiones.

## Buscar acá si

- leyes sancionadas, proyectos simbólicos (declaraciones/resoluciones) → `scraper_02_calidad_normativa.py` (caché `_cache_congreso.json`; el mes en curso nunca se persiste)
- informes del Jefe de Gabinete / art. 101 → `scraper_03_eficacia_control.py` (suplemento editable `INFORMES_EXTRA` cuando la tabla del Senado atrasa)
- costo del Congreso como % del gasto → `scraper_12_costo_legislativo.py` (excluye AGN/Defensoría)
- sesiones citadas vs realizadas / fracasadas → `scraper_14_sesiones.py`
- error TLS `CERTIFICATE_VERIFY_FAILED` en sitios del Congreso → truststore (los tres scrapers lo intentan); último recurso `--insecure` en scraper_02

## Calidad normativa  (`scraper_02_calidad_normativa.py`)
- **Estado:** OK.
- **Fuente:** InfoLeg
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Eficacia de control (art. 101)  (`scraper_03_eficacia_control.py`)
- **Estado:** OK.
- **Fuente:** Congreso / InfoLeg
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Costo del Legislativo  (`scraper_12_costo_legislativo.py`)
- **Estado:** OK. Caché output/_cache_costoleg_*.
- **Fuente:** Presupuesto / ejecución
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Sesiones del Congreso  (`scraper_14_sesiones.py`)
- **Estado:** OK.
- **Fuente:** HCDN/HSN
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Registro de cambios
- 2026-08-19 — `scraper_02` importa `infoleg_source` desde `00_Comun` (única copia); la copia local
  de esta carpeta se retiró (era idéntica, quedaba huérfana).
- 2026-08-19 — TLS: los scrapers del Congreso (02, 03, 14) fallaban con
  `CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate`. HCDN no envía el certificado
  intermedio y certifi (default de requests) no sabe ir a buscarlo; el almacén del SO sí (AIA) y
  además cubre proxies/antivirus corporativos. Ahora los tres intentan `truststore.inject_into_ssl()`
  al arrancar (dependencia agregada a requirements). `scraper_02` suma `--insecure` como último
  recurso (no verifica TLS; sólo para destrabar una corrida puntual).
- 2026-08-19 — `scraper_02_calidad_normativa.py`: la caché por MES no se revalidaba, así que un mes
  cacheado mientras estaba en curso quedaba con el conteo PARCIAL para siempre (jul-2026:
  declaracion=7 vs 105 en junio). Ahora el mes en curso nunca se persiste; purgadas las claves
  parciales de jun/jul/ago (backup en `archivos_borrar/_cache_congreso_backup.json`).
- 2026-06-25 — Bitácora creada.
