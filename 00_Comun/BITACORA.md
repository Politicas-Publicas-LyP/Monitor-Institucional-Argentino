# Bitácora — Común / Ensamblado

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-06-25_

Motor del índice y configuración transversal.

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

## Registro de cambios
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
