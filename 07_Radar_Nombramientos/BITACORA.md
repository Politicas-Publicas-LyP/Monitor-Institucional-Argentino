# Bitácora — Radar de Nombramientos (BORA)

<!-- huella: f13d624369b0 -->

> **Bitácora del eje.** Registrar acá cada cambio con su fecha. Es la fuente para saber el
> estado de cada variable sin leer el código. Mantener «Pendientes» al día. Antes de editar,
> hacé *pull*; al terminar, *commit + push* (ver AGENTS.md → régimen de trabajo).

_Última revisión: 2026-08-19_

Resumen: Radar del BORA (GitHub Actions vía proxy de Cloudflare, L–V 3 veces por día) — detecta ALTAS y BAJAS de jueces titulares leyendo el cuerpo de los decretos y las commitea a los CSV puente del repo.

## Buscar acá si

- el radar no detectó (o detectó mal) una designación o renuncia → `radar_nombramientos.py` (`detectar`/`detectar_baja`; probar con `--test`)
- recuperar un período pasado del BORA → `--desde/--hasta` (idempotente, dedup por URL)
- qué significa confianza ALTA/MEDIA/BAJA o la columna `confirmado` → `LEEME.md`
- el cron / el workflow de Actions (que corre también el radar BCRA) → `.github/workflows/radar_nombramientos.yml` (vive SOLO en la raíz)
- el radar falla con `ConnectTimeout` / `no se pudo leer el BORA` en Actions → el BORA bloquea runners de GitHub; se lee por el proxy → `00_Comun/bora_proxy.py` (`--test`), Variable `BORA_PROXY_URL`, Secret `BORA_PROXY_TOKEN`

## Radar de nombramientos — ALTAS y BAJAS  (`radar_nombramientos.py`)
- **Estado:** OK (test 8/8). Lee el BORA por fecha (/seccion/primera/AAAAMMDD), decide por el
  CUERPO del decreto. ALTAS: designaciones de jueces titulares (detectó las 46 del 25/06/2026).
  BAJAS: renuncia / cese / remoción / jubilación / límite de edad / fallecimiento de un juez
  (verificadas en el BORA: decretos 529, 530/2025, etc.). Salida en dos CSV puente.
- **Fuente:** BORA
- **Última actualización:** 2026-11-11
- **Pendientes:** verificar la 1ª corrida real por el proxy (workflow_dispatch) y mirar 2-3 días hábiles; pendiente M3 (alerta de "última fecha escaneada").

## Registro de cambios
- 2026-11-11 — El radar reconoce el nombre del sistema acusatorio: la regex de órganos incluye «Tribunal Federal de
  Juicio» / «Tribunal de Juicio» (antes dejaba `organo` vacío, p. ej. Decreto 1066/2026). `--test` 9/9 (caso nuevo).

- 2026-11-11 — Corrida manual #106 (tras el push) falló en «Correr radar»: los lectores 1-8 del proxy dieron 522 en la lista del BORA (racha mala del proxy; el radar BCRA, 4 s después, leyó bien). Fallar avisando funcionó y el workflow igual corrió el paso BCRA y la persistencia. Mejora: `bora_proxy.py` prueba los 16 lectores. Las corridas L-V de 09:30, 12:30 y 16:30 ART reintentan solas.
- 2026-11-11 — **Fallar avisando también con fichas ilegibles.** Primera corrida real por el proxy: leyó la lista
  (70 normas) pero una ficha candidata no conectó en ningún lector y el radar igual dijo «Sin novedades».
  Ahora `obtener_texto_norma` devuelve `None` si no pudo LEER la ficha; el radar lista las fichas sin leer, NO concluye
  «sin novedades» y sale con exit 1 (lo no detectado no se persiste: la corrida siguiente reintenta). El workflow corre el
  radar BCRA y persiste los CSV aunque el radar judicial falle (`if: !cancelled()`); el job queda en rojo igual.
  (La ficha de esa corrida —Decreto 1349/2026, hidroeléctricas— revisada a mano: no era relevante.)
- 2026-11-11 — **Radar caído desde 2026-10-22**: el BORA dejó de responder a los runners de GitHub
  (ConnectTimeout en los 4 reintentos; 14 corridas fallidas seguidas, último commit de radares 2026-09-28).
  Fix: `00_Comun/bora_proxy.py` (lectura por el Worker de Cloudflare `bora-proxy-sam`, rotando lectores, con
  lectura directa como último recurso), usado por ambos radares; workflow con 3 horarios diarios + `keepalive.yml`.
  Hueco recuperado a mano desde IP argentina (`--desde 2026-09-28 --hasta 2026-11-11`): 1 alta
  (Decreto 1343/2026, 2026-11-11), 0 bajas, 0 eventos BCRA. Se descartó un runner self-hosted (la PC no está prendida todos los días).
- 2026-08-19 — El workflow de Actions ahora corre PRIMERO los `--test` de ambos radares
  (8/8 y 7/7, sin red) como regresión: si una edición rompe la detección, el run falla antes
  de escanear el BORA.
- 2026-06-25 — Reescrito: lectura por fecha + detección sobre el cuerpo (arregla el bug del filtro por título).
- 2026-06-25 — Modo histórico por fecha (sin Vigía).
- 2026-06-25 — Integrado el detector de BAJAS (renuncias/ceses) → `bajas_jueces.csv`; el padrón lo lee para liberar cargos.
