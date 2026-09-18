# Bitácora — Poder Judicial

<!-- huella: e52390fd718c -->

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-09-18_

Resumen: Eje Judicial (20%) — cobertura/titularidad de jueces (dataset oficial + padrón vivo + radar del BORA) y desempeño de la CSJN (anuarios); PIA/OA queda como exploración.

Cobertura = independencia (titularidad) + funcional (vacantes sin cubrir) + flujo (nombramientos).

## Buscar acá si

- titularidad, subrogancia, vacancia o el padrón de cargos de jueces → `padron_judicial.py` (`--construir` / `--actualizar`; estimado vs oficial; altas también desde el Consejo de la Magistratura, complementario al radar del BORA)
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
- **Estado:** OK. --construir (base oficial, reconcilia exacto) y --actualizar (aplica ALTAS del
  radar — 46 designaciones de jun-2026, 0 a revisión — y BAJAS de `bajas_jueces.csv`, que liberan
  el cargo a Vacante). **AMPLIADO 2026-09-18**: ahora también lee altas confirmadas del Consejo de
  la Magistratura (`export_remitidos.php`, "Ternas remitidas al PEN" con `fecha_designación`) como
  tercera fuente, complementaria al radar del BORA — no lo reemplaza. Impacto medido en la corrida
  de prueba: `tasa_titular` estimada pasó de 0,7177/0,6325 (según el corte de la serie) a **0,7937**
  — el Consejo capturó designaciones que el radar (basado en texto de decretos del BORA) no había
  podido mapear. 0 eventos a revisión; 19 altas del Consejo resultaron ya aplicadas por el radar en
  la misma corrida y se descartan sin ruido (no van a `padron_revision.csv`).
- **Fuente:** datos.jus + nombramientos_jueces.csv + bajas_jueces.csv (puente del repo) + Consejo de
  la Magistratura (mapadeconcursos)
- **Última actualización:** 2026-09-18
- **Pendientes:** las otras dos exportaciones del Consejo ("en trámite en CM" y "concluidos") NO se
  integraron — tienen columnas de texto libre (órdenes de mérito con nombres y puntajes separados
  por comas SIN escapar) que rompen el parseo CSV fila por fila; son un problema de calidad de dato
  de la fuente, no de acceso. Si el Consejo corrige el export en el futuro, ahí sí valdría sumar el
  conteo de "vacantes en trámite" como cross-check adicional de `tasa_sin_cobertura`.

## Desempeño de la Corte (CSJN)  (`scraper_06_resolucion_csjn.py`)
- **Estado:** OK (revisado 2026-08-18). Variable **estructural de cadencia ANUAL**: la fuente son los
  Anuarios Estadísticos de la CSJN, y el scraper la lleva a serie mensual por forward-fill con contador
  `stale_meses`. Por eso está **constante en 30,0 desde nov-2025** (`stale_meses`=8; siempre el mismo
  anuario: tasa de resolución 0,454, mediana 364 días, originaria 2.082 días). No es un fallo del
  scraper. **DECISIÓN (2026-08-18): se deja así, es estructural** — se actualizará cuando la Corte
  publique el próximo anuario. Se evaluó y descartó bajar la tolerancia de alerta del QA (hoy 14 meses).
- **Fuente:** CSJN (Anuarios Estadísticos, PDF — anual)
- **Última actualización:** 2026-09-18
- **Pendientes:** al salir el anuario nuevo, re-correr para descongelar la variable.
  **INVESTIGADO 2026-09-18 (candidato descartado):** la CSJN publica un "Informe 1er Semestre"
  (2025 y 2026) que en teoría reduciría la espera de ~12 a ~6 meses, pero corre en un tablero de
  **Tableau Public** con la exportación de datos deshabilitada por la propia Corte
  (`allow_export_data: false`, `allow_view_underlying: false` en la config de la sesión —
  verificado inspeccionando el tráfico de red del tablero). La librería estándar para esto
  (`tableauscraper`) falla contra la versión actual de Tableau (2026.2): la página ya no expone
  el bootstrap de datos server-side (`textarea#tsConfigContainer` vacío), lo carga por JS después
  de un `POST /vizql/.../startSession`. Se podría seguir reverse-engineering ese protocolo, pero
  dado que la propia Corte restringió a propósito la exportación, no parece el camino correcto —
  se prefiere dejar la fuente como está (anuario) antes que forzar una vía que el publicador
  cerró deliberadamente. El PDF del informe semestral tampoco es una alternativa hoy: existe para
  2025 pero **no para 2026** (el semestre más reciente solo tiene el tablero). Sin cambios.

## Integridad (secundaria)  (`scraper_10_integridad.py`)
- **Estado:** Secundaria / no pondera en el valor.
- **Fuente:** OA
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Registro de cambios
- 2026-09-18 — **Padrón judicial: Consejo de la Magistratura como tercera fuente de altas.**
  Siguiendo la auditoría de las 18 variables del índice, se investigaron dos candidatos para
  mejorar el eje Judicial:
  1. **Implementado:** `padron_judicial.py` ahora descarga `export_remitidos.php` del Mapa de
     Concursos del Consejo (`mc.consejomagistratura.gov.ar`) — "Ternas remitidas al PEN", con
     `fecha_designación` por concurso/juzgado — y lo trata como una fuente de altas más, igual
     que el radar del BORA (`_cargar_eventos_consejo()`, confianza ALTA por venir ya confirmada
     por el propio Consejo). Se corrigió un bug de la fuente (fechas con el siglo en cero, ej.
     "0026-06-16"). Probado en producción: 128 designaciones leídas, 166 altas aplicadas sobre
     185 eventos totales (BORA + Consejo), **0 a revisión humana**, 19 descartadas sin ruido por
     estar ya aplicadas por el radar. `tasa_titular` estimada subió de ~0,72/0,63 a **0,79**.
     Las otras dos exportaciones del Consejo ("en trámite" y "concluidos") se descartaron por
     tener columnas de texto libre que rompen el CSV (comas sin escapar en listados de mérito).
  2. **Descartado (no implementado):** reemplazar/complementar el anuario de la CSJN con su
     informe semestral — el tablero (Tableau Public) tiene la exportación de datos deshabilitada
     por la propia Corte; forzarla por scraping de protocolo no parece apropiado dado que es una
     restricción deliberada del publicador, no solo una dificultad técnica. Ver detalle arriba.
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
