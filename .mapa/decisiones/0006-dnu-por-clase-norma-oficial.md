# 0006 — DNU = marca oficial `clase_norma` de InfoLEG, no detección por texto

- **Fecha:** 2026-06-01 (validada por inspección; registrada como ADR el 2026-08-19)
- **Estado:** vigente
- **Alcance:** este proyecto (scraper_01, variable DNU vs Leyes)

## Contexto

El dataset InfoLEG no parecía marcar los DNU y se construyó detección por texto
(art. 99 inc. 3 CN) abriendo la norma.htm de cada decreto.

## Decision

La fuente de verdad es `tipo_norma=='Decreto' AND clase_norma=='DNU'` (tag oficial).
La detección por texto queda solo como validación cruzada opcional (--detect-dnu).

## Alternativas descartadas

- **Detección por texto como fuente** — matchea CITAS a DNU en los considerandos de
  decretos comunes (~40 falsos positivos en 2023-25, verificados uno a uno con
  --inspect: casi todos "modificada por el DNU 70/23"), no autodeclaraciones.
- **Detección por título** — el título del enlace no trae el dato (mismo hallazgo que
  obligó a los radares a leer el cuerpo).

## Consecuencias

Dependencia de que InfoLEG mantenga bien el tag `clase_norma`. La validación cruzada
periódica (--detect-dnu fetch) es el control.

## Como saber si fue un error

Si la validación cruzada muestra DNU con marca FUERTE en el texto (autodeclaración
art. 99 inc. 3) que InfoLEG no tagueó, el tag oficial dejó de ser confiable.
