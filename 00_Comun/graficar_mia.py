"""
MIA — Gráfico desagregado de los 5 ejes (componente estándar de los informes)
=============================================================================
Genera el gráfico de líneas con los 5 sub-índices (Ejecutivo, Legislativo, Judicial,
Prensa, Banco Central) + la línea del MIA, a partir de cualquier salida del ensamblador.
Sirve para el MIA mensual (mia_mensual.csv, col 'MIA', eje x = periodo) y para el núcleo
histórico anual (mia_nucleo_anual.csv, col 'MIA_nucleo', eje x = anio).

Uso:
    py graficar_mia.py                                  # mensual (output/mia_mensual.csv)
    py graficar_mia.py --csv ../output/mia_nucleo_anual.csv --mia-col MIA_nucleo \
        --salida ../Documentos/MIA_nucleo.png --titulo "MIA — Núcleo histórico"
Requisitos: pip install pandas matplotlib
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
EJES = [("sub_Ejecutivo", "Ejecutivo", "#C8102E"),
        ("sub_Legislativo", "Legislativo", "#1f77b4"),
        ("sub_Judicial", "Judicial", "#7f3f98"),
        ("sub_Prensa", "Prensa", "#2ca02c"),
        ("sub_Banco Central", "Banco Central", "#ff7f0e")]


def graficar(csv, mia_col="MIA", salida=None, titulo="Monitor Institucional Argentino (MIA)",
             desde=None, hasta=None):
    d = pd.read_csv(csv)
    if "periodo" in d.columns and desde:
        d = d[d["periodo"] >= desde]
    if "periodo" in d.columns and hasta:
        d = d[d["periodo"] <= hasta]
    d = d.reset_index(drop=True)
    if "anio" in d.columns:
        x = d["anio"].astype(int); xlab = None; rot = 0
    else:
        x = pd.PeriodIndex(d["periodo"], freq="M").to_timestamp(); xlab = None; rot = 0
    d = d[d[mia_col].notna()]
    x = x[d.index]
    fig, ax = plt.subplots(figsize=(10, 5.6))
    for col, lab, c in EJES:
        if col in d.columns:
            ax.plot(x, d[col], marker="o", ms=3, linewidth=1.8, label=lab, color=c)
    ax.plot(x, d[mia_col], marker="s", ms=4, linewidth=3.2, color="black", label="MIA", zorder=5)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Score 0-100 (distancia al ideal republicano)", fontsize=9)
    ax.set_title(titulo, fontsize=13, fontweight="bold", color="#C8102E")
    ax.grid(True, axis="y", linestyle=":", alpha=0.5)
    ax.legend(ncol=3, fontsize=8.5, loc="lower center", framealpha=0.9)
    for _sp in ("top", "right"):   # compatible con cualquier versión de matplotlib
        ax.spines[_sp].set_visible(False)
    fig.tight_layout()
    out = salida or str(OUTPUT_DIR / "mia_grafico.png")
    fig.savefig(out, dpi=160)
    print("Gráfico guardado:", out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(OUTPUT_DIR / "mia_mensual.csv"))
    ap.add_argument("--mia-col", default="MIA")
    ap.add_argument("--salida", default=None)
    ap.add_argument("--titulo", default="Monitor Institucional Argentino (MIA)")
    ap.add_argument("--desde", default=None); ap.add_argument("--hasta", default=None)
    a = ap.parse_args()
    graficar(a.csv, a.mia_col, a.salida, a.titulo, a.desde, a.hasta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
