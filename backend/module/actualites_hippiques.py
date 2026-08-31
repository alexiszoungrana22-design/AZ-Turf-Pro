"""Agrégateur léger d'actualités hippiques officielles.
Ne fabrique jamais une actualité : si une source ne répond pas, elle est simplement ignorée.
"""
from __future__ import annotations
import re, time
from datetime import datetime, timezone
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

_CACHE = {"ts": 0.0, "items": []}
TTL = 600
HEADERS = {"User-Agent": "AZ-Turf-Pro/1.0 (+https://az-turf-pro.onrender.com)"}
SOURCES = [
    ("Equidia Régions", "https://regions.equidia.fr/", "https://regions.equidia.fr/"),
    ("LeTROT", "https://www.letrot.com/actualites/642", "https://www.letrot.com/actualites/642"),
]

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def _parse(source_name, url, home):
    r = requests.get(url, headers=HEADERS, timeout=8)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out=[]; seen=set()
    for a in soup.find_all("a", href=True):
        title=_clean(a.get_text(" ", strip=True))
        href=urljoin(url,a["href"])
        low=title.lower()
        if len(title)<18 or href in seen: continue
        if any(x in low for x in ("mentions", "connexion", "recherche", "voir toutes", "tous les")): continue
        if source_name=="Equidia Régions":
            if not any(x in low for x in ("quinté", "quinte", "course", "hippodrome", "cotes", "tuyaux", "analyse", "actualité")): continue
        else:
            if not any(x in low for x in ("prix", "grand", "course", "trot", "meeting", "actualités", "victoire", "analyse")): continue
        seen.add(href)
        out.append({"titre":title,"url":href,"source":source_name})
        if len(out)>=6: break
    return out

def recuperer_actualites(limit=10):
    now=time.time()
    if now-_CACHE["ts"] < TTL and _CACHE["items"]:
        return {"status":"success","source":"cache","actualites":_CACHE["items"][:limit],"horodatage":datetime.now(timezone.utc).isoformat()}
    items=[]; erreurs=[]
    for name,url,home in SOURCES:
        try: items.extend(_parse(name,url,home))
        except Exception as e: erreurs.append({"source":name,"erreur":str(e)})
    # dédoublonnage
    uniq=[]; seen=set()
    for x in items:
        if x["url"] in seen: continue
        seen.add(x["url"]); uniq.append(x)
    _CACHE.update(ts=now,items=uniq)
    return {"status":"success","source":"live" if uniq else "unavailable","actualites":uniq[:limit],"erreurs":erreurs,"horodatage":datetime.now(timezone.utc).isoformat(),"sources": [{"nom":n,"url":u} for n,u,_ in SOURCES]}
