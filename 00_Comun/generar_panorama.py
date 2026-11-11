"""
MIA — Panorama mensual (imagen-resumen)
=======================================
Una sola imagen con cómo va el Monitor: titular del mes, índice consolidado, los cinco ejes y
cada eje en el mes con su variación. Sale de la serie PUBLICADA (output/mia_historico.csv: meses
cerrados congelados + el mes en curso como provisional), con el mismo estilo y paleta que
graficar_mia.py y el logo de LyP. Determinístico: no usa IA y no toca el valor del índice.

Salida: Documentos/MIA — Panorama (<Mes> <Año>).png   (mismo patrón de nombre que el reporte mensual)

Uso:
    py 00_Comun/generar_panorama.py                 # último mes del histórico
    py 00_Comun/generar_panorama.py --mes 2026-09   # un mes puntual (la serie se corta ahí)
    py 00_Comun/generar_panorama.py --salida ruta.png

Si el mes está "provisional" (nowcast), el titular y el pie lo dicen y el último punto va hueco.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates
import matplotlib.pyplot as plt
import matplotlib.ticker
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.image import imread

BASE = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE / "output"
DOCS_DIR = BASE / "Documentos"
LOGO = BASE / "00_Comun" / "assets" / "logo_lyp.png"

RED, INK, GRAY = "#C8102E", "#2b2b2b", "#6b6b6b"
VERDE, ROJO_DELTA = "#1a7f37", "#b42318"
# (columna, nombre, color, peso). Colores = los de graficar_mia.py. Los pesos son los de los ejes
# (variables.yaml / nota metodológica): si cambian allá, cambiarlos acá.
EJES = [("sub_Ejecutivo", "Ejecutivo", "#C8102E", 0.30),
        ("sub_Legislativo", "Legislativo", "#1f77b4", 0.20),
        ("sub_Judicial", "Judicial", "#7f3f98", 0.20),
        ("sub_Prensa", "Prensa", "#2ca02c", 0.15),
        ("sub_Banco Central", "Banco Central", "#ff7f0e", 0.15)]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
AB = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("panorama")


def f1(v: float) -> str:
    return f"{v:.1f}".replace(".", ",")


def fs(v: float) -> str:
    return ("+" if v >= 0 else "−") + f"{abs(v):.1f}".replace(".", ",")


def _fmt_mes(v, _):
    d = matplotlib.dates.num2date(v)
    return f"{AB[d.month - 1]}-{d.strftime('%y')}"


def generar(mes: str | None = None, salida: str | None = None) -> Path | None:
    src = OUTPUT_DIR / "mia_historico.csv"
    if not src.exists():
        log.error("No existe %s: correr antes archivar_historico.py.", src)
        return None
    h = pd.read_csv(src, dtype={"periodo": str}).sort_values("periodo")
    if mes:
        if mes not in set(h["periodo"]):
            log.error("El mes %s no está en mia_historico.csv (rango: %s → %s).", mes, h["periodo"].min(), h["periodo"].max())
            return None
        h = h[h["periodo"] <= mes]
    h = h[h["MIA"].notna()].reset_index(drop=True)
    if len(h) < 2:
        log.error("Hacen falta al menos 2 meses para armar el panorama.")
        return None
    h["x"] = pd.PeriodIndex(h["periodo"], freq="M").to_timestamp()
    cur, prev = h.iloc[-1], h.iloc[-2]
    y, m = int(cur["periodo"][:4]), int(cur["periodo"][5:])
    pm = int(prev["periodo"][5:])
    provisional = str(cur.get("estado", "")) != "cerrado"
    ya = h[h["periodo"] == f"{y - 1}-{cur['periodo'][5:]}"]
    imin, imax = h["MIA"].idxmin(), h["MIA"].idxmax()

    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#444"})
    fig = plt.figure(figsize=(14, 9.2), dpi=150, facecolor="white")
    gs = GridSpec(3, 12, figure=fig, height_ratios=[0.9, 3.1, 2.2], hspace=0.42, wspace=0.9,
                  left=0.06, right=0.975, top=0.965, bottom=0.075)

    # ---------- encabezado ----------
    ax = fig.add_subplot(gs[0, :]); ax.axis("off")
    if LOGO.exists():
        lax = fig.add_axes([0.06, 0.865, 0.13, 0.09]); lax.imshow(imread(str(LOGO))); lax.axis("off")
    ax.text(0.215, 0.80, "Monitor Institucional Argentino", fontsize=23, fontweight="bold", color=INK, va="top")
    ax.text(0.215, 0.28, "Calidad republicana de 0 a 100 · dato duro oficial, sin IA en el valor", fontsize=11.5, color=GRAY, va="top")
    etiqueta_mes = f"{MESES[m - 1]} de {y}".capitalize() + (" · provisional" if provisional else "")
    ax.text(0.985, 1.08, etiqueta_mes, fontsize=11.5, color=GRAY, ha="right", va="top")
    ax.text(0.985, 0.84, f1(cur["MIA"]), fontsize=50, fontweight="bold", color=RED, ha="right", va="top")
    comp = f"{fs(cur['MIA'] - prev['MIA'])} vs {AB[pm - 1]}"
    if not ya.empty:
        comp += f"  ·  {fs(cur['MIA'] - ya.iloc[0]['MIA'])} vs {AB[m - 1]}-{str(y - 1)[2:]}"
    ax.text(0.985, 0.06, comp, fontsize=11.5, color=INK, ha="right", va="top")

    # ---------- consolidado ----------
    a1 = fig.add_subplot(gs[1, :7])
    a1.plot(h["x"], h["MIA"], color=RED, lw=3, marker="o", ms=3.5, zorder=3)
    a1.fill_between(h["x"], h["MIA"], h["MIA"].min() - 2, color=RED, alpha=0.07)
    a1.set_title("Índice consolidado", loc="left", fontsize=13, fontweight="bold", color=INK)
    a1.set_ylim(h["MIA"].min() - 2, h["MIA"].max() + 2)
    a1.set_ylabel("MIA (0–100)", color=GRAY, fontsize=10)
    a1.grid(axis="y", ls=":", alpha=.5)
    for i, dy, lab in ((imin, -1.25, "mínimo"), (imax, 1.0, "máximo")):
        dx = pd.Timedelta(days=70) if lab == "mínimo" else pd.Timedelta(days=0)
        a1.annotate(f"{lab} {f1(h['MIA'][i])}\n({AB[int(h['periodo'][i][5:]) - 1]}-{h['periodo'][i][2:4]})",
                    (h["x"][i], h["MIA"][i]), (h["x"][i] + dx, h["MIA"][i] + dy), ha="center", fontsize=9, color=GRAY,
                    arrowprops=dict(arrowstyle="-", color="#aaa", lw=.8))
    a1.scatter([h["x"].iloc[-1]], [cur["MIA"]], s=110, zorder=5, lw=1.8,
               facecolor="white" if provisional else RED, edgecolor=RED)

    # ---------- cinco ejes ----------
    a2 = fig.add_subplot(gs[1, 7:])
    pos, last = {}, -99.0
    for v, col in sorted((h[c].iloc[-1], c) for c, *_ in EJES):   # separa etiquetas a < 4,2 puntos
        pos[col] = max(v, last + 4.2); last = pos[col]
    for col, lab, c, _ in EJES:
        a2.plot(h["x"], h[col], color=c, lw=2.2)
        a2.text(h["x"].iloc[-1] + pd.Timedelta(days=14), pos[col], lab, color=c, fontsize=9.5, va="center", fontweight="bold")
    a2.set_title("Los cinco ejes", loc="left", fontsize=13, fontweight="bold", color=INK)
    a2.set_ylim(20, 85); a2.grid(axis="y", ls=":", alpha=.5)
    a2.set_xlim(h["x"].iloc[0], h["x"].iloc[-1] + pd.Timedelta(days=215))
    a2.set_xticks([t for t in pd.date_range(h["x"].iloc[0], h["x"].iloc[-1], freq="6MS")])

    for a in (a1, a2):
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        a.tick_params(labelsize=9, colors="#444")
        if a is a1:
            a.xaxis.set_major_locator(matplotlib.dates.MonthLocator(bymonth=(1, 7)))
        a.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(_fmt_mes))

    # ---------- barras por eje ----------
    a3 = fig.add_subplot(gs[2, :])
    xs = list(range(len(EJES)))
    vals = [cur[c] for c, *_ in EJES]
    a3.bar(xs, vals, color=[e[2] for e in EJES], width=0.55, zorder=3)
    a3.set_ylim(0, 108); a3.set_xlim(-0.6, len(EJES) - 0.4); a3.grid(axis="y", ls=":", alpha=.5, zorder=0)
    for i, (e, v) in enumerate(zip(EJES, vals)):
        d = cur[e[0]] - prev[e[0]]
        col = VERDE if d > 0.05 else (ROJO_DELTA if d < -0.05 else GRAY)
        a3.text(i, v + 2.5, f1(v), ha="center", fontsize=15, fontweight="bold", color=INK)
        a3.text(i, v + 13, f"{fs(d)} vs {AB[pm - 1]}", ha="center", fontsize=10.5, color=col)
        a3.text(i, 4, f"peso {int(round(e[3] * 100))}%", ha="center", fontsize=9.5, color="white", fontweight="bold")
    a3.set_xticks(xs); a3.set_xticklabels([e[1] for e in EJES], fontsize=12, fontweight="bold")
    a3.set_title(f"Cada eje en {MESES[m - 1]} (variación contra {MESES[pm - 1]})", loc="left", fontsize=13, fontweight="bold", color=INK)
    for s in ("top", "right"):
        a3.spines[s].set_visible(False)
    a3.tick_params(axis="y", labelsize=9, colors="#444")

    pie = ("Fuente: Monitor Institucional Argentino, Fundación Libertad y Progreso. Serie publicada desde enero de 2024, "
           "meses cerrados y congelados; 18 variables en 5 ejes, suavizadas con media móvil de 12 meses.")
    if provisional:
        pie += "\nEl último punto (hueco) es provisional: nowcast del mes en curso, se actualiza hasta que el mes cierra."
    fig.text(0.06, 0.004 if provisional else 0.018, pie, fontsize=8.5, color=GRAY, va="bottom")

    out = Path(salida) if salida else DOCS_DIR / f"MIA — Panorama ({MESES[m - 1].capitalize()} {y}).png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, facecolor="white")
    plt.close(fig)
    log.info("Panorama %s: MIA %s (%s) → %s", cur["periodo"], f1(cur["MIA"]), "provisional" if provisional else "cierre definitivo", out.name)
    return out


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="MIA — imagen-resumen mensual (panorama)")
    ap.add_argument("--mes", help="AAAA-MM (default: último mes del histórico)")
    ap.add_argument("--salida", help="ruta de salida (default: Documentos/MIA — Panorama (<Mes> <Año>).png)")
    args = ap.parse_args()
    return 0 if generar(args.mes, args.salida) else 1


if __name__ == "__main__":
    sys.exit(main())
