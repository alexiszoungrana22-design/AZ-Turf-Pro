import json
import os

PATH=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'v25_learning.json')

def enregistrer_pronostic(data):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    items=[]
    if os.path.exists(PATH):
        try:
            with open(PATH,'r',encoding='utf-8') as f: items=json.load(f)
        except Exception: items=[]
    items.append(data)
    with open(PATH,'w',encoding='utf-8') as f: json.dump(items,f,ensure_ascii=False,indent=2)
    return True
