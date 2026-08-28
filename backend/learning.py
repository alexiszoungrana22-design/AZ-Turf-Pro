"""AZ Turf Pro - gestion robuste de l'historique et réparation PMU."""
from __future__ import annotations
import json
import os
from datetime import datetime
from typing import Any

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORIQUE_FILE = os.path.join(DATA_DIR, "historique_az.json")

def _ensure():
    os.makedirs(DATA_DIR, exist_ok=True)

def _load() -> list[dict]:
    _ensure()
    if not os.path.exists(HISTORIQUE_FILE): return []
    try:
        with open(HISTORIQUE_FILE, "r", encoding="utf-8") as f: data=json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError): return []

def _save(data:list[dict]):
    _ensure()
    tmp=HISTORIQUE_FILE+".tmp"
    with open(tmp,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
    os.replace(tmp,HISTORIQUE_FILE)

def _clean(v:Any)->str:
    return "" if v is None else str(v).strip()

def _course_of(e:dict)->dict:
    c=e.get("course")
    if not isinstance(c,dict): c={}
    return c

def _key(e:dict)->str:
    c=_course_of(e)
    date=_clean(e.get("date") or c.get("date"))
    reunion=_clean(e.get("reunion") or c.get("reunion"))
    num=_clean(e.get("course_numero") or c.get("course_numero"))
    # La clé inclut le nom uniquement si le triplet PMU n'est pas complet.
    if date and reunion and num: return f"{date}|{reunion}|{num}"
    return _clean(e.get("cle")) or ""

def _normalize_entry(e:dict)->dict:
    out=dict(e)
    c=dict(_course_of(e))
    for k in ("date","reunion","course_numero","hippodrome","discipline","heure_depart","distance_course","allocation","source","pmu_id","identifiant_pmu"):
        if k not in c and out.get(k) not in (None, ""): c[k]=out[k]
    for k in ("date","reunion","course_numero","hippodrome","discipline","heure_depart","distance_course","allocation","pmu_id","identifiant_pmu"):
        if out.get(k) in (None, "") and c.get(k) not in (None, ""): out[k]=c[k]
    if out.get("date") and out.get("reunion") and out.get("course_numero"):
        c["date"],c["reunion"],c["course_numero"] = out["date"],out["reunion"],out["course_numero"]
        out["cle_pmu"] = f"{out['date']}|{out['reunion']}|{out['course_numero']}"
    out["course"]=c
    out.setdefault("date_enregistrement", datetime.utcnow().isoformat())
    return out

def lire_historique()->list[dict]: return _load()

def enregistrer_course(data:dict)->dict:
    if not isinstance(data,dict): return {}
    entree=_normalize_entry(data)
    hist=_load(); key=_key(entree)
    idx=next((i for i,x in enumerate(hist) if key and _key(x)==key),-1)
    if idx>=0:
        old=hist[idx]; merged={**old,**entree}
        merged["course"]={**_course_of(old),**_course_of(entree)}
        hist[idx]=_normalize_entry(merged)
    else:
        hist.insert(0,entree)
    _save(hist[:100])
    return hist[0] if idx<0 else hist[idx]

def mettre_a_jour_arrivee(index:int, arrivee:list):
    hist=_load()
    if 0<=index<len(hist):
        hist[index]["arrivee"]=list(arrivee)
        hist[index]["arrivee_officielle"]=list(arrivee)
        hist[index]["statut_resultat"]="TERMINEE"
        _save(hist)
        return True
    return False

def _merge_one(dst:dict, src:dict)->dict:
    dst=dict(dst); src=_normalize_entry(src)
    for k,v in src.items():
        if v not in (None,"",[],{}):
            if k=="course" and isinstance(v,dict): dst[k]={**_course_of(dst),**v}
            elif not dst.get(k): dst[k]=v
    return _normalize_entry(dst)

def fusionner_historique(entrees:list[dict])->bool:
    hist=_load(); changed=False
    for raw in entrees:
        if not isinstance(raw,dict): continue
        e=_normalize_entry(raw); key=_key(e)
        idx=next((i for i,x in enumerate(hist) if key and _key(x)==key),-1)
        if idx>=0:
            new=_merge_one(hist[idx],e)
            if new!=hist[idx]: hist[idx]=new; changed=True
        else:
            hist.insert(0,e); changed=True
    if changed: _save(hist[:100])
    return changed

def reparer_historique()->dict:
    hist=_load(); reparations=0; synchronisables=0; terminees=0; sans_cle=0
    try:
        from pmu_source import recuperer_arrivee_pmu
    except Exception:
        recuperer_arrivee_pmu=None
    for i,raw in enumerate(hist):
        e=_normalize_entry(raw); c=_course_of(e)
        changed=e!=raw
        date=_clean(e.get("date") or c.get("date"))
        reunion=_clean(e.get("reunion") or c.get("reunion"))
        num=_clean(e.get("course_numero") or c.get("course_numero"))
        if date and reunion and num:
            synchronisables += 1
            e["cle_pmu"]=f"{date}|{reunion}|{num}"
            if recuperer_arrivee_pmu and not e.get("arrivee"):
                try:
                    arr=recuperer_arrivee_pmu(date,reunion,num)
                    if arr:
                        e["arrivee"]=arr; e["arrivee_officielle"]=arr; e["statut_resultat"]="TERMINEE"; terminees+=1; changed=True
                except Exception as exc:
                    e["derniere_erreur_sync"]=str(exc); changed=True
        else:
            sans_cle += 1
        if changed: hist[i]=e; reparations += 1
    if reparations: _save(hist[:100])
    return {"status":"success","reparations":reparations,"entrees_synchronisables":synchronisables,"courses_terminees":terminees,"entrees_sans_cle_pmu":sans_cle,"total":len(hist)}

def diagnostic_historique()->dict:
    hist=_load(); sync=0; noid=0; done=0
    for e in hist:
        c=_course_of(e); date=_clean(e.get("date") or c.get("date")); r=_clean(e.get("reunion") or c.get("reunion")); n=_clean(e.get("course_numero") or c.get("course_numero"))
        if e.get("arrivee"): done+=1
        if e.get("pmu_id") or e.get("identifiant_pmu") or (date and r and n): sync+=1
        else: noid+=1
    return {"status":"success","pronostics_enregistres":len(hist),"courses_terminees":done,"courses_en_attente":len(hist)-done,"entrees_synchronisables":sync,"entrees_sans_identifiant_pmu":noid,"methode_secours":"date|reunion|course_numero"}

def enregistrer_pronostic(data): return enregistrer_course(data)
def enregistrer_resultat(data):
    if not isinstance(data,dict): return False
    e=enregistrer_course(data); arr=data.get("arrivee") or data.get("arrivee_officielle")
    if arr:
        hist=_load(); key=_key(e)
        for i,x in enumerate(hist):
            if _key(x)==key: return mettre_a_jour_arrivee(i,arr)
    return bool(e)
def recuperer_historique(cheval_id): return [e for e in _load() if str(cheval_id) in json.dumps(e,ensure_ascii=False)]
