"""Validation locale sans réseau ni clés IA.
Exécute les contrôles qui garantissent que le moteur et le chatbot peuvent
démarrer avec les données locales.
"""
import compileall
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if not compileall.compile_dir(str(ROOT), quiet=1):
    raise SystemExit("Échec de compilation Python")

import sys
sys.path.insert(0, str(ROOT))
from engine import lancer_analyse
from modules.chatbot_turf import repondre_assistant_turf

data = json.loads((ROOT / "data" / "courses.json").read_text(encoding="utf-8"))
result = lancer_analyse(data["chevaux"], data)
t = result["tickets"]
assert len(t["gratuit"]["quinte"]) == 7
assert len(t["premium"]["quinte"]) == 6
ctx = {"moteur": result, "course": data}
for q in ("bonjour", "donne le quinté premium", "quel est le meilleur duo", "explique le cheval 3"):
    r = repondre_assistant_turf(q, ctx, [])
    assert r.get("status") == "success" and r.get("reponse")
print("AZ TURF PRO : validation locale OK")
print("Classement test :", " - ".join(str(x["numero"]) for x in result["classement"]))
print("Quinté gratuit :", " - ".join(map(str, t["gratuit"]["quinte"])))
print("Quinté Premium :", " - ".join(map(str, t["premium"]["quinte"])))
