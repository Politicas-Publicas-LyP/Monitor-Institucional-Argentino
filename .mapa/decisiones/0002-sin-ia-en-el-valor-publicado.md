# 0002 — Sin IA en el valor publicado

- **Fecha:** 2026-06-25 (decisión fundacional; registrada como ADR el 2026-08-19)
- **Estado:** vigente
- **Alcance:** este proyecto (todas las variables y radares)

## Contexto

El MIA se presenta como determinístico y auditable ante donantes y prensa. Un juicio
de IA en el valor lo volvería irreproducible y discutible ("lo dijo un modelo").

## Decision

Todo valor publicado sale de conteos, SQL o campos estructurados reproducibles. La IA
queda para exploración, reparación de scrapers, QA/anomalías y la redacción de la
"Lectura de LyP". Los radares del BORA son detección POR REGLAS y solo alertan: lo que
entra al índice se confirma con reglas determinísticas o revisión humana (confianza
ALTA / columna `confirmado`).

## Alternativas descartadas

- **Clasificación por LLM de decretos/casos** — irreproducible entre corridas y
  versiones de modelo; indefendible metodológicamente.
- **NL2SQL (query/smart de OpenArg)** — usa un modelo por debajo; mismo problema.

## Consecuencias

Más trabajo manual (tablas mantenidas: designación BCRA, acreditaciones, informes JGM
extra) y detectores por regex que exigen tests de regresión (--test en ambos radares).
A cambio, cada número es auditable hasta la fuente.

## Como saber si fue un error

Si las tablas mantenidas a mano acumulan errores u olvidos que un clasificador
supervisado con revisión humana hubiese evitado, revisar el balance costo/beneficio.
