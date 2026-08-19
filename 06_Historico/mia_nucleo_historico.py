"""
MIA — NÚCLEO HISTÓRICO (anual, 2003+)
=====================================
Versión histórica y ANUAL del MIA para mostrar la evolución entre gobiernos. Usa SOLO
las variables con serie larga y consistente, balanceadas entre los 5 ejes, y aplica la
MISMA escala anclada al ideal que el MIA completo. Etiquetar como subconjunto histórico,
separado del MIA mensual (16 variables, desde 2023).

Lee los CSV de output/ (los mismos scrapers, corridos con --desde 2003-01), los lleva a
frecuencia ANUAL (promedio del año) y ensambla. Reporta, por año, cuántos ejes y variables
están cubiertos: el núcleo "balanceado" empieza el año en que hay >=1 variable por eje.

Variables EXCLUIDAS del núcleo (series cortas): Transparencia AAIP (2017+), Causas FOPEA,
Escrutinio, Acceso de la prensa (FOPEA solo 2023+, rompería la comparabilidad larga).
Cobertura judicial entra desde 2017 (snapshots). INCLUIDA: Respeto Carta Orgánica (BCRA),
con historia larga (balance BCRA 1990+ y recaudación 1997+).

Uso: py mia_nucleo_historico.py --desde 2003 --hasta 2026
Requisitos: pip install pandas
"""
from __future__ import annotations
import argparse, glob, sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_Comun"))
from icia_ensamblado import cargar_nucleo, MACRO  # noqa: E402

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
EPS = 1e-9

# FUENTE ÚNICA: las variables del núcleo salen de variables.yaml (nucleo: true;
# con nucleo_comp donde la serie larga difiere del pleno). Antes esta lista vivía
# hardcodeada acá, duplicando anclas y pesos (riesgo de drift): 2026-08-19.
NUCLEO = cargar_nucleo()


def _latest(p):
    f = sorted(glob.glob(str(OUTPUT_DIR / f"{p}_*.csv")))
    return f[-1] if f else None


def _annual(archivo, col, years):
    """Serie anual (promedio del año) de una columna mensual."""
    f = _latest(archivo)
    if not f: return None
    df = pd.read_csv(f)
    if "periodo" not in df.columns or col not in df.columns: return None
    df["anio"] = df["periodo"].astype(str).str[:4].astype(int)
    s = df.groupby("anio")[col].apply(lambda x: pd.to_numeric(x, errors="coerce").mean())
    return s.reindex(years)


def _annual_derived(name, years):
    if name == "leyes_por_sesion":
        ley = _latest("calidad_normativa_mensual"); ses = _latest("sesiones_mensual")
        if not ley or not ses: return None
        dl = pd.read_csv(ley); ds = pd.read_csv(ses)
        dl["anio"] = dl["periodo"].astype(str).str[:4].astype(int)
        ds["anio"] = ds["periodo"].astype(str).str[:4].astype(int)
        leyes = dl.groupby("anio")["n_leyes_sancionadas"].sum()
        real = ds.groupby("anio")["real_12m"].mean()  # sesiones realizadas (12m) prom.
        return (leyes / real).reindex(years)
    return None


def anchor(v, vb, vw):
    return None if v is None or pd.isna(v) else min(max((v - vw) / (vb - vw + (EPS if vb == vw else 0)), 0), 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", type=int, default=2003)
    ap.add_argument("--hasta", type=int, default=2026)
    a = ap.parse_args()
    years = list(range(a.desde, a.hasta + 1))

    var_year = {}  # var -> {year: score 0-1}
    for v in NUCLEO:
        comps = []
        for arch, col, vb, vw, w in v["comp"]:
            s = _annual_derived(col, years) if arch == "__derived__" else _annual(arch, col, years)
            if s is None: continue
            comps.append((s, vb, vw, w))
        if not comps: 
            var_year[v["var"]] = {y: None for y in years}; continue
        scores = {}
        for y in years:
            num = den = 0.0; ok = False
            for s, vb, vw, w in comps:
                sc = anchor(s.get(y), vb, vw)
                if sc is not None: num += sc * w; den += w; ok = True
            scores[y] = (num / den) if ok and den > 0 else None
        var_year[v["var"]] = scores

    cats = {v["var"]: v["cat"] for v in NUCLEO}
    pesos = {v["var"]: v["peso"] for v in NUCLEO}
    rows = []
    for y in years:
        sub = {}
        for c in MACRO:
            vs = [v for v in NUCLEO if v["cat"] == c]
            num = den = 0.0
            for v in vs:
                sc = var_year[v["var"]][y]
                if sc is not None: num += sc * pesos[v["var"]]; den += pesos[v["var"]]
            sub[c] = (num / den * 100) if den > 0 else None
        cats_ok = [c for c in MACRO if sub[c] is not None]
        if cats_ok:
            num = sum(MACRO[c] * sub[c] for c in cats_ok); den = sum(MACRO[c] for c in cats_ok)
            mia = num / den
        else:
            mia = None
        nvar = sum(1 for v in NUCLEO if var_year[v["var"]][y] is not None)
        rows.append({"anio": y, "MIA_nucleo": None if mia is None else round(mia, 1),
                     **{f"sub_{c}": (None if sub[c] is None else round(sub[c], 1)) for c in MACRO},
                     "ejes_cubiertos": len(cats_ok), "n_variables": nvar})
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_DIR / "mia_nucleo_anual.csv", index=False, encoding="utf-8")
    print(out.to_string(index=False))
    print("\nNúcleo balanceado (5 ejes) desde el primer año con ejes_cubiertos=5.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
