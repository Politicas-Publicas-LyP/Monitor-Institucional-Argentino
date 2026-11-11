"""
MIA — Lectura del Boletín Oficial (BORA) con proxy de Cloudflare como vía alternativa
====================================================================================
Desde 2026-10-22 el BORA (www.boletinoficial.gob.ar) no responde a las IP de los runners
hospedados por GitHub (ConnectTimeout), y el workflow de radares dejó de correr. La solución
es la misma que ya usa el Radar de Desregulación de LyP (repo Seguimiento-Desregulacion): un
Worker de Cloudflare ("bora-proxy-sam") que lee el BORA desde un Durable Object. Cada "lector"
(`?n=lector-K`) es un Durable Object distinto, ubicado por Cloudflare; algunos conectan y otros
no (error 522 tras ~40 s), así que se ROTA entre lectores hasta que uno responde.

Configuración (variables de entorno; en GitHub Actions: Variable + Secret del repo):
    BORA_PROXY_URL    p. ej. https://bora-proxy-sam.politicaspublicas.workers.dev/
    BORA_PROXY_TOKEN  la clave cargada como TOKEN en el Worker (secret; NUNCA va al repo)

Si BORA_PROXY_URL no está definida, se lee el BORA directo (como siempre; sirve desde una
máquina con IP argentina). Si está definida pero ningún lector responde, se intenta UNA lectura
directa corta antes de rendirse. Principio del proyecto: fallar avisando, nunca "sin novedades"
si no se pudo leer el Boletín: `get_bora` devuelve None y el radar lo trata como fallo.

Uso:
    from bora_proxy import get_bora
    r = get_bora(url, HEADERS, timeout=30, intentos=4, espera=8)   # Response | None
    py bora_proxy.py --test     # prueba de la rotación con requests simulado (sin red)
"""
from __future__ import annotations
import os, sys, time
from urllib.parse import urlparse

import requests

HOST_BORA = "www.boletinoficial.gob.ar"
LECTORES = [f"lector-{i}" for i in range(1, 17)]   # en las pruebas de 2026-11-11 ~8 de 16 respondían
LECTORES_POR_URL = 16       # prueba TODOS los lectores por URL: la disponibilidad cambia de a ratos (2026-11-11: 8 seguidos
                            # fallaron en la lista del BORA y minutos después el radar BCRA leyó sin problema)
TIMEOUT_PROXY = 75          # un lector caído tarda ~40 s en dar 522
MAX_URLS_FALLIDAS = 2       # tras N URLs sin ningún lector OK se deja de insistir con el proxy

_estado = {"idx": 0, "urls_fallidas": 0}


def _proxy_url() -> str:
    return (os.environ.get("BORA_PROXY_URL") or "").strip().rstrip("/")


def _es_bora(url: str) -> bool:
    return urlparse(url).hostname == HOST_BORA


def _via_proxy(url: str, headers_extra: dict | None = None):
    """Lee `url` por el Worker, rotando lectores. Devuelve Response o None."""
    base = _proxy_url()
    token = os.environ.get("BORA_PROXY_TOKEN", "")
    if _estado["urls_fallidas"] >= MAX_URLS_FALLIDAS:
        return None   # el proxy viene fallando: no gastar minutos en cada ficha
    h = {"X-Token": token} if token else {}
    for _ in range(min(LECTORES_POR_URL, len(LECTORES))):
        nombre = LECTORES[_estado["idx"]]
        try:
            r = requests.get(base, params={"url": url, "n": nombre}, headers=h, timeout=TIMEOUT_PROXY)
            if r.status_code in (401, 403):
                # Token ausente o incorrecto: rotar de lector no sirve. Avisar claro y devolver.
                print(f"  ❌ Proxy rechazó el pedido ({r.status_code}): revisar BORA_PROXY_TOKEN.")
                return r
            if r.status_code < 500:
                _estado["urls_fallidas"] = 0
                return r
            print(f"  ⚠️  Proxy ({nombre}): status {r.status_code}; pruebo otro lector")
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Proxy ({nombre}): error de red ({e}); pruebo otro lector")
        _estado["idx"] = (_estado["idx"] + 1) % len(LECTORES)
    _estado["urls_fallidas"] += 1
    print(f"  ❌ Ningún lector del proxy pudo leer {url}")
    return None


def get_bora(url: str, headers: dict, timeout: int = 30, intentos: int = 4, espera: int = 8):
    """GET de una URL del BORA: por el proxy si está configurado; si no (o si falla), directo."""
    if _proxy_url() and _es_bora(url):
        r = _via_proxy(url)
        if r is not None:
            return r
        intentos, timeout = 1, min(timeout, 15)   # último recurso: una lectura directa corta
    for i in range(1, intentos + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code < 500:
                return r
        except requests.exceptions.RequestException as e:
            print(f"  red {i}/{intentos}: {e}")
        if i < intentos:
            time.sleep(espera)
    return None


def _test() -> int:
    """Prueba de la rotación con requests.get simulado (sin red)."""
    class R:  # respuesta mínima
        def __init__(self, code): self.status_code = code
    llamadas, plan = [], {}

    def falso_get(url, params=None, headers=None, timeout=None):
        n = (params or {}).get("n", "directo")
        llamadas.append((n, (headers or {}).get("X-Token")))
        v = plan.get(n, 522)
        if v == "boom":
            raise requests.exceptions.ConnectTimeout("simulado")
        return R(v)

    real = requests.get
    requests.get = falso_get
    os.environ["BORA_PROXY_URL"] = "https://proxy.example/"
    os.environ["BORA_PROXY_TOKEN"] = "tok"
    url = f"https://{HOST_BORA}/seccion/primera/20261110"
    ok = 0
    try:
        # 1) lector-1 y -2 caídos (522 / excepción), lector-3 anda → devuelve 200 y manda el token
        _estado.update(idx=0, urls_fallidas=0); llamadas.clear(); plan.update({"lector-1": 522, "lector-2": "boom", "lector-3": 200})
        r = get_bora(url, {})
        c1 = r is not None and r.status_code == 200 and [n for n, _ in llamadas] == ["lector-1", "lector-2", "lector-3"] \
            and all(t == "tok" for _, t in llamadas)
        # 2) la siguiente URL arranca por el último lector que anduvo (lector-3)
        llamadas.clear(); r = get_bora(url, {})
        c2 = r is not None and [n for n, _ in llamadas] == ["lector-3"]
        # 3) token rechazado (403): no rota, devuelve la respuesta para que el radar falle avisando
        _estado.update(idx=0, urls_fallidas=0); llamadas.clear(); plan.clear(); plan["lector-1"] = 403
        r = get_bora(url, {})
        c3 = r is not None and r.status_code == 403 and len(llamadas) == 1
        # 4) ningún lector anda → intenta lectores_por_url y después UNA directa; todo 522 → None
        _estado.update(idx=0, urls_fallidas=0); llamadas.clear(); plan.clear()
        r = get_bora(url, {}, espera=0)
        c4 = r is None and len([n for n, _ in llamadas if n != "directo"]) == LECTORES_POR_URL \
            and [n for n, _ in llamadas].count("directo") == 1
        # 5) una URL que no es del BORA nunca va por el proxy
        llamadas.clear(); plan["directo"] = 200
        r = get_bora("https://example.com/x", {})
        c5 = r is not None and [n for n, _ in llamadas] == ["directo"]
        for i, c in enumerate([c1, c2, c3, c4, c5], 1):
            print(f"  [{'OK' if c else '✗'}] caso {i}")
            ok += bool(c)
    finally:
        requests.get = real
        os.environ.pop("BORA_PROXY_URL", None); os.environ.pop("BORA_PROXY_TOKEN", None)
    print(f"{ok}/5 casos correctos.")
    return 0 if ok == 5 else 1


if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.exit(_test())
    print(__doc__)
