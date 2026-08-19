# Bitácora — Prensa Institucional

<!-- huella: b6f5b8d65b0e -->

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-08-19_

Resumen: Eje Prensa (15%) — escrutinio (conferencias vs cadenas), pauta oficial, causas judiciales contra periodistas (FOPEA), medios estatales y acceso de la prensa.

## Buscar acá si

- conferencias de prensa vs cadenas nacionales (Casa Rosada) → `scraper_07_escrutinio.py`
- pauta publicitaria oficial como % del gasto → `scraper_08_pauta.py` (DGSIAF anual)
- causas judiciales contra periodistas (categoría FOPEA) → `scraper_13_prensa_causas.py` (caché por id inmutable)
- RTA / Télam / medios estatales, share del gasto → `scraper_20_medios_oficiales.py` (caché solo años cerrados)
- sala de prensa, acreditaciones, restricciones de acceso → `scraper_22_acceso_prensa.py` (tabla `ACREDITACIONES` mantenida a mano + FOPEA; modo arrastre 3m)

## Escrutinio abierto  (`scraper_07_escrutinio.py`)
- **Estado:** OK.
- **Fuente:** —
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Pauta publicitaria  (`scraper_08_pauta.py`)
- **Estado:** OK. Caché output/_cache_pauta_anual_*.
- **Fuente:** Jefatura de Gabinete
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Causas contra periodistas  (`scraper_13_prensa_causas.py`)
- **Estado:** OK. Categoría oficial FOPEA.
- **Fuente:** FOPEA
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Medios estatales  (`scraper_20_medios_oficiales.py`)
- **Estado:** OK.
- **Fuente:** —
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Acceso de la prensa  (`scraper_22_acceso_prensa.py`)
- **Estado:** OK. Arrastre asimétrico 3 meses para eventos puntuales (cierre/reapertura sala Casa Rosada).
- **Fuente:** FOPEA + tabla de acreditaciones
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Registro de cambios
- 2026-08-19 — `scraper_22`: retirado el cartel «PLACEHOLDER / no publicar» y el warning de cada
  corrida — los tramos del cierre (abr-2026) y la reapertura (may-2026) de la sala de prensa ya
  están datados y en producción. La tabla sigue siendo mantenida a mano (human-in-the-loop).
- 2026-06-25 — Bitácora creada.
