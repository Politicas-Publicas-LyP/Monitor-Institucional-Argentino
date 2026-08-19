# Bitácora — Raíz del proyecto

<!-- huella: e14e89aa7262 -->

> **Bitácora de la raíz.** Registrar acá los cambios de orquestación y régimen de trabajo.
> Antes de editar, hacé *pull*; al terminar, *commit + push* (ver AGENTS.md).

_Última revisión: 2026-08-19_

Resumen: Raíz del repo — orquestadores de la corrida mensual (bat/sh), workflow de los radares del BORA, régimen de trabajo (README/AGENTS) y el mapa vivo del proyecto (MAPA.md/.mapa).

## Buscar acá si

- correr el mes, cerrar un mes puntual o el cron del server → `correr_mensual.bat` / `correr_mensual.sh` (+ `Documentos/MIA — Runbook de la corrida mensual.md`)
- el pipeline "falló" pero era solo QA con avisos → `correr_mensual.sh` (exit 2 de validar.py NO cuenta como fallo desde 2026-08-19)
- los radares diarios del BORA en la nube → `.github/workflows/radar_nombramientos.yml` (corre jueces + Presidencia BCRA y commitea los CSV puente)
- qué se versiona y qué no (cachés, logs, archivos_borrar) → `.gitignore`
- ubicar código sin releer el repo → `MAPA.md` y `python3 .mapa/buscar.py "<término>"`; reindexar: `python3 scripts/indexar.py .`

## Qué hay acá

- `correr_mensual.bat` / `.sh` — pipeline mensual completo (scrapers → padrón → ensamblado → QA → gráficos → histórico → reporte). Solo calcula: no commitea ni publica.
- `.github/workflows/radar_nombramientos.yml` — radares BORA en Actions (L–V 9:30 ART), con tests de regresión previos.
- `README.md` / `AGENTS.md` — visión general y guía de arquitectura/operación (leer AGENTS primero).
- `MAPA.md` + `.mapa/` + `scripts/indexar.py` — índice vivo del proyecto (generado; no editar MAPA.md a mano).

## Trampas

- El repo se sincroniza por OneDrive **y** por GitHub Desktop: pull antes de tocar, commit + push al cerrar; escribir archivos completos (OneDrive puede mostrar copias truncadas mientras sincroniza).
- `HASTA` mal pasado trunca la serie: los orquestadores validan el formato AAAA-MM, pero revisá el rango impreso al arranque.
- El workflow de Actions vive SOLO en la raíz; una copia en 07_Radar_Nombramientos no se ejecuta.

## Estado

- **Funciona:** corrida mensual completa (bat y sh), radares en Actions, QA no bloqueante.
- **A medias:** renombre del repo remoto (…-ITR-…) y de la carpeta raíz pendiente; actualizar la URL en README/AGENTS y `MIA_RADAR_CSV_URL` al hacerlo.
- **Roto:** —

## Proximo paso

Renombrar el repositorio de GitHub al nombre MIA y actualizar README/AGENTS + la variable de entorno `MIA_RADAR_CSV_URL` donde esté seteada.

## Registro de cambios

- 2026-08-19 — Bitácora de raíz creada (formato mapa-de-proyectos). `correr_mensual.*`: retirado el
  script de descubrimiento del BCRA (hoy `05_Banco_Central/diagnostico_panhis.py`); `.sh` distingue
  QA-con-avisos (exit 2 de validar.py, no bloquea) de fallo real. Workflow: tests de regresión de
  los radares antes de escanear. `.gitignore`: encabezado ITR→MIA, `_panhis.xls` y logs de corrida.
