# 0004 — Inmutabilidad de los meses cerrados del histórico

- **Fecha:** 2026-07-29 (+ opción --reabrir el 2026-08-18)
- **Estado:** vigente
- **Alcance:** este proyecto (archivar_historico.py, atn_obs_mensual.csv)

## Contexto

Recalcular la serie completa en cada corrida hace que valores YA PUBLICADOS cambien
silenciosamente (fuentes que corrigen hacia atrás, cachés refrescadas). Un índice
público no puede reescribir su pasado sin dejar rastro.

## Decision

`archivar_historico.py` hace UPSERT sobre el maestro: un mes cuyo calendario terminó
queda CONGELADO ("cerrado") y no se reescribe; el mes en curso es "provisional".
Reabrir un mes es decisión humana explícita (`--reabrir AAAA-MM`) y queda registrada
en la columna `actualizado`. Mismo principio en el ATN mensual (atn_obs_mensual.csv).

## Alternativas descartadas

- **Recalcular todo siempre** — valores publicados cambiarían sin aviso (pasó: el
  recálculo de julio-2026 daba 55,4921 vs 55,4911 congelado; no se reabre por debajo
  de la precisión de publicación).
- **Versionar cada corrida completa** — trazable pero inusable para difusión: no habría
  UN valor oficial por mes.

## Consecuencias

Una fuente rezagada (balance BCRA, cierres AAIP) exige reapertura deliberada para
impactar un mes cerrado. Es el costo aceptado de que el titular publicado sea estable.

## Como saber si fue un error

Si las reaperturas se vuelven rutina mensual (fuentes sistemáticamente rezagadas),
el cierre está mal calendarizado: mover el día de cierre, no aflojar la inmutabilidad.
