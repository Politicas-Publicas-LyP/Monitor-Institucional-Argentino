# MAPA — Monitor Institucional Argentino (MIA)

<!-- GENERADO por indexar.py. No editar: los cambios se pierden. -->
<!-- La prosa vive en las BITACORA.md de cada carpeta. -->
<!-- 2026-08-19 17:22 UTC · 41 archivos · 7,860 LOC -->

## Como usar este archivo

Es el unico archivo del proyecto que hace falta leer para empezar. Para ubicar algo concreto: `python3 .mapa/buscar.py "<termino>"` devuelve archivo y linea sin abrir nada. Recien despues abrir los archivos que salgan, y solo esos.

Rama `main` — ultimo commit: 2026-08-18 4fcfcd0 Corrida Julio completo · **hay cambios sin commitear**

## Donde buscar que

| Si la consulta es sobre... | Ir a |
|---|---|
| correr el mes, cerrar un mes puntual o el cron del server → `correr_mensual.bat` / `correr_mensual.sh` (+ `Documentos/MIA — Runbook de la corrida mensual.md`) | `./` |
| el pipeline "falló" pero era solo QA con avisos → `correr_mensual.sh` (exit 2 de validar.py NO cuenta como fallo desde 2026-08-19) | `./` |
| los radares diarios del BORA en la nube → `.github/workflows/radar_nombramientos.yml` (corre jueces + Presidencia BCRA y commitea los CSV puente) | `./` |
| qué se versiona y qué no (cachés, logs, archivos_borrar) → `.gitignore` | `./` |
| ubicar código sin releer el repo → `MAPA.md` y `python3 .mapa/buscar.py "<término>"`; reindexar: `python3 scripts/indexar.py .` | `./` |
| cambiar un ancla, un peso, un modo (suavizado/arrastre) o qué entra al Núcleo → `variables.yaml` (nunca el código; el núcleo usa `nucleo:`/`nucleo_comp`) | `00_Comun/` |
| el índice dio raro, una variable falta o quedó vieja → `validar.py` + tolerancias en `contracts.yaml` → `output/_alertas_validacion.md` | `00_Comun/` |
| congelar, reabrir o corregir un mes cerrado del histórico (inmutabilidad) → `archivar_historico.py` (`--reabrir AAAA-MM`) | `00_Comun/` |
| el reporte mensual .docx (plantilla LyP, 3 gráficos, tablas) → `generar_reporte_mensual.py` | `00_Comun/` |
| descarga compartida de InfoLEG (datos.jus) → `infoleg_source.py` (única copia; la importan los módulos 1, 2 y 4) | `00_Comun/` |
| exportar el Excel de la serie histórica 2020→ → `exportar_serie_historica.py` | `00_Comun/` |
| DNU, decretos o leyes; la marca oficial `clase_norma` de InfoLEG → `scraper_01_dnu_leyes.py` | `01_Poder_Ejecutivo/` |
| presupuesto aprobado vs prórroga, o modificaciones por DA/DNU (OPC) → `scraper_04_discrecionalidad.py` (tabla `PRESUPUESTO_APROBADO`, actualizar cada año) | `01_Poder_Ejecutivo/` |
| pedidos de acceso a la información, tasa de respuesta o en plazo → `scraper_11_transparencia_v2.py` (fechado por mes de RESOLUCIÓN) | `01_Poder_Ejecutivo/` |
| ATN, reparto discrecional a provincias, share del gasto → `scraper_16_atn.py` (inmutabilidad en `atn_obs_mensual.csv`) | `01_Poder_Ejecutivo/` |
| una variable del eje quedó plana durante meses → revisar cachés ANTES de concluir "sin novedades" (regla de frescura, AGENTS.md) | `01_Poder_Ejecutivo/` |
| leyes sancionadas, proyectos simbólicos (declaraciones/resoluciones) → `scraper_02_calidad_normativa.py` (caché `_cache_congreso.json`; el mes en curso nunca se persiste) | `02_Poder_Legislativo/` |
| informes del Jefe de Gabinete / art. 101 → `scraper_03_eficacia_control.py` (suplemento editable `INFORMES_EXTRA` cuando la tabla del Senado atrasa) | `02_Poder_Legislativo/` |
| costo del Congreso como % del gasto → `scraper_12_costo_legislativo.py` (excluye AGN/Defensoría) | `02_Poder_Legislativo/` |
| sesiones citadas vs realizadas / fracasadas → `scraper_14_sesiones.py` | `02_Poder_Legislativo/` |
| error TLS `CERTIFICATE_VERIFY_FAILED` en sitios del Congreso → truststore (los tres scrapers lo intentan); último recurso `--insecure` en scraper_02 | `02_Poder_Legislativo/` |
| titularidad, subrogancia, vacancia o el padrón de cargos de jueces → `padron_judicial.py` (`--construir` / `--actualizar`; estimado vs oficial) | `03_Poder_Judicial/` |
| meses sin nombramiento, puente con el radar del BORA → `scraper_05_cobertura_judicial.py` (`fechas_radar()`, env `MIA_RADAR_CSV_URL`) | `03_Poder_Judicial/` |
| tasa de resolución, mediana de días, vacantes de la Corte → `scraper_06_resolucion_csjn.py` (cifras verificadas + `CSJN_MIEMBROS_REGLAS`; cadencia ANUAL: constante entre anuarios es normal) | `03_Poder_Judicial/` |
| un evento del BORA no se aplicó al padrón → `output/padron_revision.csv` (cola de revisión humana) | `03_Poder_Judicial/` |
| integridad / PIA / OA (NO pondera en el índice) → `scraper_10_integridad.py` | `03_Poder_Judicial/` |
| conferencias de prensa vs cadenas nacionales (Casa Rosada) → `scraper_07_escrutinio.py` | `04_Prensa_Institucional/` |
| pauta publicitaria oficial como % del gasto → `scraper_08_pauta.py` (DGSIAF anual) | `04_Prensa_Institucional/` |
| causas judiciales contra periodistas (categoría FOPEA) → `scraper_13_prensa_causas.py` (caché por id inmutable) | `04_Prensa_Institucional/` |
| RTA / Télam / medios estatales, share del gasto → `scraper_20_medios_oficiales.py` (caché solo años cerrados) | `04_Prensa_Institucional/` |
| sala de prensa, acreditaciones, restricciones de acceso → `scraper_22_acceso_prensa.py` (tabla `ACREDITACIONES` mantenida a mano + FOPEA; modo arrastre 3m) | `04_Prensa_Institucional/` |
| adelantos/base monetaria o letras/activo → `scraper_18_bcra_balance.py` (balbcrhis.xls, columnas POR POSICIÓN; descarga siempre, caché solo `--offline`) | `05_Banco_Central/` |
| tope del art. 20 de la Carta Orgánica / recaudación → `scraper_21_carta_organica.py` (API Series de Tiempo primero; 100 = cumple, es un test de cumplimiento) | `05_Banco_Central/` |
| con/sin acuerdo del Senado del Presidente del BCRA → `scraper_17_bcra_designacion.py` (tabla `CONFIG` mantenida a mano; pre-2019 CONFIRMAR) | `05_Banco_Central/` |
| alerta de designación/renuncia/fin de mandato en el BORA → `radar_bcra.py` (solo-alerta, corre en Actions) | `05_Banco_Central/` |
| explorar la estructura de panhis.xls (factores de la base) → `diagnostico_panhis.py` (FUERA del pipeline) | `05_Banco_Central/` |
| la serie histórica larga o la comparación entre gestiones → `mia_nucleo_mensual.py` (2020+) / `mia_nucleo_historico.py` (anual 2003+) | `06_Historico/` |
| qué variables entran al núcleo, o sus anclas/componentes → `00_Comun/variables.yaml` (`nucleo:` y `nucleo_comp:`; acá NO hay listas propias desde 2026-08-19) | `06_Historico/` |
| correr toda la historia (scrapers --desde 2003 + ensamble) → `correr_nucleo_historico.bat` | `06_Historico/` |
| por qué el núcleo y el pleno dan niveles distintos → docstring de `00_Comun/exportar_serie_historica.py` (hoja Notas) | `06_Historico/` |
| el radar no detectó (o detectó mal) una designación o renuncia → `radar_nombramientos.py` (`detectar`/`detectar_baja`; probar con `--test`) | `07_Radar_Nombramientos/` |
| recuperar un período pasado del BORA → `--desde/--hasta` (idempotente, dedup por URL) | `07_Radar_Nombramientos/` |
| qué significa confianza ALTA/MEDIA/BAJA o la columna `confirmado` → `LEEME.md` | `07_Radar_Nombramientos/` |
| el cron / el workflow de Actions (que corre también el radar BCRA) → `.github/workflows/radar_nombramientos.yml` (vive SOLO en la raíz) | `07_Radar_Nombramientos/` |
| reindexar el proyecto o sellar una bitácora → `indexar.py` (`python3 scripts/indexar.py .` / `--sellar <carpeta>` / `--estructura`) | `scripts/` |
| consultar el índice sin abrir archivos → `.mapa/buscar.py` (copiado automáticamente por el indexador) | `scripts/` |
| automatizar el reindexado en cada commit → `hook-pre-commit` (copiar a `.git/hooks/pre-commit`) | `scripts/` |

## Carpetas

| Carpeta | Que es | Arch. | LOC | Bitacora |
|---|---|---:|---:|---|
| `03_Poder_Judicial/` | Eje Judicial (20%) — cobertura/titularidad de jueces (dataset oficial + padrón vivo + radar del BORA) y desempeño de la CSJN (anuarios); PIA/OA queda como exploración. | 4 | 1,294 | **vencida** |
| `00_Comun/` | Motor del índice — ensamblador, variables.yaml (fuente única de variables, anclas y núcleo), QA de frescura, gráficos, histórico maestro inmutable y reporte mensual .docx. | 9 | 1,222 | **vencida** |
| `01_Poder_Ejecutivo/` | Eje Ejecutivo (30%) — DNU vs Leyes (InfoLEG), discrecionalidad presupuestaria (OPC+BO), transparencia AIP (AAIP) y ATN a provincias (DGSIAF). | 4 | 1,020 | **vencida** |
| `scripts/` | Herramientas del mapa vivo del repo (mapa-de-proyectos): indexador que genera MAPA.md/.mapa y hook pre-commit opcional. | 2 | 933 | **vencida** |
| `04_Prensa_Institucional/` | Eje Prensa (15%) — escrutinio (conferencias vs cadenas), pauta oficial, causas judiciales contra periodistas (FOPEA), medios estatales y acceso de la prensa. | 5 | 826 | **vencida** |
| `05_Banco_Central/` | Eje Banco Central (15%) — financiamiento al Tesoro y letras intransferibles (balance BCRA), designación del Presidente (estado mantenido) y respeto de la Carta Orgánica; más el radar BORA de la Presidencia. | 5 | 802 | **vencida** |
| `02_Poder_Legislativo/` | Eje Legislativo (20%) — calidad normativa (leyes vs simbólicos), eficacia de control (art. 101, informes JGM), costo del Congreso y cumplimiento de sesiones. | 4 | 739 | **vencida** |
| `07_Radar_Nombramientos/` | Radar del BORA (GitHub Actions, L–V 9:30 ART) — detecta ALTAS y BAJAS de jueces titulares leyendo el cuerpo de los decretos y las commitea a los CSV puente del repo. | 1 | 361 | **vencida** |
| `archivos_borrar\_retirados_20260819/` | _sin describir_ | 3 | 286 | — |
| `06_Historico/` | MIA Núcleo — serie larga comparable (anual 2003+, mensual 2020+) con las variables `nucleo: true` de variables.yaml; sus niveles NO coinciden con el índice pleno. | 2 | 190 | **vencida** |
| `./` | Raíz del repo — orquestadores de la corrida mensual (bat/sh), workflow de los radares del BORA, régimen de trabajo (README/AGENTS) y el mapa vivo del proyecto (MAPA.md/.mapa). | 1 | 121 | ok |
| `.github\workflows/` | _sin describir_ | 1 | 66 | — |

## Puntos de entrada

- `00_Comun\archivar_historico.py`
- `00_Comun\exportar_serie_historica.py`
- `00_Comun\generar_reporte_mensual.py`
- `00_Comun\graficar_mia.py`
- `00_Comun\icia_ensamblado.py`
- `00_Comun\validar.py`
- `01_Poder_Ejecutivo\scraper_01_dnu_leyes.py`
- `01_Poder_Ejecutivo\scraper_04_discrecionalidad.py`
- `01_Poder_Ejecutivo\scraper_11_transparencia_v2.py`
- `01_Poder_Ejecutivo\scraper_16_atn.py`

## Archivos centrales

Ordenados por cuantos otros archivos dependen de ellos. Tocar uno de arriba tiene mas radio de impacto.

| Archivo | LOC | Lo usan | Simbolos |
|---|---:|---:|---|
| `00_Comun\infoleg_source.py` | 91 | 3 | `build_session`, `_get_zip_bytes`, `_read_csv_resilient`, `_prepare_dates` |
| `00_Comun\icia_ensamblado.py` | 265 | 2 | `_cargar_config`, `cargar_nucleo`, `_latest`, `_col` |
| `scripts\indexar.py` | 714 | 0 | `cargar_gitignore`, `ignorado`, `leer`, `git` |
| `03_Poder_Judicial\padron_judicial.py` | 460 | 0 | `session`, `_read_csv_resilient`, `_snapshot_date`, `_es_jueces` |
| `03_Poder_Judicial\scraper_05_cobertura_judicial.py` | 422 | 0 | `session`, `_read_csv_resilient`, `_tasa`, `_snapshot_date` |
| `01_Poder_Ejecutivo\scraper_01_dnu_leyes.py` | 389 | 0 | `DNULeyesScraper`, `main` |
| `07_Radar_Nombramientos\radar_nombramientos.py` | 361 | 0 | `normalizar`, `es_candidata`, `_fecha_de_url`, `get_con_reintentos` |
| `00_Comun\generar_reporte_mensual.py` | 336 | 0 | `fmt`, `signo`, `mes_label`, `graficos` |
| `05_Banco_Central\radar_bcra.py` | 284 | 0 | `normaliza`, `get_con_reintentos`, `_fecha_de_url`, `obtener_lista_bora` |
| `01_Poder_Ejecutivo\scraper_16_atn.py` | 283 | 0 | `session`, `_to_num`, `atn_anual`, `atn_mensual_share` |
| `02_Poder_Legislativo\scraper_02_calidad_normativa.py` | 241 | 0 | `_usar_almacen_del_sistema`, `session`, `count_presentados`, `Cache` |
| `03_Poder_Judicial\scraper_06_resolucion_csjn.py` | 221 | 0 | `csjn_miembros`, `session`, `_num`, `parse_anuario` |

## Flujo interno

- `01_Poder_Ejecutivo/` → `00_Comun/` (2)
- `06_Historico/` → `00_Comun/` (2)
- `02_Poder_Legislativo/` → `00_Comun/` (1)

## Se tocan juntos

Segun el historial de git. Si vas a cambiar uno, mira el otro.

- `output/_alertas_validacion.md` + `output/mia_reporte.md` (4 commits)
- `00_Comun/BITACORA.md` + `output/_alertas_validacion.md` (3 commits)
- `00_Comun/BITACORA.md` + `05_Banco_Central/BITACORA.md` (3 commits)
- `AGENTS.md` + `correr_mensual.sh` (3 commits)
- `AGENTS.md` + `output/_alertas_validacion.md` (3 commits)
- `correr_mensual.sh` + `output/_alertas_validacion.md` (3 commits)
- `03_Poder_Judicial/BITACORA.md` + `output/itr_reporte.md` (3 commits)
- `07_Radar_Nombramientos/LEEME.md` + `07_Radar_Nombramientos/radar_nombramientos.py` (3 commits)

## Fuentes externas

- `datos.jus.gob.ar` — `00_Comun\infoleg_source.py`, `03_Poder_Judicial\padron_judicial.py`, `03_Poder_Judicial\scraper_05_cobertura_judicial.py`
- `boletinoficial.gob.ar` — `05_Banco_Central\radar_bcra.py`, `07_Radar_Nombramientos\radar_nombramientos.py`, `output\bajas_jueces.csv`
- `dgsiaf-repo.mecon.gob.ar` — `01_Poder_Ejecutivo\scraper_16_atn.py`, `02_Poder_Legislativo\scraper_12_costo_legislativo.py`, `04_Prensa_Institucional\scraper_08_pauta.py`
- `bcra.gob.ar` — `05_Banco_Central\diagnostico_panhis.py`, `05_Banco_Central\scraper_18_bcra_balance.py`, `archivos_borrar\_retirados_20260819\05_Banco_Central_scraper_18_bcra_financiamiento.py`
- `hcdn.gob.ar` — `02_Poder_Legislativo\scraper_02_calidad_normativa.py`, `02_Poder_Legislativo\scraper_14_sesiones.py`
- `monitoreo.fopea.org` — `04_Prensa_Institucional\scraper_13_prensa_causas.py`, `04_Prensa_Institucional\scraper_22_acceso_prensa.py`
- `opc.gob.ar` — `01_Poder_Ejecutivo\scraper_04_discrecionalidad.py`
- `descarga.aaip.gob.ar` — `01_Poder_Ejecutivo\scraper_11_transparencia_v2.py`
- `senado.gob.ar` — `02_Poder_Legislativo\scraper_03_eficacia_control.py`
- `csjn.gov.ar` — `03_Poder_Judicial\scraper_06_resolucion_csjn.py`
- `mpf.gob.ar` — `03_Poder_Judicial\scraper_10_integridad.py`
- `argentina.gob.ar` — `03_Poder_Judicial\scraper_10_integridad.py`

## Configuracion requerida

- `MIA_RADAR_CSV_URL` — `03_Poder_Judicial\padron_judicial.py`, `03_Poder_Judicial\scraper_05_cobertura_judicial.py`

## Frescura

- Bitacoras vencidas: `00_Comun/`, `01_Poder_Ejecutivo/`, `02_Poder_Legislativo/`, `03_Poder_Judicial/`, `04_Prensa_Institucional/`, `05_Banco_Central/`, `06_Historico/`, `07_Radar_Nombramientos/`, `scripts/`
- Carpetas sin bitacora: `archivos_borrar\_retirados_20260819/`
