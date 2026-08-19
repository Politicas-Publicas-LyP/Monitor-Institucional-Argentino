# Bitácora — Radar de Nombramientos (BORA)

<!-- huella: ab6da6567c94 -->

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-08-19_

Resumen: Radar del BORA (GitHub Actions, L–V 9:30 ART) — detecta ALTAS y BAJAS de jueces titulares leyendo el cuerpo de los decretos y las commitea a los CSV puente del repo.

## Buscar acá si

- el radar no detectó (o detectó mal) una designación o renuncia → `radar_nombramientos.py` (`detectar`/`detectar_baja`; probar con `--test`)
- recuperar un período pasado del BORA → `--desde/--hasta` (idempotente, dedup por URL)
- qué significa confianza ALTA/MEDIA/BAJA o la columna `confirmado` → `LEEME.md`
- el cron / el workflow de Actions (que corre también el radar BCRA) → `.github/workflows/radar_nombramientos.yml` (vive SOLO en la raíz)

## Radar de nombramientos — ALTAS y BAJAS  (`radar_nombramientos.py`)
- **Estado:** OK (test 8/8). Lee el BORA por fecha (/seccion/primera/AAAAMMDD), decide por el
  CUERPO del decreto. ALTAS: designaciones de jueces titulares (detectó las 46 del 25/06/2026).
  BAJAS: renuncia / cese / remoción / jubilación / límite de edad / fallecimiento de un juez
  (verificadas en el BORA: decretos 529, 530/2025, etc.). Salida en dos CSV puente.
- **Fuente:** BORA
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Registro de cambios
- 2026-08-19 — El workflow de Actions ahora corre PRIMERO los `--test` de ambos radares
  (8/8 y 7/7, sin red) como regresión: si una edición rompe la detección, el run falla antes
  de escanear el BORA.
- 2026-06-25 — Reescrito: lectura por fecha + detección sobre el cuerpo (arregla el bug del filtro por título).
- 2026-06-25 — Modo histórico por fecha (sin Vigía).
- 2026-06-25 — Integrado el detector de BAJAS (renuncias/ceses) → `bajas_jueces.csv`; el padrón lo lee para liberar cargos.
