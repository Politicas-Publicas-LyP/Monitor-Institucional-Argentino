# Bitácora — Banco Central

<!-- huella: 95a43468538e -->

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-08-19_

Resumen: Eje Banco Central (15%) — financiamiento al Tesoro y letras intransferibles (balance BCRA), designación del Presidente (estado mantenido) y respeto de la Carta Orgánica; más el radar BORA de la Presidencia.

## Buscar acá si

- adelantos/base monetaria o letras/activo → `scraper_18_bcra_balance.py` (balbcrhis.xls, columnas POR POSICIÓN; descarga siempre, caché solo `--offline`)
- tope del art. 20 de la Carta Orgánica / recaudación → `scraper_21_carta_organica.py` (API Series de Tiempo primero; 100 = cumple, es un test de cumplimiento)
- con/sin acuerdo del Senado del Presidente del BCRA → `scraper_17_bcra_designacion.py` (tabla `CONFIG` mantenida a mano; pre-2019 CONFIRMAR)
- alerta de designación/renuncia/fin de mandato en el BORA → `radar_bcra.py` (solo-alerta, corre en Actions)
- explorar la estructura de panhis.xls (factores de la base) → `diagnostico_panhis.py` (FUERA del pipeline)

## Financiamiento al Tesoro  (`scraper_18_bcra_balance.py`)
- **Estado:** OK (corregido 2026-07-29). El CSV `bcra_financiamiento_mensual` lo genera
  **`scraper_18_bcra_balance.py`** (Adelantos/Base). El `scraper_18_bcra_financiamiento.py` es
  solo un script de descubrimiento (vuelca `panhis.xls`, no produce serie) → candidato a retirar
  del orquestador. BUG resuelto: el balance quedaba congelado (abril) porque el scraper solo
  descargaba si NO existía la caché `_balbcrhis.xls`; ahora descarga siempre y refresca la caché
  (usa la copia local solo con `--offline` o si la descarga falla).
- **Fuente:** BCRA — balance histórico `balbcrhis.xls`
- **Última actualización:** 2026-08-19
- **Pendientes:** — (el ex `scraper_18_bcra_financiamiento.py` ya se retiró del pipeline y se
  renombró `diagnostico_panhis.py`, 2026-08-19).

## Letras intransferibles  (`scraper_18_bcra_balance.py`)
- **Estado:** OK (corregido 2026-07-29). Misma fuente y mismo fix de caché que Financiamiento
  (las dos salen del balance); también estaba congelada en abril.
- **Fuente:** BCRA — balance histórico `balbcrhis.xls`
- **Última actualización:** 2026-07-29
- **Pendientes:** re-correr con IP AR para traer mayo/junio.

## Respeto de la Carta Orgánica (art. 20)  (`scraper_21_carta_organica.py`)
- **Estado:** OK. Recaudación vía API de Series de Tiempo. **Revisado 2026-08-18:** la variable usa
  `carta_organica_exceso` (exceso sobre el límite legal) y está en **100 hace 25 meses** porque no
  hay exceso. **DECISIÓN (2026-08-18): se deja como está** — es un *test de cumplimiento*: que marque
  100 significa que la ley se respeta, y su valor está en alertar si alguna vez se viola. Se evaluó y
  descartó cambiarla al `carta_organica_ratio` (margen usado del límite, que sí varía: 0,125 → 0,113).
- **Fuente:** BCRA + apis.datos.gob.ar/series (serie `172.3_TL_RECAION_M_0_0_17`)
- **Última actualización:** 2026-08-18
- **Pendientes:** — (hueco de datos jun/jul RESUELTO, ver registro de cambios). El mes en curso queda
  sin ratio hasta que el BCRA publique el balance de ese mes: es normal, no es falla.

## Designación del Presidente del BCRA  (`scraper_17_bcra_designacion.py`)
- **Estado:** OK. Es un ESTADO (`sin_suavizar`): vale 0 mientras el Presidente esté «en comisión»
  (sin acuerdo del Senado) y 1 con acuerdo. El ensamblador ahora lo PERSISTE por ffill, así que
  ya no se cae de la renormalización ni infla el eje en meses parciales (antes jun-2026 saltaba
  a 83,3 por esa caída; corregido vuelve a ~66,8).
- **Fuente:** BORA / decreto PEN + acuerdo del Senado
- **Última actualización:** 2026-06-26
- **Pendientes:** Tras una alerta confirmada del radar (radar_bcra.py), actualizar el estado.

## Radar de la Presidencia del BCRA  (`radar_bcra.py`)
- **Estado:** NUEVO y OK (test 7/7). Solo-alerta: escanea el BORA y avisa designación
  (distingue «en comisión» vs «con acuerdo del Senado»), renuncia y fin de mandato del
  Presidente del BCRA. Evita trampas (Director/Vicepresidente y el boilerplate «Presidente
  de la Nación»). Corre en el workflow diario junto al radar de jueces.
- **Fuente:** BORA (`/seccion/primera/AAAAMMDD`, decisión por el cuerpo del decreto).
- **Salida:** `output/bcra_presidencia_eventos.csv` (alerta, no toca el valor publicado).
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Registro de cambios
- 2026-08-19 — `scraper_18_bcra_financiamiento.py` → renombrado **`diagnostico_panhis.py`** y
  RETIRADO de `correr_mensual.bat`/`.sh`: era un script de descubrimiento (volcaba la estructura
  de panhis.xls) que no produce ninguna serie y su nombre colisionaba con
  `scraper_18_bcra_balance.py`, el que sí genera `bcra_financiamiento_mensual` y
  `bcra_letras_mensual`. Se conserva como herramienta de diagnóstico.
- 2026-08-18 — FIX (mismo patrón que el balance del BCRA): `scraper_21_carta_organica.py` priorizaba
  el snapshot local `_recaudacion.csv` y **sólo consultaba la API si el CSV no existía**, así que un
  snapshot viejo (17-jun, hasta 2026-05) dejaba la variable **sin dato desde 2026-06** aunque la API
  ya publicaba junio y julio. El guard existente sólo verificaba el INICIO de la serie, nunca el final.
  Ahora se consulta **siempre la API primero** y se refresca el snapshot; el CSV queda como fallback
  offline, con aviso si está desactualizado o si la serie no llega al final del rango.
  Recuperado: jun ratio 0,1035 y jul 0,1048, ambos con exceso 0,0 (cumplimiento verificado, ya no
  arrastre). El valor publicado no cambia (seguía en 100), pero la variable vuelve a poder DETECTAR
  una violación reciente, que es su función. Nota: `apis.datos.gob.ar` responde desde fuera de AR.
- 2026-08-18 — Auditoría del eje (¿por qué se mueve tan poco?): Financiamiento (84,7→87,1) y Letras
  (67,9→68,8) **sí varían** —se ven planos por el suavizado de 12m—; «Designación Pdte. BCRA» = 0 hace
  32 meses es **correcto y verificado** (Bausili designado *en comisión* por Decreto 19/2023, sin
  acuerdo del Senado; el radar no detectó eventos posteriores: la quietud es la noticia); «Respeto
  Carta Orgánica» satura en 100 por diseño (ver arriba). No hay error de cálculo en el eje.
- 2026-07-29 — FIX: `scraper_18_bcra_balance.py` descargaba el balance solo si no existía la caché
  `_balbcrhis.xls`; como el snapshot era del 8-jun (datos hasta abril), Financiamiento al Tesoro y
  Letras intransferibles quedaban congeladas en abril en cada corrida. Ahora descarga siempre y
  refresca la caché; `--offline` fuerza el uso de la copia local. Requiere re-correr con IP AR.
- 2026-06-25 — Bitácora creada.
- 2026-06-25 — Creado `radar_bcra.py` (alerta de designación/renuncia/fin de mandato del Presidente del BCRA) e integrado al workflow diario de Actions.
