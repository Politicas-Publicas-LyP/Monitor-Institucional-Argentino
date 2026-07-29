"""
MIA — Archivador del histórico maestro
======================================
Mantiene una serie histórica ACUMULADA y accesible del índice, actualizada en cada
corrida. Toma la salida fresca (output/mia_mensual.csv) y hace UPSERT sobre un maestro
persistente, con INMUTABILIDAD de los meses cerrados: una vez que un mes quedó cerrado
(su calendario ya terminó), su valor queda CONGELADO en el maestro y no se reescribe
aunque un recálculo futuro lo cambie. El mes en curso se guarda como PROVISIONAL y se
actualiza en cada corrida hasta que el mes termina; en la primera corrida del mes
siguiente se congela.

Salidas (persistentes, versionadas por git):
  - output/mia_historico.csv    -> maestro completo (índice + ejes + 18 variables + estado)
  - output/mia_historico.xlsx   -> Excel con 2 hojas: "Indice" y "Variables"
  - Documentos/MIA — Serie histórica.xlsx  -> copia compartible (misma info)

Regla de cierre: un período < mes calendario actual (hora Argentina) = "cerrado"
(congelado); el mes corriente = "provisional".

Uso:  py 00_Comun/archivar_historico.py
"""
from __future__ import annotations

import logging
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE / "output"
DOCS_DIR = BASE / "Documentos"
SRC = OUTPUT_DIR / "mia_mensual.csv"
MASTER_CSV = OUTPUT_DIR / "mia_historico.csv"
MASTER_XLSX = OUTPUT_DIR / "mia_historico.xlsx"
SHARE_XLSX = DOCS_DIR / "MIA — Serie histórica.xlsx"

INDICE_COLS = ["MIA", "sub_Ejecutivo", "sub_Legislativo", "sub_Judicial",
               "sub_Prensa", "sub_Banco Central", "cobertura_vars"]
META_COLS = ["estado", "actualizado"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("archivar")


def _mes_actual() -> pd.Period:
    ar = datetime.now(timezone.utc) - timedelta(hours=3)   # hora Argentina
    return pd.Period(ar.strftime("%Y-%m"), freq="M")


def actualizar(fresh: pd.DataFrame, master: pd.DataFrame | None,
               datacols: list[str], current: pd.Period, ts: str) -> pd.DataFrame:
    """UPSERT con congelamiento: los meses 'cerrado' del maestro no se tocan."""
    rows: dict[str, dict] = {}
    if master is not None:
        for _, r in master.iterrows():
            rows[str(r["periodo"])] = r.to_dict()
    congelados = 0
    for _, r in fresh.iterrows():
        per = str(r["periodo"])
        prev = rows.get(per)
        if prev is not None and str(prev.get("estado")) == "cerrado":
            congelados += 1
            continue  # inmutable: no reescribir
        estado = "cerrado" if pd.Period(per, "M") < current else "provisional"
        row = {"periodo": per}
        for c in datacols:
            row[c] = r.get(c)
        row["estado"] = estado
        row["actualizado"] = ts
        rows[per] = row
    out = pd.DataFrame([rows[k] for k in sorted(rows)])
    # ordenar columnas: periodo + datos + meta
    cols = ["periodo"] + [c for c in datacols if c in out.columns] + META_COLS
    out = out[[c for c in cols if c in out.columns]]
    log.info("meses en maestro: %d | congelados (no tocados): %d", len(out), congelados)
    return out


def main() -> int:
    if not SRC.exists():
        log.error("No existe %s. Corré el ensamblado primero.", SRC)
        return 1
    fresh = pd.read_csv(SRC)
    fresh["periodo"] = fresh["periodo"].astype(str)

    varcols = [c for c in fresh.columns if c not in (["periodo"] + INDICE_COLS)]
    datacols = INDICE_COLS + varcols   # índice + ejes + 18 variables
    current = _mes_actual()
    ts = (datetime.now(timezone.utc) - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")

    master = pd.read_csv(MASTER_CSV, dtype={"periodo": str}) if MASTER_CSV.exists() else None
    out = actualizar(fresh, master, datacols, current, ts)

    # CSV maestro (fuente de verdad, versionable)
    out.to_csv(MASTER_CSV, index=False, encoding="utf-8")

    # Excel con 2 hojas
    hoja_indice = ["periodo"] + INDICE_COLS + META_COLS
    hoja_vars = ["periodo"] + varcols + META_COLS
    with pd.ExcelWriter(MASTER_XLSX, engine="openpyxl") as xw:
        out[[c for c in hoja_indice if c in out.columns]].to_excel(xw, sheet_name="Indice", index=False)
        out[[c for c in hoja_vars if c in out.columns]].to_excel(xw, sheet_name="Variables", index=False)
    # copia compartible en Documentos
    try:
        DOCS_DIR.mkdir(exist_ok=True)
        shutil.copy(MASTER_XLSX, SHARE_XLSX)
    except Exception as e:  # noqa: BLE001
        log.warning("No se pudo copiar a Documentos (%s).", e)

    ult = out.tail(1).iloc[0]
    log.info("Maestro actualizado. Último: %s (MIA=%s, estado=%s)", ult["periodo"], ult.get("MIA"), ult["estado"])
    print("\n=== HISTÓRICO (cola) ===")
    print(out[["periodo", "MIA", "estado"]].tail(6).to_string(index=False))
    print(f"\nCSV : {MASTER_CSV}")
    print(f"XLSX: {MASTER_XLSX}")
    print(f"Copia: {SHARE_XLSX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
