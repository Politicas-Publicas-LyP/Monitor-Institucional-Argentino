# 0005 — Vigía / OpenArg no son fuente del valor publicado

- **Fecha:** 2026-06 (verificación de primera mano; registrada como ADR el 2026-08-19)
- **Estado:** vigente
- **Alcance:** este proyecto

## Contexto

Se evaluó alimentar variables desde Vigía (feed normativo) y OpenArg (sandbox SQL)
para reducir la fragilidad del scraping propio (sobre todo HCDN).

## Decision

No se usan como fuente del valor. Los scrapers propios contra fuentes primarias
(InfoLEG, DGSIAF, BCRA, AAIP, FOPEA, BORA, CSJN, Senado) siguen siendo la vía.

## Alternativas descartadas

- **Vigía** — el deploy vivo no expone API JSON de datos y /feed y /search exigen
  login (verificado por inspección de red, jun-2026); parsear RSC detrás de login es
  frágil y zona gris de ToS.
- **OpenArg** — endpoints reales pero detrás de login de Google, sin API anónima
  (verificado jun-2026); además query/smart usa IA (viola el ADR 0002).

## Consecuencias

Se mantiene el costo de scrapers propios y sus mañas (IP argentina, TLS del Congreso).
A cambio, cero dependencia de plataformas de terceros sin contrato ni SLA.

## Como saber si fue un error

Si alguna publica una API JSON pública, estable y anónima con los campos
estructurales necesarios, reevaluar variable por variable (detalle en
`Documentos/MIA — Fuentes por variable (Vigia-OpenArg).md`).
