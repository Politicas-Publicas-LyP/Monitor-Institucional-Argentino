"""
MIA — NÚCLEO MENSUAL (serie larga, 2020+ a frecuencia mensual)
==============================================================
Núcleo general del índice: el mismo método anclado al ideal del MIA, pero restringido
al SUBCONJUNTO de variables con serie larga y consistente (las que existen desde mucho
antes de 2023), a FRECUENCIA MENSUAL. Sirve como serie de fondo para actualizar mes a
mes en paralelo al MIA pleno (18 variables, desde 2023).

Reutiliza la maquinaria de 00_Comun/icia_ensamblado.py (anchor, load, suavizado 12m,
NO_SUAVIZAR, renormalización por eje y pesos macro fijos). Calcula con arranque temprano
(warmup) para que el suavizado de 12 meses esté completo, y publica desde --desde.

Variables EXCLUIDAS (series cortas): Discrecionalidad, Transparencia AAIP, Escrutinio,
Causas contra periodistas, Acceso de la prensa. Carta Orgánica entra desde que hay
recaudación+balance (2023 en estos datos; correr scraper_21 --desde 2020 para extenderla).

Uso: py mia_nucleo_mensual.py --desde 2020-01 --hasta 2026-05
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "00_Comun"))
from icia_ensamblado import anchor, load, cargar_nucleo, NO_SUAVIZAR, MACRO, OUTPUT_DIR  # noqa

# FUENTE ÚNICA: las variables del núcleo salen de variables.yaml (nucleo: true;
# con nucleo_comp donde la serie larga difiere del pleno). Antes esta lista vivía
# hardcodeada acá, duplicando anclas y pesos (riesgo de drift): 2026-08-19.
NUCLEO = cargar_nucleo()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--desde",default="2020-01"); ap.add_argument("--hasta",default="2026-05")
    ap.add_argument("--suavizado",type=int,default=12); a=ap.parse_args()
    idx=pd.period_range("2003-01",a.hasta,freq="M")  # warmup largo para el suavizado
    var_scores={}
    for v in NUCLEO:
        cs,cw=[],[]
        for arch,col,vb,vw,w in v["comp"]:
            raw=load(arch,col,idx)
            if raw is None or raw.dropna().empty: continue
            cs.append(anchor(raw,vb,vw,a.suavizado,col not in NO_SUAVIZAR)*w)
            cw.append(raw.notna().rolling(a.suavizado,min_periods=3).max().fillna(0)*w)
        if not cs: var_scores[v["var"]]=pd.Series(float("nan"),index=idx); continue
        num=pd.concat(cs,axis=1).sum(axis=1,min_count=1); den=pd.concat(cw,axis=1).sum(axis=1,min_count=1)
        var_scores[v["var"]]=(num/den).clip(0,1)
    vs=pd.DataFrame(var_scores); pesos={v["var"]:v["peso"] for v in NUCLEO}
    out=pd.DataFrame(index=idx)
    for cat in MACRO:
        vc=[v["var"] for v in NUCLEO if v["cat"]==cat]; w=pd.Series({v:pesos[v] for v in vc}); sub=vs[vc]
        wmat=sub.notna().mul(w,axis=1)
        out[f"sub_{cat}"]=(sub.mul(w,axis=1).sum(axis=1,min_count=1)/wmat.sum(axis=1).replace(0,float("nan")))*100
    subm=pd.DataFrame({c:out[f"sub_{c}"] for c in MACRO}); wM=pd.Series(MACRO); wmat=subm.notna().mul(wM,axis=1)
    out["MIA_nucleo"]=(subm.mul(wM,axis=1).sum(axis=1,min_count=1)/wmat.sum(axis=1).replace(0,float("nan")))
    out["ejes_cubiertos"]=subm.notna().sum(axis=1).astype(int)
    out=out[out.index>=pd.Period(a.desde,"M")]
    o=out.reset_index(names="periodo"); o["periodo"]=o["periodo"].astype(str)
    o=o[["periodo","MIA_nucleo","sub_Ejecutivo","sub_Legislativo","sub_Judicial","sub_Prensa","sub_Banco Central","ejes_cubiertos"]]
    o.to_csv(OUTPUT_DIR/"mia_nucleo_mensual.csv",index=False,encoding="utf-8")
    print(o.round(1).to_string(index=False))
    print("\nCSV:",OUTPUT_DIR/"mia_nucleo_mensual.csv")
    return 0
if __name__=="__main__": sys.exit(main())
