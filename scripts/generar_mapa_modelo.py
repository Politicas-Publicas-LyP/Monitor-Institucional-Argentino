"""
MIA — Generador del mapa interactivo del modelo
===============================================
Arma un grafo navegable (HTML autocontenido, sin dependencias ni red) con TODO el
sistema: fuentes oficiales → scripts → series → 18 variables → 5 ejes → MIA, más
los satélites (radares del BORA, padrón judicial vivo, tablas mantenidas a mano)
y los consumidores (QA, histórico, gráficos, reporte, núcleo).

La estructura sale del propio repo, no de una copia a mano:
  · 00_Comun/variables.yaml      -> variables, ejes, pesos, anclas, modos, núcleo
  · output/mia_mensual.csv       -> scores del último mes y del anterior
  · output/mia_historico.csv     -> estado del mes (provisional / cerrado)
  · output/_alertas_validacion.md-> frescura por archivo
  · scripts/mapa_modelo_topologia.py -> las cañerías (qué fuente alimenta a qué)

Uso:  python3 scripts/generar_mapa_modelo.py
Salida: Documentos/MIA — Mapa del modelo.html
Requisitos: pandas, pyyaml (ya están en 00_Comun/requirements.txt)
"""
from __future__ import annotations
import json, re, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import yaml

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "scripts"))
from mapa_modelo_topologia import FUENTES, SCRIPTS, DATOS, EXTRA_LINKS  # noqa: E402

OUT = BASE / "output"
DOCS = BASE / "Documentos"
PLANTILLA = BASE / "scripts" / "mapa_modelo.plantilla.html"
DESTINO = DOCS / "MIA — Mapa del modelo.html"

MESES = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
EJES = ["Ejecutivo", "Legislativo", "Judicial", "Prensa", "Banco Central"]


def num(x, dec=1):
    """Formato es-AR (coma decimal) o s/d."""
    return "s/d" if x is None or pd.isna(x) else f"{float(x):.{dec}f}".replace(".", ",")


def mes_label(per: str) -> str:
    y, m = per.split("-")
    return f"{MESES[int(m)]} de {y}"


# ─────────────────────────── lectura del repo ───────────────────────────────
def leer_frescura() -> dict:
    """{archivo: (ultimo, meses, tolerancia)} desde el reporte de QA."""
    f = OUT / "_alertas_validacion.md"
    if not f.exists():
        return {}
    out = {}
    for ln in f.read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in ln.split("|")]
        if len(c) >= 7 and c[2].endswith("_mensual"):
            try:
                out[c[2]] = (c[3], int(c[4]), int(c[5]))
            except ValueError:
                pass
    return out


def leer_valores():
    """(mes, mes_previo, estado, serie_de_valores) desde el índice publicado."""
    f = OUT / "mia_mensual.csv"
    if not f.exists():
        return None, None, "sin datos", {}, {}
    df = pd.read_csv(f, dtype={"periodo": str}).set_index("periodo")
    mes = df.index[-1]
    prev = df.index[-2] if len(df) > 1 else None
    estado = "provisional"
    fh = OUT / "mia_historico.csv"
    if fh.exists():
        h = pd.read_csv(fh, dtype={"periodo": str})
        r = h[h["periodo"] == mes]
        if not r.empty:
            estado = str(r["estado"].iloc[0])
    cur = df.loc[mes].to_dict()
    ant = df.loc[prev].to_dict() if prev else {}
    return mes, prev, estado, cur, ant


# ─────────────────────────── armado del grafo ───────────────────────────────
def construir():
    cfg = yaml.safe_load((BASE / "00_Comun" / "variables.yaml").read_text(encoding="utf-8"))
    macro = {k: float(v) for k, v in cfg["macro"].items()}
    carry = int(cfg.get("carry_meses", 3))
    mes, prev, estado, cur, ant = leer_valores()
    fresc = leer_frescura()

    nodes, links = [], []
    def N(**kw): nodes.append(kw)
    def L(s, t, kind="flujo", w=None, label=None, nota=None):
        links.append({k: v for k, v in
                      dict(source=s, target=t, kind=kind, w=w, label=label, nota=nota).items()
                      if v is not None})

    # 1) fuentes oficiales
    for f in FUENTES:
        N(id=f["id"], label=f["label"], corto=f.get("corto"), tipo="fuente", eje="Infra", nota=f["nota"],
          fuera=f.get("fuera", False),
          meta=[("Host", f["host"]),
                ("Requiere IP argentina", "sí — bloquea datacenter/exterior" if f["ip_ar"] else "no")])

    # 2) scripts
    for s in SCRIPTS:
        N(id=s["id"], label=s["label"], tipo="script", eje=s["eje"], nota=s["nota"],
          fuera=s.get("fuera", False),
          meta=[("Archivo", s["archivo"])] + ([("Rol", s["rol"])] if s.get("rol") else []))

    # 3) datos declarados en la topología
    for d in DATOS:
        N(id=d["id"], label=d["label"], tipo="dato", clase=d["clase"], eje=d["eje"],
          nota=d["nota"], fuera=d.get("fuera", False), meta=[("Tipo", d["clase"])])

    # 4) series mensuales: nodo por cada CSV que produce un scraper del índice
    ya = {d["id"] for d in DATOS}   # d_mia_mensual y d_nucleo_mensual ya son nodos de salida
    series = sorted({p for s in SCRIPTS for p in s["produce"] if p.endswith("_mensual")} - ya)
    for ser in series:
        u, m, tol = fresc.get(ser, (None, None, None))
        meta = [("Archivo", f"output/{ser}_<timestamp>.csv")]
        if m is not None:
            meta.append(("Frescura (QA)", f"{m} mes(es) de atraso · tolerancia {tol}"))
        N(id=ser, label=ser, tipo="dato", clase="serie", eje="Infra", nota=None,
          meta=meta, frescura=m, tolerancia=tol)

    # 5) aristas fuente→script y script→dato
    for s in SCRIPTS:
        for r in s["lee"]:
            L(r, s["id"], kind="config" if r.startswith(("cfg_", "t_")) else "flujo")
        for p in s["produce"]:
            L(s["id"], p, kind="alerta" if s.get("rol", "").startswith("radar") else "flujo")

    # 6) el modelo: series → variable → eje → MIA
    N(id="MIA", label="MIA", tipo="indice", eje="Indice",
      score=cur.get("MIA"), delta=(cur.get("MIA", 0) - ant.get("MIA", 0)) if ant else None,
      nota="Índice mensual de calidad republicana 0–100, anclado a un ideal absoluto. "
           "Promedio ponderado de los 5 ejes con pesos macro fijos.",
      meta=[("Mes", mes_label(mes) if mes else "s/d"), ("Estado", estado),
            ("Escala", "0 = colapso institucional · 100 = ideal republicano"),
            ("Suavizado", "media móvil de 12 meses"),
            ("Publicado desde", "2024-01 (calculado desde 2023-01 como colchón)")])
    for e in EJES:
        sc = cur.get(f"sub_{e}")
        N(id=f"eje_{e}", label=e, tipo="eje", eje=e, score=sc,
          delta=(sc - ant.get(f"sub_{e}")) if (ant and sc is not None and ant.get(f"sub_{e}") is not None) else None,
          nota=f"Sub-índice del eje {e}. Se renormaliza sobre las variables disponibles, "
               "así que una variable ausente no altera el peso macro del poder.",
          meta=[("Peso macro", f"{macro[e]*100:.0f}%"),
                ("Variables", str(sum(1 for v in cfg["variables"] if v["eje"] == e)))])
        L(f"eje_{e}", "MIA", w=macro[e], label=f"peso macro {macro[e]*100:.0f}%")

    derivadas = {}
    for v in cfg["variables"]:
        vid = "var_" + re.sub(r"[^a-z0-9]+", "_", v["var"].lower()).strip("_")
        sc = cur.get(v["var"])
        modos = sorted({c.get("modo", "suavizado") for c in v["comp"]})
        meta = [("Eje", v["eje"]), ("Peso en el índice", f"{v['peso']*100:.0f}%"),
                ("Modo", ", ".join(modos))]
        for i, c in enumerate(v["comp"], 1):
            rot = "Componente" if len(v["comp"]) == 1 else f"Componente {i}"
            meta.append((rot, f"{c['archivo']} → {c['col']} · ancla {c['mejor']}→100 / {c['peor']}→0 · "
                              f"peso intra {c['peso_intra']} · {c.get('modo','suavizado')}"))
        meta.append(("En el Núcleo", "sí" + (" (con componentes propios: nucleo_comp)" if v.get("nucleo_comp") else "")
                     if v.get("nucleo") else "no"))
        if "arrastre" in modos:
            meta.append(("Arrastre", f"caída inmediata, recuperación en {carry} meses"))
        N(id=vid, label=v["var"], tipo="variable", eje=v["eje"], score=sc,
          delta=(sc - ant.get(v["var"])) if (ant and sc is not None and ant.get(v["var"]) is not None) else None,
          nucleo=bool(v.get("nucleo")), nucleo_propio=bool(v.get("nucleo_comp")),
          nota=None, meta=meta)
        L(vid, f"eje_{v['eje']}", w=v["peso"], label=f"peso {v['peso']*100:.0f}%")
        for c in v["comp"]:
            etiq = f"{c['col']} · peso intra {c['peso_intra']} · {c['mejor']}→100 / {c['peor']}→0"
            if c["archivo"] == "__derived__":
                did = "der_" + c["col"]
                if did not in derivadas:
                    derivadas[did] = c["col"]
                    N(id=did, label=c["col"], tipo="dato", clase="derivada", eje=v["eje"],
                      nota="Serie derivada: se calcula en el ensamblador combinando dos fuentes "
                           "(leyes sancionadas de InfoLEG ÷ sesiones realizadas de HCDN, ventana 12m).",
                      meta=[("Definición", "leyes_12m / sesiones_realizadas_12m, con ffill")])
                    L("calidad_normativa_mensual", did, label="n_leyes_sancionadas")
                    L("sesiones_mensual", did, label="real_12m")
                L(did, vid, w=c["peso_intra"], label=etiq)
            else:
                L(c["archivo"], vid, w=c["peso_intra"], label=etiq)

    # 7) quién calcula y quién consume
    L("sc_ensamblado", "MIA", kind="calcula", nota="Aplica anclaje, suavizado, ffill de estados, arrastre y renormalización.")
    L("MIA", "d_mia_mensual", label="se materializa en el CSV publicado")
    for src, tgt, *_ in [(l["source"], l["target"]) for l in EXTRA_LINKS]:
        pass
    for l in EXTRA_LINKS:
        L(l["source"], l["target"], kind=l.get("kind", "flujo"), nota=l.get("nota"))

    # 8) agrupamiento espacial: cada serie hereda el eje de la variable que alimenta y
    #    cada fuente el de los scripts que abastece (si abastece a varios, queda compartida).
    porid = {n["id"]: n for n in nodes}
    for n in nodes:
        if n.get("clase") == "serie":
            ejes = {porid[l["target"]]["eje"] for l in links
                    if l["source"] == n["id"] and porid.get(l["target"], {}).get("tipo") == "variable"}
            if len(ejes) == 1:
                n["eje"] = ejes.pop()
    for n in nodes:
        if n["tipo"] == "fuente":
            ejes = {porid[l["target"]]["eje"] for l in links
                    if l["source"] == n["id"] and porid.get(l["target"], {}).get("tipo") == "script"}
            ejes.discard("Infra")
            n["eje"] = ejes.pop() if len(ejes) == 1 else "Infra"
            n["compartida"] = len(ejes) > 1

    ids = {n["id"] for n in nodes}
    huerf = [l for l in links if l["source"] not in ids or l["target"] not in ids]
    if huerf:
        raise SystemExit(f"Aristas sin nodo: {huerf}")

    meta = {
        "mes": mes, "mes_label": mes_label(mes) if mes else "s/d", "estado": estado,
        "mes_previo": prev, "mes_previo_label": mes_label(prev) if prev else "s/d",
        "generado": (datetime.now(timezone.utc) - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
        "n_variables": len(cfg["variables"]),
        "n_nucleo": sum(1 for v in cfg["variables"] if v.get("nucleo")),
        "macro": macro, "ejes": EJES,
    }
    return {"nodes": nodes, "links": links, "meta": meta}


def main() -> int:
    datos = construir()
    if not PLANTILLA.exists():
        raise SystemExit(f"Falta la plantilla: {PLANTILLA}")
    html = PLANTILLA.read_text(encoding="utf-8").replace(
        "/*__DATOS__*/", json.dumps(datos, ensure_ascii=False))
    DOCS.mkdir(exist_ok=True)
    DESTINO.write_text(html, encoding="utf-8")
    n, l = len(datos["nodes"]), len(datos["links"])
    print(f"OK — {DESTINO.name}: {n} nodos, {l} aristas · mes {datos['meta']['mes']} ({datos['meta']['estado']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
