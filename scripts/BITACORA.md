# scripts/

<!-- huella: a2555ed2414b -->

Resumen: Herramientas del mapa vivo del repo (mapa-de-proyectos): indexador que genera MAPA.md/.mapa y hook pre-commit opcional.

## Buscar acá si

- reindexar el proyecto o sellar una bitácora → `indexar.py` (`python3 scripts/indexar.py .` / `--sellar <carpeta>` / `--estructura`)
- consultar el índice sin abrir archivos → `.mapa/buscar.py` (copiado automáticamente por el indexador)
- automatizar el reindexado en cada commit → `hook-pre-commit` (copiar a `.git/hooks/pre-commit`)

## Qué hay acá

- `indexar.py` — indexa el repo, ensambla MAPA.md, diagnostica estructura y sella bitácoras. Solo stdlib (Python 3.9+), sin red. Incluye el fix del co-cambio en repos sin historial (Counter).
- `buscar.py` — consulta de mapa.json (símbolos, archivos, carpetas). Se copia solo a `.mapa/` al indexar.
- `hook-pre-commit` — reindexa antes de cada commit sin bloquear; en Windows usa el launcher `py` si no hay `python3`.

## Trampas

- `MAPA.md` y `.mapa/mapa.json` son GENERADOS: no editarlos a mano, se pisan al reindexar.
- Sellar una bitácora sin haber actualizado su texto convierte el aviso de "vencida" en una afirmación falsa de frescura.

## Estado

- **Funciona:** indexado, sellado, diagnóstico y búsqueda, probados sobre este repo (2026-08-19).

## Proximo paso

Instalar el hook en las máquinas del equipo (`cp scripts/hook-pre-commit .git/hooks/pre-commit`).
