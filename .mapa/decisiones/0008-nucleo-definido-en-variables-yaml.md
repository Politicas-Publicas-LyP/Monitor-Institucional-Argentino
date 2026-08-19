# 0008 — El Núcleo se define en variables.yaml (nucleo / nucleo_comp)

- **Fecha:** 2026-08-19
- **Estado:** vigente
- **Alcance:** este proyecto (06_Historico, 00_Comun)

## Contexto

Los dos ensambladores del núcleo tenían listas NUCLEO hardcodeadas que triplicaban
anclas y pesos de variables.yaml. Coincidían en membresía, pero dos variables
diferían en componentes sin que el YAML lo declarara: drift silencioso asegurado.

## Decision

`icia_ensamblado.cargar_nucleo()` deriva el registro del núcleo desde variables.yaml:
entran las variables `nucleo: true`; si una define `nucleo_comp`, el núcleo usa esos
componentes en lugar de los del pleno. Las dos divergencias deliberadas quedaron
declaradas: ATN usa el share ANUAL (existe desde 2003) y Cobertura Judicial usa
titular/subrogancia (comparable desde 2017, sin el radar 2026+).

## Alternativas descartadas

- **Dejar las listas hardcodeadas** — tres copias de cada ancla; un cambio en el YAML
  no llegaba al núcleo y nadie lo notaría hasta comparar series.
- **Un YAML separado para el núcleo** — duplica las variables compartidas; la relación
  pleno/núcleo quedaría otra vez implícita.

## Consecuencias

Cambiar un ancla del núcleo es editar el YAML. Migración verificada byte a byte:
mia_nucleo_mensual.csv y mia_nucleo_anual.csv idénticos antes/después (2026-08-19).

## Como saber si fue un error

Si aparece una tercera vista del índice cuyas necesidades no entran en el patrón
comp/nucleo_comp, el esquema quedó chico y hay que generalizarlo (no parchearlo).
