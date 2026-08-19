# 0001 — Anclar el índice a un ideal absoluto, no al pasado

- **Fecha:** 2026-06-25 (decisión de diseño; registrada como ADR el 2026-08-19)
- **Estado:** vigente
- **Alcance:** este proyecto (MIA pleno y Núcleo)

## Contexto

Un índice institucional puede normalizarse contra la historia propia (percentiles,
z-scores) o contra un estándar externo. La normalización relativa hace que el valor
de un mes cambie cuando se agrega historia, y convierte "mejor que ayer" en "bien".

## Decision

Cada componente define dos anclas principistas en variables.yaml: `mejor` → 100
(óptimo republicano alcanzable) y `peor` → 0 (colapso institucional), con
interpolación lineal y recorte. El MIA mide distancia al ideal, no posición relativa.

## Alternativas descartadas

- **Normalización por percentiles históricos** — el valor publicado de un mes cerrado
  cambiaría retroactivamente al crecer la serie; incompatible con la inmutabilidad.
- **Base 100 en un mes de referencia** — convierte la elección del mes base en una
  decisión política y no dice nada del nivel institucional absoluto.

## Consecuencias

Se gana comparabilidad en el tiempo y lectura directa ("cuánto falta para el ideal").
Se acepta que las anclas son juicio experto: cambiarlas es decisión humana registrada
(editar variables.yaml), nunca un ajuste automático.

## Como saber si fue un error

Si una variable satura (0 o 100) durante más de ~24 meses sin que el hecho
institucional lo justifique, las anclas están mal calibradas y hay que revisarlas.
