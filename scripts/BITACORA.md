# scripts/

<!-- huella: 94875667b5c2 -->

Resumen: Herramientas del mapa vivo del repo (mapa-de-proyectos): indexador que genera MAPA.md/.mapa y hook pre-commit opcional.

## Buscar acá si

- reindexar el proyecto o sellar una bitácora → `indexar.py` (`python3 scripts/indexar.py .` / `--sellar <carpeta>` / `--estructura`)
- regenerar el mapa interactivo del modelo (grafo HTML) → `generar_mapa_modelo.py` (correrlo DESPUÉS de la corrida mensual: congela los valores del mes)
- corregir qué fuente alimenta a qué script, o el texto de una ficha del grafo → `mapa_modelo_topologia.py` (las cañerías; las variables salen de variables.yaml)
- cambiar el aspecto o la interacción del grafo → `mapa_modelo.plantilla.html`
- consultar el índice sin abrir archivos → `.mapa/buscar.py` (copiado automáticamente por el indexador)
- automatizar el reindexado en cada commit → `hook-pre-commit` (copiar a `.git/hooks/pre-commit`)

## Qué hay acá

- `indexar.py` — indexa el repo, ensambla MAPA.md, diagnostica estructura y sella bitácoras. Solo stdlib (Python 3.9+), sin red. Incluye el fix del co-cambio en repos sin historial (Counter).
- `buscar.py` — consulta de mapa.json (símbolos, archivos, carpetas). Se copia solo a `.mapa/` al indexar.
- `hook-pre-commit` — reindexa antes de cada commit sin bloquear; en Windows usa el launcher `py` si no hay `python3`.
- `generar_mapa_modelo.py` — arma `Documentos/MIA — Mapa del modelo.html`: grafo interactivo con las 115 piezas del sistema y sus 139 conexiones. Lee variables.yaml + output/ + la topología; no necesita red ni CDN.
- `mapa_modelo_topologia.py` — lo que un escáner no puede deducir: qué fuente oficial alimenta a cada script, qué produce, y qué es alerta en vez de valor publicado. Es el archivo a editar cuando cambia una cañería.
- `mapa_modelo.plantilla.html` — plantilla del grafo (CSS + simulación de fuerzas propia, sin dependencias). El generador le inyecta los datos en `/*__DATOS__*/`.

## Trampas

- `MAPA.md` y `.mapa/mapa.json` son GENERADOS: no editarlos a mano, se pisan al reindexar.
- El mapa del modelo (.html) también es generado, y **congela los valores del mes** en el que se corrió: si se publica un mes nuevo hay que regenerarlo o mostrará el anterior. El pie del archivo dice con qué fecha se armó.
- La paleta del grafo está validada con el validador de la skill `dataviz` (3 slots categóricos, CVD all-pairs en claro y oscuro). Si se agregan colores, hay que volver a validarla: ningún set de 5 tonos pasa, y por eso la identidad de eje se lee por agrupamiento y rótulo, no por color.
- Sellar una bitácora sin haber actualizado su texto convierte el aviso de "vencida" en una afirmación falsa de frescura.

## Estado

- **Funciona:** indexado, sellado, diagnóstico y búsqueda, probados sobre este repo (2026-08-19).
- **Funciona:** el mapa del modelo, verificado en Chromium (sin errores de consola, 0 solapamientos de marcas y de etiquetas, modo claro y oscuro, vista de tabla).

## Proximo paso

Instalar el hook en las máquinas del equipo (`cp scripts/hook-pre-commit .git/hooks/pre-commit`) y agregar
`python3 scripts/generar_mapa_modelo.py` al final de `correr_mensual.*` si se quiere el mapa siempre al día.

## Registro de cambios

- 2026-08-19 — Nuevo mapa interactivo del modelo (`generar_mapa_modelo.py` + topología + plantilla):
  grafo force-directed con fuentes, scripts, series, las 18 variables con sus anclas y su score del mes,
  los 5 ejes, el MIA, los radares, el padrón y los consumidores. Vistas predefinidas (cadena del valor
  publicado, Núcleo, satélites, fuera del pipeline), ficha por nodo, resaltado del camino completo,
  gemelo en tabla y modo oscuro.
