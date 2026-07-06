#!/usr/bin/env bash
# ============================================================================
#  MIA - PIPELINE MENSUAL COMPLETO  (Linux / servidor)
# ----------------------------------------------------------------------------
#  Equivalente de correr_mensual.bat. Requiere EGRESS con IP ARGENTINA:
#  datos.jus, DGSIAF y BCRA bloquean IPs del exterior/datacenter. (Por eso el
#  server de la corrida mensual debe tener IP AR; ver AGENTS.md y el runbook
#  Documentos/MIA — Runbook de la corrida mensual.md)
#
#  Los RADARES del BORA (jueces altas/bajas + Presidencia BCRA) corren en
#  GitHub Actions y dejan sus CSV puente en el repo; este pipeline los lee de
#  ahi (variable de entorno MIA_RADAR_CSV_URL).
#
#  QUE MES CALCULA (HASTA):
#    ./correr_mensual.sh                 -> HASTA = mes en curso (PROVISIONAL)
#    ./correr_mensual.sh 2026-06         -> cierra un mes puntual (YYYY-MM)
#    HASTA=2026-06 ./correr_mensual.sh   -> idem, por entorno
#    CERRAR_ANTERIOR=1 ./correr_mensual.sh  -> cierra el mes anterior (para el cron)
#
#  AUTOMATIZACION (server con IP AR). Cerrar el mes anterior el dia 3 de cada
#  mes, 06:00, y dejar el log:
#    crontab -e  ->
#    0 6 3 * *  CERRAR_ANTERIOR=1 /ruta/al/repo/correr_mensual.sh >> /var/log/mia.log 2>&1
#  Solo CALCULA el indice (sin commit ni publicacion automatica): el equipo
#  revisa las alertas de QA y publica. Devuelve exit!=0 si algun paso fallo.
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")"

DESDE="${DESDE:-2023-01}"        # colchon: 1 anio antes para suavizado 12m completo (no se publica)
PUBLICAR="${PUBLICAR:-2024-01}"  # inicio publicado = gestion Milei, ya suavizado
# HASTA: prioridad = arg posicional $1 > env HASTA > (CERRAR_ANTERIOR ? mes anterior) > mes en curso.
if [ "${1:-}" != "" ]; then
  HASTA="$1"
elif [ "${HASTA:-}" != "" ]; then
  HASTA="$HASTA"
elif [ "${CERRAR_ANTERIOR:-}" = "1" ]; then
  HASTA="$(date -d "$(date +%Y-%m-01) -1 day" +%Y-%m)"   # ultimo dia del mes pasado -> YYYY-MM
else
  HASTA="$(date +%Y-%m)"
fi
if ! echo "$HASTA" | grep -Eq '^[0-9]{4}-[0-9]{2}$'; then
  echo "ERROR: HASTA invalido ('$HASTA'). Formato esperado YYYY-MM." >&2; exit 3
fi
PY="${PY:-python3}"
mkdir -p output
LOG="output/_corrida_mensual_$(date +%Y%m%d_%H%M%S).log"
echo "MIA - corrida mensual | rango: $DESDE .. $HASTA | log: $LOG" | tee "$LOG"

FALLOS=0
run() {
  echo -e "\n### $*" | tee -a "$LOG"
  if ! "$@" >>"$LOG" 2>&1; then
    echo "  (FALLO: $* — sigue)" | tee -a "$LOG"
    FALLOS=$((FALLOS+1))
  fi
}

echo "== EJECUTIVO ==" | tee -a "$LOG"
run "$PY" 01_Poder_Ejecutivo/scraper_01_dnu_leyes.py        --desde "$DESDE" --hasta "$HASTA"
run "$PY" 01_Poder_Ejecutivo/scraper_04_discrecionalidad.py --desde "$DESDE" --hasta "$HASTA"
run "$PY" 01_Poder_Ejecutivo/scraper_11_transparencia_v2.py --desde "$DESDE" --hasta "$HASTA"
run "$PY" 01_Poder_Ejecutivo/scraper_16_atn.py              --desde "$DESDE" --hasta "$HASTA"

echo "== LEGISLATIVO ==" | tee -a "$LOG"
run "$PY" 02_Poder_Legislativo/scraper_02_calidad_normativa.py --desde "$DESDE" --hasta "$HASTA"
run "$PY" 02_Poder_Legislativo/scraper_03_eficacia_control.py  --desde "$DESDE" --hasta "$HASTA"
run "$PY" 02_Poder_Legislativo/scraper_12_costo_legislativo.py --desde "$DESDE" --hasta "$HASTA"
run "$PY" 02_Poder_Legislativo/scraper_14_sesiones.py          --desde "$DESDE" --hasta "$HASTA"

echo "== JUDICIAL ==" | tee -a "$LOG"
run "$PY" 03_Poder_Judicial/scraper_06_resolucion_csjn.py --desde "$DESDE" --hasta "$HASTA"
run "$PY" 03_Poder_Judicial/padron_judicial.py --construir     # base oficial de jueces
run "$PY" 03_Poder_Judicial/padron_judicial.py --actualizar    # altas/bajas del BORA (estimado)
run "$PY" 03_Poder_Judicial/scraper_05_cobertura_judicial.py --desde "$DESDE" --hasta "$HASTA"

echo "== PRENSA ==" | tee -a "$LOG"
run "$PY" 04_Prensa_Institucional/scraper_07_escrutinio.py       --desde "$DESDE" --hasta "$HASTA"
run "$PY" 04_Prensa_Institucional/scraper_08_pauta.py            --desde "$DESDE" --hasta "$HASTA"
run "$PY" 04_Prensa_Institucional/scraper_13_prensa_causas.py    --desde "$DESDE" --hasta "$HASTA"
run "$PY" 04_Prensa_Institucional/scraper_20_medios_oficiales.py --desde "$DESDE" --hasta "$HASTA"
run "$PY" 04_Prensa_Institucional/scraper_22_acceso_prensa.py    --desde "$DESDE" --hasta "$HASTA"

echo "== BANCO CENTRAL ==" | tee -a "$LOG"
run "$PY" 05_Banco_Central/scraper_18_bcra_financiamiento.py --desde "$DESDE" --hasta "$HASTA"
run "$PY" 05_Banco_Central/scraper_18_bcra_balance.py
run "$PY" 05_Banco_Central/scraper_21_carta_organica.py      --desde "$DESDE" --hasta "$HASTA"
run "$PY" 05_Banco_Central/scraper_17_bcra_designacion.py    --desde "$DESDE" --hasta "$HASTA"

echo "== ENSAMBLAR + QA + GRAFICOS ==" | tee -a "$LOG"
run "$PY" 00_Comun/icia_ensamblado.py --desde "$DESDE" --hasta "$HASTA" --publicar-desde "$PUBLICAR"
run "$PY" 00_Comun/validar.py
run "$PY" 00_Comun/graficar_mia.py

echo "LISTO. Indice: output/mia_mensual.csv | Alertas QA: output/_alertas_validacion.md" | tee -a "$LOG"
echo "(El mes en curso sale PROVISIONAL; para el titular cerrado, correr con el mes cerrado: ./correr_mensual.sh AAAA-MM)" | tee -a "$LOG"
if [ "$FALLOS" -gt 0 ]; then
  echo "ATENCION: $FALLOS paso(s) fallaron. Revisar el log: $LOG" | tee -a "$LOG"
  exit 1
fi
echo "OK: todos los pasos corrieron sin error." | tee -a "$LOG"
