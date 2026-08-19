# 0009 — Respeto de la Carta Orgánica como test de cumplimiento (satura en 100)

- **Fecha:** 2026-08-18
- **Estado:** vigente
- **Alcance:** este proyecto (scraper_21, variable Respeto Carta Orgánica)

## Contexto

La variable usa `carta_organica_exceso` (exceso sobre el tope del art. 20) y está en
100 hace 25+ meses porque no hay exceso. Se auditó si "no se mueve" era un bug o si
convenía cambiarla a una métrica que varíe.

## Decision

Se deja como test de cumplimiento: 100 significa que la ley se respeta; su valor está
en alertar si alguna vez se viola. La magnitud del financiamiento ya la penaliza la
variable Financiamiento al Tesoro (módulo 18): no se mide dos veces lo mismo.

## Alternativas descartadas

- **Usar carta_organica_ratio (margen usado del tope)** — sí varía (0,113–0,125) pero
  castigaría usar un margen LEGAL, contradiciendo el anclaje principista: dentro de la
  ley no hay falta republicana que medir.

## Consecuencias

Un eje BCRA menos "vivo" mes a mes; la variable es un seguro, no un termómetro. El
scraper debe seguir corriendo (el hueco jun/jul-2026 por caché vieja ya se corrigió
con la regla de frescura) para que la detección de una violación sea inmediata.

## Como saber si fue un error

Si el tope se viola y la variable tarda más de una corrida en reflejarlo, o si los
lectores del reporte piden sistemáticamente "algo que se mueva" en ese eje.
