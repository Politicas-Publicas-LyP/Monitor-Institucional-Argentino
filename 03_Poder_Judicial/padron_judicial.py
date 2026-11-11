"""
MIA — Padrón Judicial Vivo (cobertura e independencia, eje Judicial)
===================================================================
Mantiene un PADRÓN de cargos de JUECES (un cargo por fila) que arranca del último snapshot
oficial del dataset de magistrados (datos.jus.gob.ar) y que el bot va actualizando EN VIVO
con los decretos del BORA:
  - ALTAS  (designaciones de juez titular)            → el cargo pasa a Titular   (radar de nombramientos)
  - BAJAS  (renuncias/ceses/jubilaciones/remociones)  → el cargo pasa a Vacante   (detector de bajas, a futuro)

Con el padrón actualizado se RECALCULAN las tasas (titularidad/subrogancia/sin-cobertura/
vacancia) sobre los cargos HABILITADOS — mismo universo que el índice — marcadas «estimado»
mientras el dataset oficial no se actualice. Cada snapshot oficial nuevo RECONCILIA y reinicia
el padrón desde el dato duro.

Gobernanza (línea no-IA del MIA): determinístico y auditable. Cada cargo guarda su
estado_fuente (oficial | estimado-radar | estimado-baja) y la norma/fecha que lo cambió. Los
eventos del BORA que no se puedan mapear con confianza a un cargo van a una COLA DE REVISIÓN.

Subcomandos:
    py padron_judicial.py --construir [--verbose]   # baja el snapshot oficial y crea el padrón base
    py padron_judicial.py --actualizar              # aplica altas (radar) y bajas sobre el padrón
Requisitos: pip install pandas requests
"""
from __future__ import annotations

import argparse
import io
import logging
import os
import re
import sys
import time
import unicodedata
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PACKAGE = "magistrados-justicia-federal-y-de-la-justicia-nacional"
API = f"https://datos.jus.gob.ar/api/3/action/package_show?id={PACKAGE}"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
PADRON = OUTPUT_DIR / "padron_judicial.csv"            # padrón vivo
PADRON_BASE = OUTPUT_DIR / "padron_judicial_base.csv"  # ancla = snapshot oficial
REVISION = OUTPUT_DIR / "padron_revision.csv"          # eventos sin cargo asignado
PENDIENTES = OUTPUT_DIR / "padron_pendientes_vigencia.csv"  # eventos con vigencia FUTURA (se aplican solos al llegar la fecha)
TASAS_EST = OUTPUT_DIR / "padron_tasas_estimadas.csv"  # tasas recalculadas
RADAR_ALTAS = OUTPUT_DIR / "nombramientos_jueces.csv"  # salida del radar (designaciones)
# Mismo puente que la cobertura. OJO con el slug: el repo se renombró a
# `Monitor-Institucional-Argentino` y `raw.githubusercontent.com` sobre el nombre VIEJO (…-ITR-)
# devuelve contenido desactualizado (verificado 2026-09-17). El default ya usa el nombre nuevo.
REPO_RAW = "https://raw.githubusercontent.com/Politicas-Publicas-LyP/Monitor-Institucional-Argentino/main/output"
RADAR_ALTAS_URL = os.environ.get("MIA_RADAR_CSV_URL") or f"{REPO_RAW}/nombramientos_jueces.csv"
if "-ITR-" in RADAR_ALTAS_URL:
    RADAR_ALTAS_URL = f"{REPO_RAW}/nombramientos_jueces.csv"
RADAR_BAJAS = OUTPUT_DIR / "bajas_jueces.csv"          # salida del detector de bajas (radar)
RADAR_BAJAS_URL = RADAR_ALTAS_URL.replace("nombramientos_jueces", "bajas_jueces")
# Fuente COMPLEMENTARIA de altas (2026-09-18): "Ternas remitidas al PEN" del Consejo de la
# Magistratura (mapadeconcursos), con fecha_designación confirmada por concurso/juzgado. NO
# reemplaza al radar del BORA (que sigue siendo la fuente primaria); es un segundo canal para
# detectar designaciones que el radar no pudo mapear. De las tres exportaciones del Consejo,
# solo esta ("Ternas remitidas al PEN") parsea limpio como CSV — las otras dos ("en trámite" y
# "concluidos") tienen columnas de texto libre (órdenes de mérito) con comas sin escapar que
# rompen el formato fila por fila; se descartaron por calidad de dato, no por falta de acceso.
CONSEJO_REMITIDOS_URL = "https://mc.consejomagistratura.gov.ar/mapadeconcursos/export_remitidos.php"
HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
           "Accept": "application/json,*/*"}

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("padron_judicial")

STOP = {"DE", "DEL", "LA", "LAS", "EL", "LOS", "EN", "LO", "Y", "A", "AL", "CON", "SI", "NO"}


# ──────────────────────────────────────────────────────────────────────────────
# Descarga del snapshot oficial (CKAN) — mismo origen que scraper_05
# ──────────────────────────────────────────────────────────────────────────────
def session() -> requests.Session:
    s = requests.Session()
    r = Retry(total=4, backoff_factor=2.0, status_forcelist=(429, 500, 502, 503, 504),
              allowed_methods=frozenset(["GET"]))
    s.mount("https://", HTTPAdapter(max_retries=r))
    s.headers.update(HEADERS)
    return s


def _read_csv_resilient(blob: bytes) -> pd.DataFrame | None:
    for enc in ("utf-8", "latin-1"):
        for sep in (",", ";"):
            try:
                df = pd.read_csv(io.BytesIO(blob), sep=sep, encoding=enc, dtype=str,
                                 low_memory=False, on_bad_lines="skip")
                if df.shape[1] > 3:
                    return df
            except Exception:  # noqa: BLE001
                continue
    return None


def _snapshot_date(name: str, last_modified: str | None) -> pd.Timestamp | None:
    m = re.search(r"(20\d{6})", name or "")
    if m:
        try:
            return pd.Timestamp(datetime.strptime(m.group(1), "%Y%m%d"))
        except ValueError:
            pass
    if last_modified:
        try:
            return pd.Timestamp(last_modified)
        except Exception:  # noqa: BLE001
            return None
    return None


def _es_jueces(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    ct = cols.get("cargo_tipo") or cols.get("tipo_cargo")
    if ct:
        return df[df[ct].astype(str).str.strip().str.lower().str.startswith("juez")]
    return df


def latest_jueces_snapshot(s: requests.Session):
    resp = s.get(API, timeout=60)
    resp.raise_for_status()
    resources = resp.json()["result"]["resources"]
    log.info("Recursos en el dataset: %s", len(resources))
    mejor = None
    for r in resources:
        url, fmt, name = r.get("url"), (r.get("format") or "").lower(), r.get("name") or ""
        if not url:
            continue
        try:
            blob = s.get(url, timeout=120).content
        except Exception as e:  # noqa: BLE001
            log.warning("No pude bajar %s: %s", name, e)
            continue
        dfs = []
        if "zip" in fmt or url.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(blob)) as zf:
                    for n in zf.namelist():
                        if n.lower().endswith(".csv"):
                            d = _read_csv_resilient(zf.read(n))
                            if d is not None:
                                dfs.append((n, d))
            except Exception:  # noqa: BLE001
                continue
        else:
            d = _read_csv_resilient(blob)
            if d is not None:
                dfs.append((name, d))
        for nm, d in dfs:
            cl = {c.lower(): c for c in d.columns}
            if not (cl.get("cargo_cobertura") or cl.get("cobertura")):
                continue
            fecha = _snapshot_date(nm, r.get("last_modified"))
            if fecha is None:
                continue
            if mejor is None or fecha > mejor[0]:
                mejor = (fecha, d, nm)
    if mejor is None:
        raise RuntimeError("No encontré un recurso con cobertura en el dataset.")
    fecha, df, nm = mejor
    log.info("Snapshot elegido: %s (%s) — %s filas", nm, fecha.date(), len(df))
    return _es_jueces(df), fecha


# ──────────────────────────────────────────────────────────────────────────────
# Normalización e identidad del cargo (para el matching con los decretos del BORA)
# ──────────────────────────────────────────────────────────────────────────────
def normaliza(s: str) -> str:
    s = str(s)
    # Unificar el marcador de número ANTES de quitar acentos: el «º» de «Nº» se descompone
    # en «o» (Nº → NO) y se perdería el número del juzgado. Lo pasamos a «N » primero.
    s = re.sub(r"[Nn][º°ªᵒ]\s*", "N ", s)
    s = re.sub(r"\b[Nn]ro\.?\s*", "N ", s)
    s = re.sub(r"\b[Nn][uú]mero\s*", "N ", s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").upper()
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # Sinónimos de jurisdicción: el decreto dice «Capital Federal»; el dataset «Ciudad
    # Autónoma de Buenos Aires». Unificamos a CABA para que matcheen.
    s = re.sub(r"\bCAPITAL FEDERAL\b", "CABA", s)
    s = re.sub(r"\bCIUDAD AUTONOMA DE BUENOS AIRES\b", "CABA", s)
    s = re.sub(r"\bCIUDAD DE BUENOS AIRES\b", "CABA", s)
    s = re.sub(r"\bC A B A\b", "CABA", s)
    s = re.sub(r"\bCAP FEDERAL\b", "CABA", s)
    s = re.sub(r"\bLA CAPITAL\b", "LA CABA", s)      # «… N° 4 de la Capital» (sin «Federal»)
    return s


# Nombres de órganos. El sistema acusatorio los fue renombrando y el padrón oficial mezcla ambos
# nombres según la provincia (p. ej. «Tribunal Federal de Juicio de Neuquén» pero «Tribunal Oral
# en lo Criminal Federal de Corrientes»); el decreto puede usar el otro. Caso real que lo motivó:
# Decreto 1066/2026 («Tribunal Federal de Juicio de Corrientes») vs padrón («Tribunal Oral en lo
# Criminal Federal de Corrientes»). Se pasan a una forma CANÓNICA antes de comparar, de los dos lados.
ALIAS_ORGANO = [
    (r"\bTRIBUNAL(?:ES)? ORAL(?:ES)? EN LO CRIMINAL FEDERAL\b", "TRIBUNAL FEDERAL DE JUICIO"),
    (r"\bTRIBUNAL(?:ES)? ORAL(?:ES)? FEDERAL(?:ES)?\b", "TRIBUNAL FEDERAL DE JUICIO"),
    (r"\bTRIBUNAL(?:ES)? DE JUICIO FEDERAL(?:ES)?\b", "TRIBUNAL FEDERAL DE JUICIO"),
    (r"\bJUZGADO FEDERAL DE (?:PRIMERA INSTANCIA|GARANTIAS?)\b", "JUZGADO FEDERAL"),
]
# Palabras de tipo/materia de órgano: NO identifican un lugar.
GENERICO = {"APELACIONES", "JUICIO", "INSTANCIA", "CASACION", "PENAL", "CRIMINAL", "FEDERAL", "NACIONAL",
            "CIVIL", "COMERCIAL", "TRABAJO", "SEGURIDAD", "SOCIAL", "CONTENCIOSO", "ADMINISTRATIVO",
            "ELECTORAL", "ECONOMICO", "CORRECCIONAL", "EJECUCION", "MENORES", "FAMILIA", "GARANTIA",
            "GARANTIAS", "FUNCIONES", "ASIENTO", "CIUDAD", "SALA", "TRIBUNAL", "JUZGADO", "CAMARA", "ORAL",
            "VOCALIA", "VOCAL", "SECRETARIA"}


def canon(s: str) -> str:
    """Forma canónica de un nombre de órgano: sin el paréntesis «(con funciones de Juicio)», que
    describe la función y no identifica el órgano, y con los sinónimos unificados."""
    t = normaliza(re.sub(r"\([^)]*\)", " ", str(s)))
    t = re.split(r"\b(?:A LA DOC\w*|AL DOC\w*|A LA DRA?|AL DR)\b", t)[0].strip()   # coletilla «… a la doctora X»
    for pat, rep in ALIAS_ORGANO:
        t = re.sub(pat, rep, t)
    return t


def tokens(s: str) -> set:
    return {t for t in canon(s).split() if t not in STOP and (len(t) > 1 or t.isdigit())}


def lugar(org: str) -> set:
    """Tokens del LUGAR de un órgano (ciudad): lo que sigue al último «DE». Se ignora el sufijo
    «, PROVINCIA DE X» (repite la provincia) y las salas. Vacío si no se puede inferir un lugar."""
    t = canon(org)
    t = re.sub(r"\bSALA [A-Z0-9]+\b", " ", t)
    m = re.search(r"\bPROVINCIA DEL? [A-Z ]+?\s*$", t)
    if m:
        t = t[:m.start()].strip()
    partes = re.split(r"\bDE\b", t)
    if len(partes) < 2:
        return set()
    return {w for w in partes[-1].split() if w not in STOP and w not in GENERICO and len(w) > 1 and not w.isdigit()}


def numero(s: str):
    m = re.search(r"\bN (\d+)\b", normaliza(s))
    return m.group(1) if m else None


def limpiar_organo(texto: str) -> str:
    """Recorta la coletilla del nombre del juez (… al doctor X / D.N.I. …)."""
    t = normaliza(texto)
    t = re.split(r"\bDOCTORA?\b|\bDOCTORES\b|\bDRA?\b|\bD N I\b", t)[0]
    return t.strip()


_TEXTO_BORA: dict = {}


def _texto_bora(url: str) -> str:
    """Texto plano de un aviso del BORA ('' si no se pudo leer). Se cachean solo las lecturas
    EXITOSAS (el mismo decreto se consulta para el órgano y para la vigencia); un fallo se reintenta."""
    if url in _TEXTO_BORA:
        return _TEXTO_BORA[url]
    for intento in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                _TEXTO_BORA[url] = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", r.text))
                return _TEXTO_BORA[url]
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1.5 * (intento + 1))
    return ""


_MESES = {m: i + 1 for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
                                           "agosto", "septiembre", "octubre", "noviembre", "diciembre"])}
_MESES["setiembre"] = 9


def vigencia_desde_texto(txt: str):
    """Fecha desde la que rige el decreto, si dice «a partir del 1° de diciembre de 2026» o
    «a partir del 01/12/2026» (también «con efecto al/a partir del …»). None si no aclara: rige
    desde la publicación. Importa en renuncias/ceses con fecha futura."""
    pre = r"(?:a\s+partir\s+del?|con\s+efectos?\s+(?:a\s+partir\s+del?|al|desde\s+el))\s+"
    m = re.search(pre + r"(\d{1,2})\s*(?:°|º|ro|er)?\s+de\s+([A-Za-záéíóúÁÉÍÓÚ]+)\s+de(?:l)?\s+(\d{4})", txt, re.I)
    if m:
        mes = _MESES.get(unicodedata.normalize("NFKD", m.group(2).lower()).encode("ascii", "ignore").decode())
        if mes:
            try:
                return pd.Timestamp(int(m.group(3)), mes, int(m.group(1)))
            except ValueError:
                return None
    m = re.search(pre + r"(\d{1,2})/(\d{1,2})/(\d{4})", txt, re.I)
    if m:
        try:
            return pd.Timestamp(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    return None


def vigencia_desde_bora(url: str):
    return vigencia_desde_texto(_texto_bora(url))


def organo_desde_bora(url: str) -> str:
    """Lee el cuerpo del decreto en el BORA y extrae el ÓRGANO al que se designa, cubriendo
    todos los tipos (juzgado, cámara, sala, tribunal oral, tribunal federal de juicio, etc.).
    Es la fuente autoritativa para el matching; el `organo` del radar queda como respaldo."""
    try:
        t = _texto_bora(url)
        if not t:
            return ""
        m = re.search(
            r"\b(?:JUEZ|JUEZA|JUECES|VOCAL|MAGISTRAD\w*)\b\s+DE\s*L?\s+(?:LA\s+)?(.+?)"
            r"(?:,?\s+a\s+l[ao]\s+(?:doctora?|dra?)\b|,?\s+al\s+(?:doctora?|dr)\b|\(?\s*D\.?N\.?I|\.\s|$)",
            t, re.IGNORECASE)
        return m.group(1).strip() if m else ""
    except Exception:  # noqa: BLE001
        return ""


# ──────────────────────────────────────────────────────────────────────────────
# CONSTRUIR el padrón base desde el snapshot oficial
# ──────────────────────────────────────────────────────────────────────────────
def _estado(cobertura: str, vacante: str) -> str:
    c = (cobertura or "").strip().lower()
    v = (vacante or "").strip().upper() in ("SI", "SÍ")
    if c == "titular":
        return "Titular"
    if "sin subrogante" in c:
        return "Sin cobertura"
    if c == "subrogante":
        return "Subrogante"
    if v:
        return "Vacante"
    return (cobertura or "").strip() or "Otro"


def _g(cols, *names):
    for n in names:
        if n in cols:
            return cols[n]
    return None


def construir(verbose: bool = False) -> int:
    OUTPUT_DIR.mkdir(exist_ok=True)
    s = session()
    df, fecha = latest_jueces_snapshot(s)
    cols = {c.lower(): c for c in df.columns}
    CAM = _g(cols, "camara"); TIP = _g(cols, "organo_tipo"); NOM = _g(cols, "organo_nombre")
    PRO = _g(cols, "organo_provincia"); JUR = _g(cols, "justicia_federal_o_nacional")
    HAB = _g(cols, "organo_habilitado"); MAG = _g(cols, "magistrado_nombre"); DNI = _g(cols, "magistrado_dni")
    CC = _g(cols, "cargo_cobertura", "cobertura"); CV = _g(cols, "cargo_vacante", "vacante")
    NT = _g(cols, "norma_tipo"); NN = _g(cols, "norma_numero", "norma"); NF = _g(cols, "norma_fecha")
    CO = _g(cols, "concurso_numero", "concurso")

    if verbose:
        print("\n=== COLUMNAS DEL DATASET (jueces) ===")
        print(list(df.columns))
        muestra = [c for c in [CAM, TIP, NOM, PRO, MAG, CC] if c]
        print("\n=== EJEMPLOS (8 cargos) ===")
        print(df[muestra].head(8).to_string(index=False))
        # DIAGNÓSTICO para la variable "duración de vacancia": qué campos de fecha hay y con
        # cuánta cobertura en los cargos NO titulares (para elegir bien cómo medir la antigüedad).
        no_tit = df[df[CC].astype(str).str.strip().str.lower() != "titular"] if CC else df
        print(f"\n=== CAMPOS DE FECHA (cargos NO titulares: {len(no_tit)}) ===")
        for fcol in ["concurso_ambito_fecha_ingreso", "subrogancia_fecha_vencimiento",
                     "cargo_fecha_jura", "norma_fecha", "concurso_en_tramite"]:
            c = _g(cols, fcol)
            if c:
                nn = int(no_tit[c].notna().sum() - (no_tit[c].astype(str).str.strip() == "").sum())
                ej = list(no_tit[c].dropna().astype(str).str.strip().replace("", pd.NA).dropna().unique()[:5])
                print(f"  {fcol}: {nn}/{len(no_tit)} con dato | ej: {ej}")
            else:
                print(f"  {fcol}: (no está en el dataset)")
        # Distribución de ANTIGÜEDAD del concurso (meses) en cargos NO titulares → para calibrar anclas.
        ci = _g(cols, "concurso_ambito_fecha_ingreso")
        if ci:
            fi = pd.to_datetime(no_tit[ci], errors="coerce")
            ant = ((pd.Timestamp(fecha) - fi).dt.days / 30.44).dropna()
            if len(ant):
                print(f"\n=== ANTIGÜEDAD del concurso en cargos NO titulares (meses; snapshot {fecha.date()}) ===")
                print(f"  n={len(ant)}  mediana={ant.median():.1f}  media={ant.mean():.1f}  "
                      f"p25={ant.quantile(.25):.1f}  p75={ant.quantile(.75):.1f}  p90={ant.quantile(.90):.1f}  max={ant.max():.1f}")
                for u in (12, 24, 36, 48, 60):
                    print(f"  share con concurso > {u:>2}m sin resolver: {(ant > u).mean():.3f}")

    rows = []
    for _, r in df.iterrows():
        cam = str(r.get(CAM, "") or ""); nom = str(r.get(NOM, "") or ""); pro = str(r.get(PRO, "") or "")
        clave = normaliza(f"{cam} {nom} {pro}")
        rows.append({
            "jurisdiccion": str(r.get(JUR, "") or "").strip(),
            "camara": cam.strip(),
            "organo_tipo": str(r.get(TIP, "") or "").strip(),
            "organo_nombre": nom.strip(),
            "provincia": pro.strip(),
            "habilitado": str(r.get(HAB, "") or "").strip(),
            "estado": _estado(r.get(CC, ""), r.get(CV, "")),
            "cobertura_oficial": str(r.get(CC, "") or "").strip(),
            "magistrado": str(r.get(MAG, "") or "").strip(),
            "magistrado_dni": str(r.get(DNI, "") or "").strip(),
            "norma": (str(r.get(NT, "") or "").strip() + " " + str(r.get(NN, "") or "").strip()).strip(),
            "norma_fecha": str(r.get(NF, "") or "").strip(),
            "concurso": str(r.get(CO, "") or "").strip(),
            "estado_fuente": "oficial",
            "snapshot_fecha": str(fecha.date()),
            "evento_norma": "",
            "evento_fecha": "",
            "clave": clave,
        })
    pad = pd.DataFrame(rows)
    pad.insert(0, "cargo_id", (pad["clave"] + "#" + pad.groupby("clave").cumcount().astype(str)))
    pad.to_csv(PADRON_BASE, index=False, encoding="utf-8")
    pad.to_csv(PADRON, index=False, encoding="utf-8")
    log.info("Padrón base creado: %s cargos. Archivos: %s y %s", len(pad), PADRON_BASE.name, PADRON.name)
    print("\n=== ESTADOS (todos los cargos) ===")
    print(pad["estado"].value_counts().to_string())
    _imprimir_tasas(pad, etiqueta="oficial (base)")
    return 0


# ──────────────────────────────────────────────────────────────────────────────
# ACTUALIZAR el padrón con altas (radar) y bajas — matching por tokens + número
# ──────────────────────────────────────────────────────────────────────────────
def _filtrar_conf(d: pd.DataFrame, tipo: str) -> pd.DataFrame:
    d = d.fillna("")
    if "confianza" in d.columns:  # solo ALTA o confirmadas entran al valor
        conf = d["confianza"].str.upper().str.strip()
        m = conf.eq("ALTA")
        if "confirmado" in d.columns:
            cf = d["confirmado"].str.lower().str.strip()
            m = (m | cf.isin(["si", "sí", "true", "1"])) & ~cf.isin(["no", "false", "0"])
        d = d[m]
    d = d.copy()
    d["_tipo"] = tipo
    return d


def _cargar_eventos(path: Path, tipo: str, url: str = "") -> pd.DataFrame:
    """Lee eventos de la URL del repo (si está) o del archivo local; si ninguno, vacío."""
    if url:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200 and r.text.strip():
                log.info("%s: leído del repo (%s)", tipo, url)
                return _filtrar_conf(pd.read_csv(io.StringIO(r.text), dtype=str), tipo)
        except Exception as e:  # noqa: BLE001
            log.warning("No pude bajar %s del repo (%s); uso local. %s", tipo, url, e)
    if path.exists():
        return _filtrar_conf(pd.read_csv(path, dtype=str), tipo)
    return pd.DataFrame()


def _preparar(pad: pd.DataFrame) -> pd.DataFrame:
    """Columnas auxiliares del padrón para el matching. El LUGAR de un cargo es el de su propio órgano
    y provincia (_lug); la cámara de apelaciones NO cuenta, porque un juzgado de Jujuy depende de la
    Cámara Federal de Salta y no por eso es «de Salta». Solo para eventos de cámaras/salas se usa
    el lugar de la cámara (_lugc)."""
    pad["_tok"] = (pad["camara"] + " " + pad["organo_nombre"] + " " + pad["provincia"]).map(tokens)
    pad["_lug"] = (pad["organo_nombre"] + " " + pad["provincia"]).map(tokens)
    pad["_lugc"] = pad["_tok"]
    pad["_num"] = pad["organo_nombre"].map(numero)
    return pad


def _match_detalle(ev_org: str, pad: pd.DataFrame, umbral: float = 0.6):
    """Busca el órgano del evento en el padrón. Devuelve (índices de cargos, motivo_si_falla).
    Determinístico y CONSERVADOR con lo que puede dañar el dato: nunca cruza provincias.
      1. Los nombres se comparan en forma canónica (alias: «Tribunal Federal de Juicio» ≡ «Tribunal
         Oral en lo Criminal Federal»; se ignora el paréntesis «(con funciones de …)»).
      2. El número de juzgado, si está en ambos, debe coincidir.
      3. El LUGAR (ciudad) del decreto es OBLIGATORIO. Antes bastaba con compartir las palabras de
         tipo: un decreto de «Tribunal Federal de Juicio de Corrientes» podía aplicarse al de Neuquén.
         Si el lugar no aparece en ningún cargo, no se adivina: va a revisión humana.
    Entre los cargos que pasan, el orden es el de siempre (mejor puntaje primero)."""
    D = tokens(ev_org)
    dn = numero(ev_org)
    if not D:
        return [], "sin órgano identificable"
    L = lugar(ev_org)
    ce = canon(ev_org)
    es_camara = ce.startswith("CAMARA") or bool(re.search(r"\bSALA\b", ce))
    col_lug = ("_lugc" if es_camara else "_lug") if "_lug" in pad.columns else "_tok"
    cand, cand_sin_lugar = [], 0
    for i, rt, rl, rn in zip(pad.index, pad["_tok"], pad[col_lug], pad["_num"]):
        if dn and rn and dn != rn:
            continue
        sc = len(D & rt) / len(D)
        if sc < umbral:
            continue
        if L and not L <= rl:
            cand_sin_lugar += 1
            continue
        cand.append((sc, i))
    if not cand:
        if cand_sin_lugar:
            return [], f"el lugar del decreto ({' '.join(sorted(L))}) no coincide con ningún cargo del padrón"
        return [], "sin cargo coincidente"
    cand.sort(reverse=True)
    return [i for _, i in cand], ""


def _match(ev_org: str, pad: pd.DataFrame, umbral: float = 0.6):
    """Índices de los cargos candidatos del evento, mejor puntaje primero ([] si no hay)."""
    return _match_detalle(ev_org, pad, umbral)[0]


def _fix_anio_truncado(fecha_str: str) -> str:
    """El CSV del Consejo trae algunas fechas con el siglo en cero (ej. '0026-06-16' en vez de
    '2026-06-16' — bug de exportación de la fuente). Se corrige antes de parsear; sin esto, esas
    filas se pierden como fecha inválida."""
    fecha_str = (fecha_str or "").strip()
    return "20" + fecha_str[2:] if re.match(r"^00\d{2}-\d{2}-\d{2}", fecha_str) else fecha_str


def _cargar_eventos_consejo() -> pd.DataFrame:
    """Altas confirmadas por el Consejo de la Magistratura (ver nota en CONSEJO_REMITIDOS_URL).
    Se descarga fresco en cada corrida (regla de frescura); si falla o cambia de formato, se
    ignora sin frenar el resto de --actualizar (es un complemento, no la fuente primaria)."""
    try:
        r = requests.get(CONSEJO_REMITIDOS_URL, headers=HEADERS, timeout=60)
        if r.status_code != 200:
            log.warning("Consejo de la Magistratura: HTTP %s en export_remitidos.php — se ignora.", r.status_code)
            return pd.DataFrame()
        df = pd.read_csv(io.StringIO(r.text))
    except Exception as e:  # noqa: BLE001
        log.warning("Consejo de la Magistratura: no se pudo descargar/leer (%s) — se ignora.", type(e).__name__)
        return pd.DataFrame()
    df.columns = [c.strip() for c in df.columns]
    col_desig = next((c for c in df.columns if "designaci" in c.lower()), None)
    col_organo = next((c for c in df.columns if c.lower() == "juzgado_tribunal_camara_nombre"), None)
    col_nombre = next((c for c in df.columns if c.lower() == "nombre_apellido"), None)
    col_concurso = next((c for c in df.columns if re.match(r"concurso_n", c.lower())), None)
    if not (col_desig and col_organo):
        log.warning("Consejo de la Magistratura: cambiaron las columnas del export, no encuentro "
                    "designación/juzgado — se ignora esta corrida.")
        return pd.DataFrame()
    fecha = pd.to_datetime(df[col_desig].astype(str).map(_fix_anio_truncado), errors="coerce")
    df = df[fecha.notna()].copy()
    df["fecha_publicacion"] = fecha[fecha.notna()].dt.strftime("%Y-%m-%d")
    df["organo"] = df[col_organo]
    nombre = df[col_nombre].astype(str) if col_nombre else ""
    concurso = df[col_concurso].astype(str) if col_concurso else ""
    df["titulo"] = "Designación (Consejo de la Magistratura): " + nombre + " — concurso " + concurso
    df["confianza"] = "ALTA"   # fecha_designación ya confirmada por el propio Consejo
    df["url"] = ""             # no hay decreto asociado; el "organo" ya viene resuelto
    df["_fuente"] = "consejo_magistratura"
    log.info("Consejo de la Magistratura: %s designaciones confirmadas leídas.", len(df))
    return _filtrar_conf(df[["organo", "titulo", "confianza", "url", "fecha_publicacion", "_fuente"]], "alta")


def actualizar() -> int:
    if not PADRON_BASE.exists():
        log.error("No existe %s. Corré primero: padron_judicial.py --construir", PADRON_BASE.name)
        return 1
    pad = pd.read_csv(PADRON_BASE, dtype=str).fillna("")
    _preparar(pad)
    pad["_num"] = pad["organo_nombre"].map(numero)

    altas = _cargar_eventos(RADAR_ALTAS, "alta", url=RADAR_ALTAS_URL)
    bajas = _cargar_eventos(RADAR_BAJAS, "baja", url=RADAR_BAJAS_URL)
    consejo = _cargar_eventos_consejo()
    fuentes = [altas, bajas, consejo]
    eventos = pd.concat([x for x in fuentes if len(x)], ignore_index=True) \
        if any(len(x) for x in fuentes) else pd.DataFrame()

    # Solo eventos POSTERIORES al snapshot oficial: los anteriores ya están en el dato duro,
    # aplicarlos sería contar dos veces. El padrón es un overlay desde la fecha del snapshot.
    snap_fecha = pad["snapshot_fecha"].iloc[0] if len(pad) and "snapshot_fecha" in pad else ""
    if len(eventos) and snap_fecha:
        fp = pd.to_datetime(eventos.get("fecha_publicacion"), errors="coerce")
        corte = pd.to_datetime(snap_fecha, errors="coerce")
        previos = int((fp <= corte).sum())
        eventos = eventos[fp > corte]
        if previos:
            log.info("%s evento(s) <= snapshot (%s) ignorados: ya están en el dato oficial.", previos, snap_fecha)
    log.info("Eventos a aplicar (posteriores al snapshot): %s", len(eventos))

    revision, pendientes, aplicados, ya_aplicados_otra_fuente = [], [], 0, 0
    hoy = pd.Timestamp((datetime.now(timezone.utc) - timedelta(hours=3)).date())   # fecha de hoy en Argentina
    for _, ev in eventos.iterrows():
        # Autoritativo: leer el órgano del cuerpo del decreto (si hay URL de BORA); respaldo:
        # el `organo` que ya trae el evento (el Consejo de la Magistratura no tiene decreto
        # asociado, viene resuelto directamente).
        url_ev = ev.get("url", "")
        org_raw = (organo_desde_bora(url_ev) if url_ev else "") or ev.get("organo", "") or ev.get("titulo", "")
        org = limpiar_organo(org_raw)
        if url_ev:
            time.sleep(0.8)
        # Vigencia futura (p. ej. renuncia «a partir del 1° de diciembre»): el cargo sigue ocupado hasta
        # esa fecha. No se aplica todavía; como el padrón se rearma desde el snapshot en cada corrida,
        # el evento se aplica solo cuando llega la fecha.
        vig = vigencia_desde_bora(url_ev) if url_ev else None
        if vig is not None and vig > hoy:
            pendientes.append({**ev.to_dict(), "_vigencia": vig.strftime("%Y-%m-%d"), "_organo": org})
            continue
        cand, motivo_match = _match_detalle(org, pad)
        if not cand:
            revision.append({**ev.to_dict(), "_motivo": motivo_match, "_organo": org})
            continue
        objetivo, ya_titular = None, False
        for i in cand:                       # alta → un cargo NO titular; baja → uno Titular
            est = pad.at[i, "estado"]
            if ev["_tipo"] == "alta" and est != "Titular":
                objetivo = i; break
            if ev["_tipo"] == "alta" and est == "Titular":
                ya_titular = True
            if ev["_tipo"] == "baja" and est == "Titular":
                objetivo = i; break
        if objetivo is None:
            # Una alta del Consejo que ya encuentra el cargo en Titular casi siempre significa
            # que otra fuente (el radar del BORA) ya la aplicó antes en esta misma corrida —
            # no es un caso ambiguo, así que no ensucia la cola de revisión humana.
            if ya_titular and ev.get("_fuente") == "consejo_magistratura":
                ya_aplicados_otra_fuente += 1
                continue
            revision.append({**ev.to_dict(), "_motivo": f"match sin cargo en estado esperado ({ev['_tipo']})", "_organo": org})
            continue
        pad.at[objetivo, "estado"] = "Titular" if ev["_tipo"] == "alta" else "Vacante"
        pad.at[objetivo, "estado_fuente"] = ("estimado-consejo" if ev.get("_fuente") == "consejo_magistratura"
                                             else "estimado-radar") if ev["_tipo"] == "alta" else "estimado-baja"
        pad.at[objetivo, "evento_norma"] = str(ev.get("titulo", ""))[:120]
        pad.at[objetivo, "evento_fecha"] = ev.get("fecha_publicacion", "") or ev.get("fecha_deteccion", "")
        aplicados += 1
    if ya_aplicados_otra_fuente:
        log.info("%s alta(s) del Consejo de la Magistratura ya estaban aplicadas por otra fuente "
                 "(radar del BORA) — no se mandan a revisión.", ya_aplicados_otra_fuente)

    pad = pad.drop(columns=[c for c in ("_tok", "_lug", "_lugc", "_num") if c in pad.columns])
    pad.to_csv(PADRON, index=False, encoding="utf-8")
    pd.DataFrame(revision).to_csv(REVISION, index=False, encoding="utf-8")
    pd.DataFrame(pendientes).to_csv(PENDIENTES, index=False, encoding="utf-8")
    log.info("Aplicados: %s | a revisión: %s | con vigencia futura (se aplican solos): %s",
             aplicados, len(revision), len(pendientes))
    for p_ in pendientes:
        log.info("  vigencia %s — %s (%s)", p_["_vigencia"], p_.get("_organo", ""), p_.get("_tipo", ""))
    if revision:
        log.warning("%s evento(s) sin asignar → %s (revisión humana).", len(revision), REVISION.name)
    _imprimir_tasas(pad, etiqueta="estimado (vivo)")
    return 0


def _imprimir_tasas(pad: pd.DataFrame, etiqueta: str) -> None:
    base = pad[pad["habilitado"].astype(str).str.upper().isin(["SI", "SÍ"])] if "habilitado" in pad else pad
    n = max(len(base), 1)
    est = base["estado"].str.lower()
    fila = {"etiqueta": etiqueta, "n_cargos_habilitados": len(base),
            "tasa_titular": round((est == "titular").sum() / n, 4),
            "tasa_subrogancia": round((est == "subrogante").sum() / n, 4),
            "tasa_sin_cobertura": round((est == "sin cobertura").sum() / n, 4),
            "tasa_vacancia": round((est == "vacante").sum() / n, 4)}
    pd.DataFrame([fila]).to_csv(TASAS_EST, index=False, encoding="utf-8")
    print(f"\n=== TASAS [{etiqueta}] (sobre habilitados) ===")
    for k, v in fila.items():
        if k != "etiqueta":
            print(f"  {k}: {v}")


def _padron_demo() -> pd.DataFrame:
    """Mini padrón con los nombres reales mezclados (viejo y nuevo sistema) para la prueba."""
    filas = [
        ("Tribunal Oral en lo Criminal Federal de Corrientes", "Corrientes", "Titular"),
        ("Tribunal Oral en lo Criminal Federal de Corrientes", "Corrientes", "Sin cobertura"),
        ("Tribunal Federal de Juicio de Neuquén", "Neuquén", "Titular"),
        ("Tribunal Federal de Juicio de Neuquén", "Neuquén", "Sin cobertura"),
        ("Tribunal Oral en lo Criminal Federal Nº 1 de Rosario (con Funciones de Juicio)", "Santa Fe", "Titular"),
        ("Tribunal Oral en lo Criminal Federal Nº 2 de Rosario  (con Funciones de Juicio)", "Santa Fe", "Titular"),
        ("Juzgado Federal de Primera Instancia Nº 3 de Rosario (con funciones de Garantía)", "Santa Fe", "Titular"),
        ("Juzgado Nacional en lo Criminal y Correccional N° 9 de la Capital Federal", "Ciudad de Buenos Aires", "Titular"),
        ("Juzgado Nacional en lo Criminal y Correccional N° 10 de la Capital Federal", "Ciudad de Buenos Aires", "Titular"),
        ("Tribunal Oral en lo Criminal Federal de Mar del Plata", "Provincia de Buenos Aires", "Titular"),
        ("Juzgado Federal de Primera Instancia Nº 2 de Salta", "Salta", "Titular"),
        ("Juzgado Federal de Primera Instancia Nº 2 de Jujuy", "Jujuy", "Titular"),
    ]
    pad = pd.DataFrame(filas, columns=["organo_nombre", "provincia", "estado"])
    pad["camara"] = ""
    pad.loc[pad["organo_nombre"].str.contains("Primera Instancia Nº 2 de (?:Jujuy|Salta)"), "camara"] = \
        "Cámara Federal de Apelaciones de Salta"          # los juzgados de Jujuy dependen de la Cámara de Salta
    _preparar(pad)
    pad["_num"] = pad["organo_nombre"].map(numero)
    return pad


def _test() -> int:
    """Prueba sin red del matching (alias, lugar obligatorio, ambigüedad) y de la vigencia."""
    pad = _padron_demo()

    def orgs(texto):
        idx, motivo = _match_detalle(limpiar_organo(texto), pad)
        return sorted({pad.at[i, "organo_nombre"].split(" (")[0].strip() for i in idx}), motivo

    casos = [
        ("TRIBUNAL FEDERAL DE JUICIO DE CORRIENTES, PROVINCIA DE CORRIENTES",
         ["Tribunal Oral en lo Criminal Federal de Corrientes"], None),   # Decreto 1066/2026
        ("TRIBUNAL ORAL EN LO CRIMINAL FEDERAL DE NEUQUEN",
         ["Tribunal Federal de Juicio de Neuquén"], None),                 # alias al revés
        ("TRIBUNAL FEDERAL DE JUICIO DE SALTA", [], "no coincide"),   # NO se confunde con Neuquén
        ("TRIBUNAL FEDERAL DE JUICIO DE ROSARIO",                           # sin número: los de Rosario, no otros
         ["Tribunal Oral en lo Criminal Federal Nº 1 de Rosario", "Tribunal Oral en lo Criminal Federal Nº 2 de Rosario"], None),
        ("TRIBUNAL FEDERAL DE JUICIO N 2 DE ROSARIO",
         ["Tribunal Oral en lo Criminal Federal Nº 2 de Rosario"], None),
        ("JUZGADO FEDERAL DE GARANTIAS N 3 DE ROSARIO",
         ["Juzgado Federal de Primera Instancia Nº 3 de Rosario"], None),
        ("JUZGADO NACIONAL EN LO CRIMINAL Y CORRECCIONAL N 9 DE LA CAPITAL FEDERAL",
         ["Juzgado Nacional en lo Criminal y Correccional N° 9 de la Capital Federal"], None),
        ("TRIBUNAL ORAL EN LO CRIMINAL FEDERAL DE MAR DEL PLATA",
         ["Tribunal Oral en lo Criminal Federal de Mar del Plata"], None),
        ("JUZGADO FEDERAL DE PRIMERA INSTANCIA N 2 DE SALTA PROVINCIA DE SALTA",           # NO el de Jujuy
         ["Juzgado Federal de Primera Instancia Nº 2 de Salta"], None),
        ("JUZGADO NACIONAL EN LO CRIMINAL Y CORRECCIONAL N 9 DE LA CAPITAL",                  # «de la Capital» a secas
         ["Juzgado Nacional en lo Criminal y Correccional N° 9 de la Capital Federal"], None),
        ("JUZGADO NACIONAL EN LO CRIMINAL Y CORRECCIONAL N 10 DE LA CABA A LA DOCT",          # coletilla truncada
         ["Juzgado Nacional en lo Criminal y Correccional N° 10 de la Capital Federal"], None),
    ]
    ok = 0
    print("=== TEST padrón judicial (matching de órganos) ===")
    for texto, esperado, motivo in casos:
        got, mot = orgs(texto)
        bien = (got == sorted(e.split(" (")[0].strip() for e in esperado)) and (motivo is None or motivo in mot)
        ok += bien
        print(f"  [{'OK' if bien else '✗'}] {texto[:62]:62s} → {got or mot}")
    vig = [
        ("Acéptase, a partir del 1° de diciembre de 2026, la renuncia presentada", pd.Timestamp(2026, 12, 1)),
        ("a partir del 15/03/2027 la renuncia", pd.Timestamp(2027, 3, 15)),
        ("con efectos a partir del 2 de setiembre de 2026", pd.Timestamp(2026, 9, 2)),
        ("Acéptase la renuncia presentada por el doctor X", None),
    ]
    for texto, esperado in vig:
        got = vigencia_desde_texto(texto)
        bien = (got == esperado) if esperado is not None else got is None
        ok += bien
        print(f"  [{'OK' if bien else '✗'}] vigencia: {texto[:55]:55s} → {got.date() if got is not None else None}")
    total = len(casos) + len(vig)
    print(f"{ok}/{total} casos correctos.")
    return 0 if ok == total else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="MIA — Padrón judicial vivo")
    ap.add_argument("--construir", action="store_true", help="crea el padrón base desde el snapshot oficial")
    ap.add_argument("--actualizar", action="store_true", help="aplica altas/bajas del BORA sobre el padrón")
    ap.add_argument("--verbose", action="store_true", help="vuelca columnas y ejemplos del dataset")
    ap.add_argument("--test", action="store_true", help="prueba el matching de órganos y la vigencia (sin red)")
    args = ap.parse_args()
    if args.test:
        return _test()
    if args.construir:
        return construir(verbose=args.verbose)
    if args.actualizar:
        return actualizar()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
