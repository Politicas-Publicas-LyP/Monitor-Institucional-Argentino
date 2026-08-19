# 0003 — Regla de frescura: fuente primero, caché como fallback

- **Fecha:** 2026-08-18
- **Estado:** vigente
- **Alcance:** este proyecto (los 19 scrapers)

## Contexto

Auditoría del 2026-08-18: cuatro scrapers tenían el antipatrón "caché primero"
(balance BCRA, recaudación, medios, congreso). Síntoma: variables planas durante
meses leyendo copias locales viejas aunque la fuente ya publicaba datos nuevos.

## Decision

Un scraper SIEMPRE consulta la fuente antes de usar una copia local. Snapshots se
descargan y refrescan en cada corrida (`--offline` para forzar la copia); cachés por
año solo para años CERRADOS (`anio < año actual`); cachés por mes nunca persisten el
mes en curso; cachés por ítem inmutable (id de decreto/caso) OK si el listado se baja
fresco. Documentada como no negociable en AGENTS.md.

## Alternativas descartadas

- **TTL por caché** — arbitrario: un TTL corto rompe la reproducibilidad offline y uno
  largo reintroduce el congelamiento; la semántica correcta es "cerrado = cacheable".
- **Borrar todas las cachés en cada corrida** — pierde reproducibilidad offline y
  reabre el costo de re-clasificar ítems inmutables (fetch de miles de decretos).

## Consecuencias

Corridas algo más lentas (siempre se descarga lo vivo). El impacto de los 4 bugs en el
valor publicado fue verificado NULO (±0,001), pero el patrón queda prohibido.

## Como saber si fue un error

Nunca debería serlo; la señal inversa es la que vale: si una variable queda plana
varios meses, revisar la caché ANTES de concluir que no hubo novedades.
