"""
MIA — Exportador de la serie histórica larga (2020 →)
=====================================================
Arma un Excel único con TODA la historia disponible del Monitor, para consulta y difusión:

  Hoja "MIA Nucleo mensual"  -> serie comparable de fondo, 2020-01 en adelante (MIA Núcleo + 5 ejes).
  Hoja "MIA Nucleo anual"    -> misma serie en frecuencia anual (si existe).
  Hoja "MIA pleno mensual"   -> índice pleno de 18 variables + 5 ejes (publicado desde 2024-01),
                                con la marca provisional/cerrado del histórico maestro.
  Hoja "Variables"           -> las 18 variables desagregadas por mes (desde 2024-01).
  Hoja "Notas"               -> qué es cada serie y por qué los niveles no coinciden.

Por qué dos series: el MIA pleno usa 18 variables y arranca en 2024-01 (con colchón 2023 para el
suavizado de 12 meses); hacia atrás no todas las fuentes existen. El MIA Núcleo aplica el mismo
método al subconjunto de variables con dato consistente desde 2020, así que es comparable en el
largo plazo pero sus niveles NO coinciden con los del índice pleno.

Salida: Documentos/MIA — Serie histórica 2020-<último año>.xlsx
Uso:    py 00_Comun/exportar_serie_historica.py
"""
from __future__ import annotations
import logging, sys
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "output"
DOCS = BASE / "Documentos"
EJES = ["sub_Ejecutivo", "sub_Legislativo", "sub_Judicial", "sub_Prensa", "sub_Banco Central"]
NOM = {"sub_Ejecutivo": "Ejecutivo", "sub_Legislativo": "Legislativo", "sub_Judicial": "Judicial",
       "sub_Prensa": "Prensa", "sub_Banco Central": "Banco Central"}

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("hist2020")


def _nucleo_col(df):
    for c in ("MIA_nucleo", "ITR_nucleo"):
        if c in df.columns: return c
    return None


def main() -> int:
    hojas: dict[str, pd.DataFrame] = {}

    # 1) Núcleo mensual (2020 →)
    fnm = OUT / "mia_nucleo_mensual.csv"
    if fnm.exists():
        n = pd.read_csv(fnm)
        col = _nucleo_col(n)
        if col:
            d = n[["periodo", col] + [c for c in EJES if c in n.columns]].copy()
            d = d.rename(columns={col: "MIA Núcleo", **{k: NOM[k] for k in EJES if k in d.columns}})
            d[d.columns[1:]] = d[d.columns[1:]].round(2)
            hojas["MIA Nucleo mensual"] = d
            log.info("Núcleo mensual: %s → %s (%d meses)", d["periodo"].iloc[0], d["periodo"].iloc[-1], len(d))
    # 2) Núcleo anual
    fna = OUT / "mia_nucleo_anual.csv"
    if fna.exists():
        a = pd.read_csv(fna)
        col = _nucleo_col(a)
        if col:
            d = a[["anio", col] + [c for c in EJES if c in a.columns]].copy()
            d = d.rename(columns={col: "MIA Núcleo", **{k: NOM[k] for k in EJES if k in d.columns}})
            d[d.columns[1:]] = d[d.columns[1:]].round(2)
            hojas["MIA Nucleo anual"] = d

    # 3) MIA pleno mensual (desde 2024-01) + estado
    fh = OUT / "mia_historico.csv"
    src = fh if fh.exists() else (OUT / "mia_mensual.csv")
    if src.exists():
        m = pd.read_csv(src, dtype={"periodo": str})
        base_cols = ["periodo", "MIA"] + [c for c in EJES if c in m.columns] + \
                    [c for c in ("cobertura_vars", "estado", "actualizado") if c in m.columns]
        d = m[base_cols].copy().rename(columns={k: NOM[k] for k in EJES if k in m.columns})
        for c in d.columns:
            if c not in ("periodo", "estado", "actualizado", "cobertura_vars"):
                d[c] = pd.to_numeric(d[c], errors="coerce").round(2)
        hojas["MIA pleno mensual"] = d
        log.info("MIA pleno: %s → %s (%d meses)", d["periodo"].iloc[0], d["periodo"].iloc[-1], len(d))

        # 4) Variables desagregadas
        no_var = set(["periodo", "MIA", "cobertura_vars", "estado", "actualizado"] + EJES)
        varc = [c for c in m.columns if c not in no_var]
        if varc:
            dv = m[["periodo"] + varc].copy()
            for c in varc: dv[c] = pd.to_numeric(dv[c], errors="coerce").round(2)
            hojas["Variables"] = dv

    if not hojas:
        log.error("No hay series para exportar."); return 1

    # 5) Notas
    hojas["Notas"] = pd.DataFrame({
        "Serie": ["MIA Núcleo (mensual/anual)", "MIA pleno (mensual)", "Variables", "Escala", "Estados"],
        "Descripción": [
            "Serie comparable de largo plazo desde 2020: mismo método aplicado al subconjunto de variables "
            "con dato consistente. Sirve para comparar gestiones; sus niveles NO coinciden con el índice pleno.",
            "Índice pleno de 18 variables en 5 ejes (Ejecutivo 30%, Legislativo 20%, Judicial 20%, Prensa 15%, "
            "Banco Central 15%). Publicado desde enero de 2024 (calculado con colchón desde 2023).",
            "Las 18 variables que componen el índice pleno, ya normalizadas (0-100) por anclaje al ideal.",
            "0 a 100, anclado a un ideal liberal de república (0 = peor referencia; 100 = ideal). "
            "Suavizado con media móvil de 12 meses. Determinístico y auditable: sin IA en el valor.",
            "'cerrado' = mes congelado (no se reescribe); 'provisional' = mes en curso, puede cambiar.",
        ]})

    DOCS.mkdir(exist_ok=True)
    ultimo = hojas.get("MIA pleno mensual", hojas.get("MIA Nucleo mensual"))
    anio_fin = str(ultimo["periodo"].iloc[-1])[:4] if "periodo" in ultimo.columns else ""
    out_xlsx = DOCS / f"MIA — Serie histórica 2020-{anio_fin}.xlsx"
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as xw:
        for nombre, d in hojas.items():
            d.to_excel(xw, sheet_name=nombre[:31], index=False)
            ws = xw.sheets[nombre[:31]]
            ws.freeze_panes = "B2"
            for col in ws.columns:
                ancho = max((len(str(c.value)) for c in col if c.value is not None), default=10)
                ws.column_dimensions[col[0].column_letter].width = min(48, max(11, ancho + 2))
    log.info("Excel histórico: %s", out_xlsx.name)
    print(f"\nOK — {out_xlsx}")
    for k, v in hojas.items():
        print(f"   hoja «{k}»: {len(v)} filas x {len(v.columns)} col")
    return 0


if __name__ == "__main__":
    sys.exit(main())
