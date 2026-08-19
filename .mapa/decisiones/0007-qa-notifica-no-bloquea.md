# 0007 — El QA notifica, no bloquea la publicación

- **Fecha:** 2026-06-25 (política de equipo; registrada como ADR el 2026-08-19)
- **Estado:** vigente
- **Alcance:** este proyecto (validar.py, correr_mensual.sh)

## Contexto

Muchas variables del MIA son estructurales (anuarios CSJN, datasets bienales):
"dato viejo" es su estado normal, no una falla. Un QA bloqueante frenaría cada mes
por avisos esperables.

## Decision

`validar.py` escribe `output/_alertas_validacion.md` y devuelve exit 2 si hay
hallazgos; la publicación sigue y una persona evalúa. Desde 2026-08-19,
`correr_mensual.sh` distingue ese exit 2 (QA con avisos) de un fallo real del
pipeline (exit 1), para que el cron no marque como rota una corrida sana.

## Alternativas descartadas

- **QA bloqueante** — falsos positivos estructurales frenarían la publicación mensual
  y el equipo terminaría salteando el validador (peor que no tenerlo).
- **Sin QA** — los 4 bugs de frescura de ago-2026 mostraron que las variables se
  congelan en silencio; el QA es la red que lo hace visible.

## Consecuencias

La responsabilidad final es humana: publicar con avisos es una decisión, no un
accidente. Los overrides de tolerancia por variable viven en contracts.yaml.

## Como saber si fue un error

Si un mes se publica con un dato realmente roto que el QA había marcado y nadie leyó,
el "notificar sin bloquear" necesita al menos un canal más ruidoso (mail/webhook).
