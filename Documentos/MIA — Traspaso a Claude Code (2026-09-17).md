# MIA — Traspaso a Claude Code

_2026-09-17_

Este documento cierra la revisión pedida (ATN, corrida de agosto, limpieza, verificación de
que todo esté prendido, mejoras) y deja lo que falta listo para ejecutar desde la máquina con
IP argentina.

**Por qué queda por ejecutar y no ejecutado:** en esta sesión el entorno de shell está caído
(una actualización de Windows del 8-sep impide que el sandbox llegue a los archivos). Se pudo
leer, analizar y **editar código**, pero no correr un solo script. Todo lo que sigue marcado
como «correr» es para Claude Code o para la consola.

---

## 1. Lo que ya quedó corregido en el código

### 1.1 ATN — tres bugs, todos del mismo tipo

El patrón común: **un valor que no se pudo medir se estaba publicando como si fuera una
medición**. Es el error más peligroso en un índice, porque no se ve.

**Bug 1 — «sin dato» publicado como CERO.**
`scraper_16_atn.py` identifica el ATN buscando el texto «aportes del tesoro nacional» en las
columnas de descripción de los archivos de DGSIAF. En los ejercicios viejos la etiqueta es
distinta, así que no matcheaba **ninguna** fila y el scraper devolvía `share = 0,0`.

Con las anclas de `variables.yaml` (`mejor = 0,001`, `peor = 0,007`, donde *menos ATN es
mejor*), un 0 normaliza a **100 = federalismo perfecto**. Resultado: **2003-01 a 2016-12
enteros en 0,0 — 168 meses — inflando el eje Ejecutivo del MIA Núcleo en toda la serie larga.**

Ahora: 0 filas matcheadas sobre un devengado total > 0 devuelve **SIN DATO**, avisa por log y
sugiere correr `--diagnostico`.

**Bug 2 — el mes en curso quedaba congelado con su devengado PARCIAL.**
`output/atn_obs_mensual.csv` es el store inmutable de publicación: un mes cerrado no se
recalcula nunca más. El problema es que también persistía el **mes corriente**. Secuencia:

1. Corrida del 19-ago → agosto está a mitad de camino → se observa `2026-08 = 0,0`.
2. Llega septiembre → agosto ya está cerrado **y ya figura en el store** → la regla de
   inmutabilidad lo saltea.
3. **Agosto queda publicado para siempre en 0,0**, que es el valor de medio mes.

Ahora el mes en curso **nunca** entra al store: se usa sólo en memoria para el nowcast de la
serie y se observa recién en la primera corrida del mes siguiente, ya completo. Es el mismo
bug que ya habíamos corregido en la caché de `scraper_02_calidad_normativa.py`.

**Bug 3 — cachés envenenadas.**
Los ceros del bug 1 quedaban guardados en `_cache_atn_{año}.csv` y
`_cache_atn_mensual_{año}.csv` **como dato definitivo**, así que arreglar el patrón no
alcanzaba: la caché seguía sirviendo el cero. Ahora una caché anual con `atn_dev = 0`, o una
mensual con los 12 meses en 0, se descarta sola y se recalcula. No hay que borrar nada a mano.

**Además:** se amplió el patrón a «Aporte(s) [no reintegrables] del Tesoro [Nacional]» — la
redacción varía entre ejercicios — cuidando de **no** matchear la *fuente de financiamiento*
«Tesoro Nacional» (fuente 1.1), que es otra cosa y aparece en casi todas las filas.

**Purga aplicada a `output/atn_obs_mensual.csv`:** se borraron los 168 ceros artificiales de
2003-01..2016-12 y el parcial congelado de 2026-08.

> **Ojo con los ceros que SÍ son reales.** 2020-01, 2021-04, 2021-05, 2022-08, 2022-10,
> 2024-07, 2024-08, 2024-09, 2024-12, 2025-11, 2026-05 y 2026-06 están en 0 **de verdad**:
> son meses sin ATN de la era Milei. En esos años el patrón sí matchea filas en el ejercicio,
> simplemente el mes no tiene monto devengado. Se conservan y deben conservarse — son, de
> hecho, el hallazgo más interesante de la variable.

### 1.2 El repositorio ya estaba renombrado; lo que faltaba era la URL

`AGENTS.md` y `README.md` seguían con el placeholder `<REPO>` y la nota «renombrar el repo».
**El repo ya se llama `Politicas-Publicas-LyP/Monitor-Institucional-Argentino`** (verificado
contra la API de GitHub). Ambos archivos quedaron actualizados.

**Trampa importante que apareció en el camino:** GitHub redirige el slug viejo (`…-ITR-…`) en
la web, pero **`raw.githubusercontent.com` sobre el nombre viejo devuelve contenido
desactualizado**. Verificado hoy: el `bajas_jueces.csv` servido por el slug viejo llegaba sólo
al 26-jun y **le faltaban las bajas de julio** (decretos 569/2026, 570/2026 y 664/2026), que
sí están en la versión servida por el nombre nuevo.

Esto importa porque el puente del radar judicial se lee por HTTP:
`scraper_05_cobertura_judicial.py` y `padron_judicial.py` ahora traen el CSV con un **default
apuntando al slug nuevo**, y si `MIA_RADAR_CSV_URL` apunta al viejo lo **descartan con aviso**.

> **Acción para vos, una sola vez:** borrá la variable de entorno si la tenés seteada al slug
> viejo. En PowerShell:
> ```powershell
> [Environment]::SetEnvironmentVariable("MIA_RADAR_CSV_URL", $null, "User")
> ```
> Ya no hace falta: el default del código es correcto.

---

## 2. Verificación: qué está prendido

| Componente | Estado | Evidencia |
|---|---|---|
| Repo remoto | **OK** | `Monitor-Institucional-Argentino`, público, rama `main`, último push 2026-09-08 |
| Workflow de radares (Actions) | **OK** | `Radares BORA (jueces + Presidencia BCRA)`, estado `active`, **66 corridas**, la última **hoy 17-sep 17:11Z** con `success` |
| `bajas_jueces.csv` remoto | **OK** | 10 filas, incluye las 3 detecciones de julio-2026 |
| Puente radar → cobertura judicial | **Estaba leyendo del slug viejo** | corregido en código (ver 1.2) |
| Cierre mensual | **PENDIENTE** | `mia_historico.csv` termina en `2026-08, provisional, 2026-08-19`. **Agosto nunca se cerró** |
| ATN | **Corregido, sin re-correr** | requiere IP AR |

Sobre la fiabilidad del cron: 66 corridas desde el 24-jun son ~19 menos que los días
transcurridos. En la última quincena faltan el 12 y el 13 de septiembre (sábado y domingo).
Coincide con lo ya anotado en la bitácora judicial el 06-jul: **el cron de Actions se saltea
corridas**. No pierde eventos de forma permanente —el radar reescanea una ventana de días—
pero conviene tenerlo presente (ver mejora M3).

---

## 3. Corrida mensual de agosto — comandos

Desde la máquina con IP argentina, en la raíz del proyecto.

```bat
REM 0) Traer lo último (el radar commitea solo) y confirmar que no hay nada sin pushear
git pull

REM 1) Corrida completa hasta agosto CERRADO
correr_mensual.bat 2026-08
```

Antes de dar por buena la corrida, en el log del ATN verificá que **no** aparezca
`0 filas matchean la etiqueta ATN` para 2023-2026, y que agosto traiga un share propio.

```bat
REM 2) Reporte del mes + actualización del Excel histórico
py 00_Comun\generar_reporte_mensual.py --mes 2026-08
py 00_Comun\exportar_serie_historica.py

REM 3) Cerrar el mes (congela agosto en mia_historico.csv)
py 00_Comun\archivar_historico.py --cerrar 2026-08
```

**Si el ATN de agosto sale raro**, forzá la reobservación del mes puntual:

```bat
py 01_Poder_Ejecutivo\scraper_16_atn.py --desde 2023-01 --hasta 2026-08
```

Como 2026-08 ya no está en el store (lo purgamos), esta corrida lo observa por primera vez con
el mes completo. El valor que salga es el que queda publicado.

---

## 4. ATN: lo que falta y las dos opciones

### Sobre la API de Presupuesto Abierto

Revisé `https://www.presupuestoabierto.gob.ar/api/`. Dos cosas:

1. **Requiere token**, y el token se obtiene registrándose con nombre y correo. No me registré
   en tu nombre: es una decisión tuya y tus datos.
2. **Probablemente no haga falta.** La API y los archivos abiertos de DGSIAF que ya usa el
   scraper (`credito-anual-{año}.zip` / `credito-mensual-{año}.zip`) salen de la misma base.
   Y tengo evidencia de que los archivos viejos están completos y se parsean bien: las cachés
   de **pauta oficial** y **costo legislativo** para 2015 tienen valores sanos
   (`_cache_pauta_anual_2015.csv` → intensidad 0,002164; `_cache_costoleg_v2_2015.csv` → doce
   meses con share). O sea: el archivo 2015 baja, abre y se lee. **El único que no encuentra
   nada es el ATN, y es por la etiqueta.**

Conclusión: el «faltante» no es de fuente ni de acceso. Es que **identificamos el ATN por
texto y el texto cambió**. La API no resolvería eso por sí sola; habría que hacer el mismo
trabajo de identificación, con un token de por medio.

### Lo que falta hacer (un comando)

```bat
py 01_Poder_Ejecutivo\scraper_16_atn.py --diagnostico 2015
py 01_Poder_Ejecutivo\scraper_16_atn.py --diagnostico 2010
py 01_Poder_Ejecutivo\scraper_16_atn.py --diagnostico 2005
```

Vuelca, por año, todos los valores de descripción que mencionan
*tesoro / aporte / provincia / asistencia financiera / coparticipación* con su devengado
ordenado de mayor a menor. Ahí va a estar el ATN con su nombre de la época. **Pegame esa
salida y cierro el arreglo.**

### Y la mejora de fondo que propongo hacer después

Dejar de identificar el ATN por texto y pasar a identificarlo por **código de la estructura
programática** (jurisdicción / programa / actividad), que es un identificador estable y no
depende de cómo redactaron la etiqueta ese año. Es exactamente lo que hace que *pauta* y
*costo legislativo* sí funcionen en 2015 y el ATN no. El diagnóstico de arriba nos da los
códigos junto con las descripciones, así que sale del mismo paso.

---

## 5. Limpieza

### 5.1 Cachés huérfanas (ningún script las lee ni las escribe)

Sobrevivieron a versiones retiradas de los scrapers. Verificado por búsqueda en todo el
código: la única referencia viva es `_cache_costoleg_v2_{anio}.csv`.

| Patrón | Archivos | Estado |
|---|---|---|
| `output/_cache_disim_*.csv` | 4 | huérfano |
| `output/_cache_disim_v2_*.csv` | 4 | huérfano |
| `output/_cache_reasig_*.csv` | 4 | huérfano |
| `output/_cache_costoleg_2023..2026.csv` (sin `_v2_`) | 4 | huérfano — la versión viva es `_v2_` |

```powershell
# Revisar primero, borrar después
Get-ChildItem output\_cache_disim_*.csv, output\_cache_reasig_*.csv
Get-ChildItem output\_cache_costoleg_2*.csv | Where-Object { $_.Name -notlike "*_v2_*" }
```

**No tocar** `_cache_atn_*`, `_cache_pauta_*`, `_cache_medios_*` ni `_cache_costoleg_v2_*`:
están vivos. (Los de ATN con ceros ya se auto-descartan solos, ver 1.1.)

### 5.2 Salidas con timestamp acumuladas

`output/` guarda cada corrida con su sello (`atn_mensual_20260805_110001.csv`, etc.). El
ensamblador toma la más reciente por glob, así que las viejas son peso muerto — pero **son la
única traza de corridas anteriores**. Sugerencia: conservar la última de cada variable y mover
el resto a `archivos_borrar/corridas_hasta_202608/`, en vez de borrarlas.

### 5.3 `archivos_borrar/`

Contiene, entre otras cosas, `truncados_20260818/` (los CSV que quedaron cortados por el
`HASTA` mal pasado) y `_cache_congreso_backup.json`. Ya cumplieron su función de red de
seguridad: si la corrida de agosto sale bien, se pueden eliminar.

---

## 6. Mejoras propuestas

Ordenadas por relación entre lo que evitan y lo que cuestan.

**M1 — Un test que prohíba publicar un cero que no se midió. (alta / bajo)**
Es la generalización del bug del ATN. En `validar.py`, agregar un chequeo: para toda variable
cuya ancla sea de tipo «menos es mejor», un **0 exacto** debe venir acompañado de evidencia de
que la fuente se leyó y no arrojó filas. Hoy un 0 y un «no encontré nada» son indistinguibles
aguas abajo, y el segundo se publica como 100. Revisé pauta, medios y costo legislativo y
están sanos, pero nada impide que vuelva a pasar.

**M2 — Alerta de mes congelado en los stores inmutables. (alta / bajo)**
El bug 2 del ATN es estructural del patrón «store inmutable»: cualquier archivo que congele
meses cerrados puede congelar un parcial si se escribió durante el mes. Un chequeo en el QA
—«¿algún periodo del store fue observado antes de que ese periodo terminara?»— lo detecta.
Requiere guardar la fecha de observación junto al valor, que hoy no se guarda.

**M3 — Chequeo de «última fecha procesada» en el radar. (media / bajo)**
Ya anotado en la bitácora judicial el 06-jul y sigue pendiente. El cron de Actions se saltea
corridas (66 en ~85 días). Que el workflow escriba la última fecha del BORA efectivamente
escaneada y avise si quedó a más de N días permite distinguir «no hubo novedades» de «no
corrió», que hoy se ven igual.

**M4 — Marcar el mes en curso como parcial en la salida. (media / bajo)**
Ya pendiente en la bitácora del Ejecutivo para `scraper_04_discrecionalidad.py`. Una columna
`parcial = True` en las salidas del mes corriente evita leer un nowcast como dato cerrado.

**M5 — ATN por código de estructura programática. (media / medio)**
Ver sección 4. Requiere el diagnóstico primero.

**M6 — Sección 5 de la aplicación Templeton. (fuera del código)**
La «Lectura de Libertad y Progreso» nunca se redactó. Sigue pendiente del documento.

---

## Resumen para arrancar

1. Borrar `MIA_RADAR_CSV_URL` si apunta al slug viejo (§1.2).
2. `git pull` y correr agosto (§3).
3. Correr los tres `--diagnostico` del ATN y pasarme la salida (§4).
4. Limpiar las cachés huérfanas (§5.1).
