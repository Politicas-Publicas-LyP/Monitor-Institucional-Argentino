"""
MIA — Módulo 11: Transparencia v2 — Tasa de respuesta a pedidos de AIP
======================================================================
Mide, para CADA MES, el desempeño del Estado respondiendo pedidos de acceso a la
información pública (Ley 27.275): de los expedientes que se CERRARON en el mes
(resueltos o vencidos), qué proporción fue efectivamente respondida (`tasa_respuesta`)
y qué proporción se respondió dentro del plazo legal (`tasa_en_plazo`). Signo: más
respuestas, idealmente en plazo = mejor (menor asimetría de información).

FECHADO POR MES DE RESOLUCIÓN (decisión 2026-07-29)
---------------------------------------------------
La tasa se fecha por el mes en que el expediente se CERRÓ (`fecha_ultimo_pase` de los
expedientes terminales), NO por el mes de INICIO del pedido. Motivo: queremos "la tasa
del mes" — cuántos pedidos se cumplieron o no en ese mes — disponible de inmediato, en
vez de esperar 1-2 meses a que "madure" el cohorte por fecha de inicio. Los expedientes
todavía abiertos (estado "En plazo" / "En prórroga") no se cuentan hasta que se cierran;
entrarán en el mes en que se resuelvan o venzan. Así no hace falta un gate de madurez.

Fuente: microdato AAIP, una fila por solicitud (descarga.aaip.gob.ar/dataset/sip.csv).
Columnas usadas:
  - estado: Resuelto (respondido) | Vencido (venció sin respuesta) | En plazo / En prórroga (abierto).
  - fecha_ultimo_pase: fecha del último movimiento = fecha de cierre para los terminales.
  - plazo: días hábiles que tomó el trámite (para marcar "en plazo" ≤ 15 días hábiles).

Uso:
    py scraper_11_transparencia_v2.py --desde 2023-01 --hasta 2026-07
    py scraper_11_transparencia_v2.py --diagnostico            # vuelca columnas/estados (sin recorte)
Requisitos: pip install pandas requests
"""
from __future__ import annotations

import argparse
import io
import logging
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL = "https://descarga.aaip.gob.ar/dataset/sip.csv"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36",
           "Accept": "*/*", "Accept-Language": "es-AR,es;q=0.9"}
PLAZO_LEGAL = 15   # días hábiles (prorrogable a 30)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("transparencia_v2")


def session() -> requests.Session:
    s = requests.Session()
    r = Retry(total=4, backoff_factor=2.0, status_forcelist=(429, 500, 502, 503, 504),
              allowed_methods=frozenset(["GET"]))
    s.mount("https://", HTTPAdapter(max_retries=r))
    s.headers.update(HEADERS)
    return s


def load() -> pd.DataFrame:
    s = session()
    resp = s.get(URL, timeout=180)
    resp.raise_for_status()
    blob = resp.content
    for enc in ("utf-8", "latin-1"):
        for sep in (",", ";"):
            try:
                df = pd.read_csv(io.BytesIO(blob), sep=sep, encoding=enc, dtype=str,
                                 low_memory=False, on_bad_lines="skip")
                if df.shape[1] > 5:
                    log.info("CSV parseado enc=%s sep='%s' -> %s filas, %s cols", enc, sep, len(df), df.shape[1])
                    return df
            except Exception:  # noqa: BLE001
                continue
    raise RuntimeError("No se pudo parsear sip.csv")


def _parse_fechas(s: pd.Series) -> pd.Series:
    """Parseo robusto: ISO primero; si casi todo queda NaT, reintenta dayfirst."""
    d = pd.to_datetime(s, errors="coerce", format="ISO8601")
    if d.notna().mean() < 0.5:
        d = pd.to_datetime(s, errors="coerce", dayfirst=True)
    return d


def agregar(df: pd.DataFrame, desde: str, hasta: str) -> pd.DataFrame:
    """Serie mensual fechada por MES DE RESOLUCIÓN (fecha_ultimo_pase de los terminales).
    Devuelve: periodo, n_concluido, n_resuelto, n_vencido, n_en_plazo, tasa_respuesta, tasa_en_plazo."""
    est = df["estado"].astype(str).str.strip().str.lower()
    df = df.copy()
    df["_resuelto"] = est.eq("resuelto")
    df["_vencido"] = est.eq("vencido")
    plazo = pd.to_numeric(df.get("plazo"), errors="coerce")
    df["_en_plazo"] = df["_resuelto"] & (plazo <= PLAZO_LEGAL)     # respondido dentro del término legal
    df["_cierre"] = _parse_fechas(df.get("fecha_ultimo_pase"))

    # Solo expedientes TERMINALES (ya cerrados) y con fecha de cierre válida.
    term = (df["_resuelto"] | df["_vencido"]) & df["_cierre"].notna()
    d = df.loc[term].copy()
    d["periodo"] = d["_cierre"].dt.to_period("M")

    g = d.groupby("periodo").agg(
        n_concluido=("_resuelto", "size"),      # resueltos + vencidos cerrados en el mes
        n_resuelto=("_resuelto", "sum"),
        n_vencido=("_vencido", "sum"),
        n_en_plazo=("_en_plazo", "sum"),
    ).reset_index()
    g["tasa_respuesta"] = (g["n_resuelto"] / g["n_concluido"]).round(4)   # respondidos / cerrados en el mes
    g["tasa_en_plazo"] = (g["n_en_plazo"] / g["n_concluido"]).round(4)    # respondidos en plazo / cerrados en el mes
    g = g[(g["periodo"] >= pd.Period(desde, "M")) & (g["periodo"] <= pd.Period(hasta, "M"))]
    g["periodo"] = g["periodo"].astype(str)
    return g.reset_index(drop=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="MIA Módulo 11 — Transparencia v2 (tasa de respuesta AIP, por mes de resolución)")
    ap.add_argument("--desde", default="2023-01")
    ap.add_argument("--hasta", default="2026-07")
    ap.add_argument("--diagnostico", action="store_true", help="vuelca columnas y valores de 'estado' (sin recorte)")
    args = ap.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)
    try:
        df = load()
    except Exception as e:  # noqa: BLE001
        log.error("Fallo al descargar/parsear (¿bloqueo de IP? correr desde IP argentina): %s", e)
        return 1

    if args.diagnostico:
        print("\n=== DIAGNÓSTICO ===")
        print("Columnas:", list(df.columns))
        print("\n--- estado ---"); print(df["estado"].value_counts(dropna=False).head(25).to_string())
        f = _parse_fechas(df.get("fecha_ultimo_pase"))
        print(f"\n--- fecha_ultimo_pase: min={f.min()} max={f.max()} NaT={int(f.isna().sum())}")

    g = agregar(df, args.desde, args.hasta)

    print("\n=== SERIE MENSUAL (por mes de RESOLUCIÓN) ===")
    print(g.tail(18).to_string(index=False))
    print("\nNota: cada mes cuenta los expedientes CERRADOS en él (resueltos o vencidos). "
          "Los pedidos aún abiertos entran cuando se resuelven o vencen. Sin gate de madurez.")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = OUTPUT_DIR / f"transparencia_v2_mensual_{stamp}.csv"
    g.to_csv(out_csv, index=False, encoding="utf-8")
    log.info("CSV guardado: %s", out_csv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
