# ITR — Runbook de la corrida mensual

Modelo operativo de la corrida mensual del Índice de Transparencia Republicana (ITR).
Es el plano para automatizarla en el server propio. La corrida **solo calcula el
índice**: es determinística y auditable, sin IA en el valor, y **no publica ni commitea
nada de forma automática** — el equipo revisa las alertas de QA y publica a mano.

_Última revisión: 2026-07-06_

## 1. Qué corre y dónde

Dos piezas independientes, con requisitos de red distintos:

- **Radares del BORA** (jueces altas/bajas + Presidencia BCRA). Ya corren solos en
  **GitHub Actions** (L–V 09:30 ART) y dejan sus CSV puente en el repo. El BORA es
  accesible desde el exterior, por eso viven en la nube. **No forman parte de esta
  corrida**: la corrida mensual los *lee* del repo.
- **Corrida mensual (dato duro → índice)**. Todo lo demás: scrapers de las 18 variables,
  padrón judicial, ensamblado, QA y gráficos. **Requiere IP argentina.**

### Requisito de entorno: IP argentina (no negociable)

`DGSIAF` (`dgsiaf-repo.mecon.gob.ar`), `BCRA` (`bcra.gob.ar`) y `datos.jus.gob.ar`
**bloquean IPs de datacenter/exterior**. Por eso la corrida mensual **no puede correr en
runners cloud del exterior** (GitHub Actions, VM en el extranjero): tiene que ejecutarse
en una máquina/servidor con **egress con IP argentina**. `apis.datos.gob.ar` (recaudación)
sí responde afuera, pero es la excepción.

> El único que sortea esto es el radar del BORA, porque el BORA no discrimina por IP.

## 2. El comando único

El orquestador corre TODO en orden: scrapers → padrón judicial → cobertura → ensamblado
→ QA → gráficos. Idempotente (cachés y `--desde/--hasta`).

| Objetivo | Windows | Linux / server |
|---|---|---|
| Mes en curso (provisional) | `correr_mensual.bat` | `./correr_mensual.sh` |
| **Cerrar un mes puntual** | `correr_mensual.bat 2026-06` | `./correr_mensual.sh 2026-06` |
| Cerrar el mes anterior (cron) | — | `CERRAR_ANTERIOR=1 ./correr_mensual.sh` |

Parámetros fijos del modelo (no cambian mes a mes):

- **DESDE = 2023-01** — colchón de 1 año para que el suavizado de 12m esté completo al
  inicio publicado. El tramo 2023 se calcula pero **no se publica**.
- **PUBLICAR = 2024-01** — inicio publicado (gestión Milei), ya suavizado.
- **HASTA** — el mes que se calcula. Sin argumento = mes en curso (sale **provisional**).
  Con `AAAA-MM` = cierra ese mes (titular definitivo).

### La corrida de junio 2026

```
# Windows (tu PC):
correr_mensual.bat 2026-06

# Linux (server):
./correr_mensual.sh 2026-06
```

Antes de correr, traer el repo al día (para tomar los CSV puente del radar más frescos):
`git pull`.

## 3. Salidas

- `output/itr_mensual.csv` — el índice (0–100) por mes y por eje, publicado desde 2024-01.
- `output/_alertas_validacion.md` — alertas de QA (frescura, faltantes, saltos). **Notifica,
  no bloquea.**
- Gráficos del índice (consolidado, 5 ejes y núcleo).
- `output/_corrida_mensual_AAAAMMDD_HHMMSS.log` — log completo de la corrida.

En Linux, el script devuelve **exit ≠ 0 si algún paso falló** (con la cuenta de fallos al
pie del log), para que el cron/monitoreo lo detecte. Principio: **fallar avisando**, nunca
dar "sin novedades" si una fuente no respondió.

## 4. Después de correr (revisión y publicación — manual)

1. Abrir `output/_alertas_validacion.md` y revisar alertas.
2. Verificar `cobertura_vars` (deben ser las 18 variables) en el log del ensamblado.
3. Si el mes está cerrado y las alertas están limpias, publicar el titular. La
   publicación es una decisión humana; la corrida no la hace sola.

## 5. Automatización en el server (cuando esté listo)

Meta: el server con IP AR cierra el mes anterior a principios de cada mes.

**Linux (cron).** Día 3, 06:00:

```
crontab -e
0 6 3 * *  CERRAR_ANTERIOR=1 /ruta/al/repo/correr_mensual.sh >> /var/log/itr.log 2>&1
```

**Linux (systemd timer).** Alternativa más observable: un `itr.service` (Type=oneshot que
ejecute el script con `CERRAR_ANTERIOR=1`) + un `itr.timer` con `OnCalendar=*-*-03 06:00:00`
y `Persistent=true` (recupera la corrida si el server estuvo apagado ese día).

**Windows (Task Scheduler).** Si el "server" es una PC Windows encendida: tarea mensual
(día 3) que ejecute `correr_mensual.bat` con el mes anterior. Para pasar el mes anterior
automático conviene un wrapper `.bat` de una línea que calcule `AAAA-MM` con PowerShell y
llame al orquestador.

### Checklist de puesta en marcha del server

- [ ] Egress con **IP argentina** verificado (probar que responden DGSIAF, BCRA y datos.jus).
- [ ] Python 3 + `pip install -r 00_Comun/requirements.txt`.
- [ ] Repo clonado y `git pull` en el arranque de cada corrida (para los CSV del radar).
- [ ] Variable `ITR_RADAR_CSV_URL` apuntando al `nombramientos_jueces.csv` del repo
      (la de bajas se deriva sola).
- [ ] Cron/timer cargado y con log redirigido.
- [ ] Alerta si el exit del script ≠ 0 (mail o webhook) — para no depender de mirar el log.

## 6. Qué NO hace la corrida (por diseño)

- No usa IA en el valor publicado (la IA queda para reparar scrapers, redactar el informe
  y el futuro radar de eventos).
- No commitea ni publica sola: el cierre lo confirma una persona tras leer el QA.
- No recalcula los radares del BORA: los lee del repo (los produce GitHub Actions).
