# Bitácora — Común / Ensamblado

<!-- huella: 489428da0445 -->

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-08-19_

Resumen: Motor del índice — ensamblador, variables.yaml (fuente única de variables, anclas y núcleo), QA de frescura, gráficos, histórico maestro inmutable y reporte mensual .docx.

## Buscar acá si

- cambiar un ancla, un peso, un modo (suavizado/arrastre) o qué entra al Núcleo → `variables.yaml` (nunca el código; el núcleo usa `nucleo:`/`nucleo_comp`)
- el índice dio raro, una variable falta o quedó vieja → `validar.py` + tolerancias en `contracts.yaml` → `output/_alertas_validacion.md`
- congelar, reabrir o corregir un mes cerrado del histórico (inmutabilidad) → `archivar_historico.py` (`--reabrir AAAA-MM`)
- el reporte mensual .docx (plantilla LyP, 3 gráficos, tablas) → `generar_reporte_mensual.py`
- descarga compartida de InfoLEG (datos.jus) → `infoleg_source.py` (única copia; la importan los módulos 1, 2 y 4)
- exportar el Excel de la serie histórica 2020→ → `exportar_serie_historica.py`

## Ensamblador  (`icia_ensamblado.py`)
- **Estado:** OK. Lee variables.yaml; anclaje al ideal, suavizado 12m, arrastre y carryover; renormaliza por categoría sobre variables disponibles. Los ESTADOS (`sin_suavizar`) persisten por ffill: no se caen de la renormalización en meses sin fila nueva.
- **Fuente:** output/*_mensual.csv
- **Última actualización:** 2026-06-26
- **Pendientes:** —

## Fuente única de variables  (`variables.yaml`)
- **Estado:** OK. 18 variables con eje/peso/componentes/modo. Pesos macro fijos 30/20/20/15/15.
- **Fuente:** —
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## QA y frescura  (`validar.py + contracts.yaml`)
- **Estado:** OK. Notifica (no bloquea): escribe output/_alertas_validacion.md, exit 2 si hay alertas.
- **Fuente:** —
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Gráficos  (`graficar_mia.py`)
- **Estado:** OK. Consolidado, 5 ejes y núcleo.
- **Fuente:** output/mia_mensual.csv
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Histórico maestro  (`archivar_historico.py`)
- **Estado:** NUEVO y OK (2026-07-29). Acumula la serie completa (MIA + 5 ejes + 18 variables) en
  `output/mia_historico.csv` y `output/mia_historico.xlsx` (hojas *Indice*/*Variables*; copia en
  `Documentos/MIA — Serie histórica.xlsx`). UPSERT con **inmutabilidad**: los meses cerrados quedan
  congelados; el mes en curso es provisional y se congela en la 1ª corrida del mes siguiente. Corre
  al final del pipeline (tras graficar). Probado: congelamiento OK (no pisa meses cerrados).
- **Fuente:** output/mia_mensual.csv
- **Última actualización:** 2026-07-29
- **Pendientes:** —

## Reporte mensual  (`generar_reporte_mensual.py`)
- **Estado:** NUEVO y OK (2026-07-29; diseño calcado del modelo el 2026-07-29). Con el dato nuevo
  genera automáticamente el .docx **abriendo `Modelos y Administración/Modelo documento LyP.docx`
  como plantilla base** (hereda encabezado con logo, pie con banda roja de CONTACTO, estilos y
  fuentes de la casa; título y encabezados en rojo). Contenido: resumen ejecutivo factual, 3 gráficos
  (consolidado, 5 ejes y **núcleo** con bandas por gestión), tabla de ejes (pesos macro 30/20/20/15/15),
  tabla de variables que más se movieron, "Lectura de los datos" automática, y un **slot** para la
  "Lectura de Libertad y Progreso" (única parte manual → ver `Documentos/MIA — Prompt lectura institucional.md`).
  Toma el estado provisional/cerrado del histórico. Robusto al nombre de la col del núcleo (MIA_nucleo/ITR_nucleo).
  Corre al final del pipeline. Logo del repo en `00_Comun/assets/logo_lyp.png`.
- **Fuente:** output/mia_mensual.csv, mia_historico.csv, mia_nucleo_mensual.csv, variables.yaml
- **Última actualización:** 2026-07-29
- **Pendientes:** el gráfico de núcleo usa la última corrida del núcleo (hoy 2026-05); se refresca con el pipeline del núcleo.

## Serie histórica larga  (`exportar_serie_historica.py`)
- **Estado:** NUEVO y OK (2026-08-18). Exporta a un solo Excel toda la historia disponible:
  `Documentos/MIA — Serie histórica 2020-<año>.xlsx` con hojas *MIA Nucleo mensual* (2020-01 →),
  *MIA Nucleo anual*, *MIA pleno mensual* (2024-01 →, con estado provisional/cerrado), *Variables*
  (18 desagregadas) y *Notas* (aclara que los niveles del Núcleo y del pleno no coinciden).
- **Fuente:** output/mia_nucleo_mensual.csv, mia_nucleo_anual.csv, mia_historico.csv
- **Última actualización:** 2026-08-18
- **Pendientes:** —

## Registro de cambios
- 2026-08-19 — **Refactor de correspondencias (impacto en el valor: NULO, verificado byte a byte
  sobre `mia_mensual.csv`, `mia_nucleo_mensual.csv` y `mia_nucleo_anual.csv`):**
  (a) nuevo `cargar_nucleo()` en `icia_ensamblado.py` + claves `nucleo_comp` en `variables.yaml`:
  los ensambladores del núcleo (06) ahora leen el YAML en vez de listas hardcodeadas (fin de la
  triplicación de anclas); (b) `infoleg_source.py` quedó como ÚNICA copia acá (se retiraron las
  de 01 y 02; los módulos 1, 2 y 4 la importan vía `sys.path`; scraper_01 dejó de duplicar la
  descarga adentro, verificado con zip sintético); (c) `validar.py`: la frescura ahora mira el
  máximo entre TODAS las columnas usadas de cada archivo (antes una arbitraria de un set — no
  determinístico); (d) el docstring del ensamblador dejó de duplicar anclas/pesos (decía
  35/25/25/15 y anclas viejas; ahora remite a variables.yaml); (e) `contracts.yaml` sin el
  override redundante de carta_organica (= default 3); (f) `.gitignore` actualizado (ITR→MIA,
  `_panhis.xls`, logs de corrida). Además: `MAPA.md` + `.mapa/` + `scripts/indexar.py` (índice
  vivo del repo) y ADRs en `.mapa/decisiones/`.
- 2026-08-19 — **Cierre de la auditoría de frescura: verificado el impacto en el valor publicado = NULO**
  (±0,001). Los 4 bugs eran reales y había que corregirlos, pero no alteraron el índice: (a) «Medios
  estatales» recalculado sin caché da 0,0004211 vs 0,00042211 → mismo valor normalizado (71,8);
  (b) la corrupción de la caché del Congreso afectaba sólo las columnas de *simbólicas*
  (`n_declaracion/resolucion/comunicacion_pres`), que **no alimentan el índice** — «Calidad Normativa»
  usa `leyes_por_sesion` (derivada de `n_leyes_sancionadas`, que viene de InfoLEG) y
  `cumplimiento_sesiones`. Las simbólicas se publican en el CSV para análisis, no para el valor.
  Julio queda en **55,49** (congelado; el recálculo da 55,4921 vs 55,4911 congelado: diferencia por
  debajo de la precisión de publicación, no se reabre). Agosto provisional: 54,52.
- 2026-08-18 — **AUDITORÍA DE FRESCURA de los 19 scrapers** (¿consultan la fuente antes de caer al
  archivo local?). Se encontró el mismo antipatrón "caché primero" en **4** y se corrigieron todos.
  Se fijó la **regla de frescura** en AGENTS.md (Convenciones de scrapers). Detalle:
  · `scraper_18_bcra_balance.py` (corregido 29-jul): sólo descargaba si NO existía `_balbcrhis.xls`
    → Financiamiento y Letras congeladas en abril.
  · `scraper_21_carta_organica.py`: priorizaba el snapshot `_recaudacion.csv` → sin dato desde jun-2026
    pese a que la API ya publicaba jun/jul. Ahora API primero + refresco del snapshot.
  · `scraper_20_medios_oficiales.py`: caché anual **sin** el guard `anio < año actual` (que sus pares
    ATN/pauta/costo sí tenían) → «Medios estatales» congelada en 0,00042211 desde el 8-jun.
  · `scraper_02_calidad_normativa.py`: caché por MES sin guard → un mes cacheado mientras estaba en
    curso quedaba con el conteo PARCIAL para siempre (p. ej. `declaracion|2026-07 = 7` vs 105 en junio),
    corrompiendo incluso meses ya cerrados. Ahora el mes en curso nunca se persiste; se purgaron las
    9 claves parciales de jun/jul/ago (backup en `archivos_borrar/_cache_congreso_backup.json`).
  Verificados como CORRECTOS (consultan la fuente o cachean sólo ítems inmutables): dnu_leyes,
  discrecionalidad, transparencia_v2, atn, eficacia_control, costo_legislativo, sesiones,
  resolucion_csjn (anual por diseño), cobertura_judicial (URL primero), padron_judicial, escrutinio,
  pauta, prensa_causas y acceso_prensa (listado fresco + caché por id), bcra_designacion y los radares.
- 2026-08-18 — `archivar_historico.py`: nueva opción **`--reabrir AAAA-MM`** para recalcular a
  propósito un mes ya congelado (caso típico: una fuente rezagada —balance del BCRA, cierres de
  AAIP— publica después del primer congelamiento). Es decisión humana y queda registrada en la
  columna `actualizado`. Sin la opción, la inmutabilidad se mantiene igual. Probado (test OK).
- 2026-08-18 — Nuevo `exportar_serie_historica.py` (Excel histórico 2020 →). Núcleo mensual
  re-corrido hasta 2026-07 y ya con la columna `MIA_nucleo`.
- 2026-07-29 — Diseño: el reporte mensual y **todos los .docx MIA** se pasaron al diseño del
  `Modelo documento LyP.docx` (encabezado con logo, pie con banda roja de CONTACTO, estilos/fuentes
  de la casa; título/encabezados en rojo). Los reportes mensuales lo heredan del generador; el resto
  se migró transplantando el cuerpo a la plantilla (originales respaldados en `archivos_borrar/pre_plantilla`).
- 2026-07-29 — Nuevo `generar_reporte_mensual.py`: arma el reporte mensual (.docx) automático con
  3 gráficos + tablas + lectura factual y slot LyP; integrado al pipeline. Deps: python-docx.
- 2026-07-29 — Nuevo `archivar_historico.py`: histórico maestro acumulado (CSV + Excel 2 hojas) con
  meses cerrados congelados; integrado a `correr_mensual.bat`/`.sh`.
- 2026-07-06 — Renombre integral del índice: **Índice de Transparencia Republicana (ITR) → Monitor Institucional Argentino (MIA)**. Afectó código, columna de datos (`ITR`→`MIA`), nombres de archivo (`itr_*`→`mia_*`, `graficar_mia.py`, `mia_nucleo_*.py`), variable de entorno (`ITR_RADAR_CSV_URL`→`MIA_RADAR_CSV_URL`), documentos y bitácoras. PENDIENTE (manual): renombrar la carpeta raíz y el repositorio de GitHub, y actualizar la URL del repo y la variable de entorno donde esté seteada.
- 2026-06-29 — Limpieza: 51 CSV `*_mensual_*` viejos (duplicados timestamped) movidos a `archivos_borrar/`
  (ignorada por git); queda 1 por variable. Caches/snapshots intactos. `matplotlib` agregado a requirements.
- 2026-06-26 — Estados (`sin_suavizar`) ahora persisten por ffill: corrige la inflación de ejes
  en meses parciales cuando un estado no tiene fila nueva (Designación Pdte. BCRA, presupuesto aprobado).
- 2026-06-25 — Override de cobertura ESTIMADA del mes corriente desde el padrón vivo (vía scraper_05).
- 2026-06-25 — Bitácora creada.
