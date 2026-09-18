# Bitácora — Núcleo histórico

<!-- huella: bc12a12545ed -->

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-09-18_

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

## Núcleo mensual (2015+)  (`mia_nucleo_mensual.py`)
- **Estado:** OK. **AMPLIADO 2026-09-18** de 2020-01 a 2015-01 (`--desde 2015-01 --hasta 2026-08`)
  para tener panorama mensual completo de Macri + Alberto Fernández + Milei. El script ya
  calculaba internamente con warmup desde 2003 (`idx=pd.period_range("2003-01", ...)`, sin
  cambios de código) y sólo recorta la salida a `--desde`; extenderlo fue una corrida, no un
  cambio de lógica. `ejes_cubiertos` baja a 4 antes de 2017 (Judicial no tiene dato ahí), igual
  que en el núcleo anual — comportamiento esperado, no un hueco nuevo.
- **Fuente:** —
- **Última actualización:** 2026-09-18
- **Pendientes:** si se quiere ir antes de 2015 (para tener también la 2ª gestión de CFK
  completa), es la misma corrida con `--desde` más atrás — ya no depende del fix del ATN
  (resuelto 2026-09-17/18), solo de que los scrapers históricos tengan cobertura para esos años.

## Corrida histórica  (`correr_nucleo_historico.bat`)
- **Estado:** OK. Requiere IP AR; sirve de test de cobertura de fuentes.
- **Fuente:** —
- **Última actualización:** 2026-06-25
- **Pendientes:** —

## Registro de cambios
- 2026-09-18 — Núcleo mensual ampliado a 2015-01 (ver sección arriba). También se corrió
  `00_Comun/exportar_serie_historica.py` con el CSV ampliado: el nombre del archivo de salida y
  las notas ahora toman el año de inicio del propio `mia_nucleo_mensual.csv` en vez de tener
  "2020" fijo en el código, para no repetir este mismo desajuste la próxima vez que se cambie el
  rango. Se borró `Documentos/MIA — Serie histórica 2020-2026.xlsx` (superseded por la de
  2015-2026, mismo contenido regenerado con más historia).
- 2026-08-19 — **Fuente única real:** los dos ensambladores del núcleo ahora leen
  `variables.yaml` vía `cargar_nucleo()` (icia_ensamblado) en vez de listas `NUCLEO`
  hardcodeadas (anclas triplicadas, riesgo de drift). Las dos diferencias deliberadas con el
  pleno quedaron declaradas en el YAML como `nucleo_comp` (ATN usa el share anual; Cobertura
  Judicial usa titular/subrogancia). Verificado: `mia_nucleo_mensual.csv` y `mia_nucleo_anual.csv`
  idénticos byte a byte antes/después.
- 2026-06-25 — Bitácora creada.
