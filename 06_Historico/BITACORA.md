# Bitácora — Núcleo histórico

<!-- huella: e7fa9d9efcb5 -->

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-08-19_

Resumen: MIA Núcleo — serie larga comparable (anual 2003+, mensual 2020+) con las variables `nucleo: true` de variables.yaml; sus niveles NO coinciden con el índice pleno.

## Buscar acá si

- la serie histórica larga o la comparación entre gestiones → `mia_nucleo_mensual.py` (2020+) / `mia_nucleo_historico.py` (anual 2003+)
- qué variables entran al núcleo, o sus anclas/componentes → `00_Comun/variables.yaml` (`nucleo:` y `nucleo_comp:`; acá NO hay listas propias desde 2026-08-19)
- correr toda la historia (scrapers --desde 2003 + ensamble) → `correr_nucleo_historico.bat`
- por qué el núcleo y el pleno dan niveles distintos → docstring de `00_Comun/exportar_serie_historica.py` (hoja Notas)

## Núcleo anual (2003+)  (`mia_nucleo_historico.py`)
- **Estado:** OK.
- **Fuente:** —
- **Última actualización:** 2026-06-25
- **Pendientes:** ATN y Judicial históricos para llegar a Macri (parqueado).

## Núcleo mensual (2020+)  (`mia_nucleo_mensual.py`)
- **Estado:** OK.
- **Fuente:** —
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Corrida histórica  (`correr_nucleo_historico.bat`)
- **Estado:** OK. Requiere IP AR; sirve de test de cobertura de fuentes.
- **Fuente:** —
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Registro de cambios
- 2026-08-19 — **Fuente única real:** los dos ensambladores del núcleo ahora leen
  `variables.yaml` vía `cargar_nucleo()` (icia_ensamblado) en vez de listas `NUCLEO`
  hardcodeadas (anclas triplicadas, riesgo de drift). Las dos diferencias deliberadas con el
  pleno quedaron declaradas en el YAML como `nucleo_comp` (ATN usa el share anual; Cobertura
  Judicial usa titular/subrogancia). Verificado: `mia_nucleo_mensual.csv` y `mia_nucleo_anual.csv`
  idénticos byte a byte antes/después.
- 2026-06-25 — Bitácora creada.
