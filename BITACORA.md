# Bitácora — Raíz del proyecto

<!-- huella: 4edcbef52c13 -->

> **Bitácora de la raíz.** Registrar acá los cambios de orquestación y régimen de trabajo.
> Antes de editar, hacé *pull*; al terminar, *commit + push* (ver AGENTS.md).

_Última revisión: 2026-11-11_

Resumen: Raíz del repo — orquestadores de la corrida mensual (bat/sh), workflow de los radares del BORA, régimen de trabajo (README/AGENTS) y el mapa vivo del proyecto (MAPA.md/.mapa).

## Buscar acá si

- correr el mes, cerrar un mes puntual o el cron del server → `correr_mensual.bat` / `correr_mensual.sh` (+ `Documentos/MIA — Runbook de la corrida mensual.md`)
- el pipeline "falló" pero era solo QA con avisos → `correr_mensual.sh` (exit 2 de validar.py NO cuenta como fallo desde 2026-08-19)
- los radares diarios del BORA en la nube → `.github/workflows/radar_nombramientos.yml` (corre jueces + Presidencia BCRA y commitea los CSV puente)
- qué se versiona y qué no (cachés, logs, archivos_borrar) → `.gitignore`
- ubicar código sin releer el repo → `MAPA.md` y `python3 .mapa/buscar.py "<término>"`; reindexar: `python3 scripts/indexar.py .`
- ver cómo se conecta el modelo (qué alimenta cada variable, qué se cae si falla una fuente) → `Documentos/MIA — Mapa del modelo.html` (grafo interactivo; se regenera con `python3 scripts/generar_mapa_modelo.py`)

## Qué hay acá

- `correr_mensual.bat` / `.sh` — pipeline mensual completo (scrapers → padrón → ensamblado → QA → gráficos → histórico → reporte). Solo calcula: no commitea ni publica.
- `.github/workflows/radar_nombramientos.yml` — radares BORA en Actions (L–V 9:30 ART), con tests de regresión previos.
- `README.md` / `AGENTS.md` — visión general y guía de arquitectura/operación (leer AGENTS primero).
- `MAPA.md` + `.mapa/` + `scripts/indexar.py` — índice vivo del proyecto (generado; no editar MAPA.md a mano).

## Trampas

- El repo se sincroniza por OneDrive **y** por GitHub Desktop: pull antes de tocar, commit + push al cerrar; escribir archivos completos (OneDrive puede mostrar copias truncadas mientras sincroniza).
- `HASTA` mal pasado trunca la serie: los orquestadores validan el formato AAAA-MM, pero revisá el rango impreso al arranque.
- El workflow de Actions vive SOLO en la raíz; una copia en 07_Radar_Nombramientos no se ejecuta.
- **El slug VIEJO del repo sirve datos rancios.** GitHub redirige `…-ITR-…` → `Monitor-Institucional-Argentino` en la web, pero `raw.githubusercontent.com` sobre el nombre viejo devuelve una versión desactualizada (verificado 2026-09-17: le faltaban las bajas de julio). Cualquier URL raw debe usar el nombre NUEVO.
- Un dato que no se pudo medir **no** se publica como 0: con anclas donde «menos es mejor», el 0 normaliza a 100 y se lee como institucionalidad ideal. Ver el bug del ATN (2026-09-17, bitácora del Ejecutivo).

## Estado

- **Funciona:** corrida mensual completa (bat y sh), QA no bloqueante. Radares en Actions **verificados el 2026-09-17**: workflow `active`, 66 corridas, la última el 17-sep 17:11Z con `success`.
  **Agosto-2026 ya está cerrado** (MIA=54,80, `mia_historico.csv` estado=cerrado, corrido el
  2026-09-17/18 desde esta máquina con IP AR). El ATN quedó corregido y re-corrido para toda la
  serie 2003-2026 (ver `01_Poder_Ejecutivo/BITACORA.md`).
- **A medias:** —
- **Roto:** —

## Proximo paso

Pushear `main` desde GitHub Desktop (las credenciales de Git de esta máquina no tienen permiso de escritura) y, cuando HCDN
publique su nueva versión, repetir Calidad Normativa y revisar si el fallback de Datos Abiertos sigue vigente — ver
`02_Poder_Legislativo/BITACORA.md`.

## Registro de cambios

- 2026-11-11 — **Corrida mensual de septiembre y octubre 2026 (cierre)** desde esta máquina con IP AR
  (`& .\correr_mensual.bat 2026-10`; rango 2022-01..2026-10, publicado desde 2024-01). **MIA sep = 54,66 · oct = 55,47**
  (cobertura_vars=18; `mia_historico.csv`: 34 meses cerrados, agosto idéntico = 54,80). Reabiertos a propósito los 12
  meses de 2024 (colchón 2022: +1,6 pts en ene-24, ver ADR 0004) y sep/oct (recalculados tras reparar sesiones).
  Incidentes: sesiones (HCDN rediseñó su sitio, reparado) y Calidad Normativa sin dato en sep/oct por la caída de HCDN
  (no afecta el valor) — ver `02_Poder_Legislativo/BITACORA.md`. Radares: el workflow de Actions estuvo caído desde
  2026-10-22 (el BORA bloquea a los runners de GitHub): ahora leen por el proxy de Cloudflare (`00_Comun/bora_proxy.py`);
  hueco 28-sep..11-nov recuperado a mano (1 alta, 0 bajas, 0 eventos BCRA). Pendiente humano: lectura institucional,
  confirmar BCRA y acreditaciones de prensa, informe JGM >N°145 (Eficacia de Control, 196 días sin informe).

- 2026-09-18 — **Colchón de la corrida mensual ampliado de 1 a 2 años** (`DESDE=2022-01` en vez de
  `2023-01`, en `correr_mensual.bat`/`.sh`): un componente cuya media móvil de 12 meses no llegaba
  a completarse antes de la publicación (ene-2024) quedaba con `NaN` ya dentro de lo publicado.
  OJO: no resuelve todos los casos — `Discrecionalidad presup. → modif_12m` sigue en `NaN` de
  2024-01 a 2024-05 porque la OPC recién tiene página propia de modificaciones desde 2024 (`HTTP
  404` verificado para 2020-2023); ningún colchón trae un dato que la fuente no publicó. Validado
  re-corriendo agosto completo con el nuevo rango: `validar.py` sigue en estado=OK, MIA=54,81 (vs
  54,80 antes, diferencia de redondeo).
- 2026-09-17 — Renombre del repo remoto **cerrado**: el repositorio ya es
  `Politicas-Publicas-LyP/Monitor-Institucional-Argentino` (lo que faltaba era actualizar la URL,
  no renombrar). README y AGENTS apuntan al nombre nuevo. `scraper_05_cobertura_judicial.py` y
  `padron_judicial.py` ahora traen el puente del radar con un **default al slug nuevo** y
  **descartan** un `MIA_RADAR_CSV_URL` que apunte al viejo (servía el CSV sin las bajas de julio).
- 2026-09-17 — Tres bugs del ATN corregidos (sin-dato-como-cero, mes en curso congelado, cachés
  envenenadas). Detalle en `01_Poder_Ejecutivo/BITACORA.md`.

- 2026-08-19 — Bitácora de raíz creada (formato mapa-de-proyectos). `correr_mensual.*`: retirado el
  script de descubrimiento del BCRA (hoy `05_Banco_Central/diagnostico_panhis.py`); `.sh` distingue
  QA-con-avisos (exit 2 de validar.py, no bloquea) de fallo real. Workflow: tests de regresión de
  los radares antes de escanear. `.gitignore`: encabezado ITR→MIA, `_panhis.xls` y logs de corrida.
