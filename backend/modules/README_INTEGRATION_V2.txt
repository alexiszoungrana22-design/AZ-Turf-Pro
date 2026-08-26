
AZ TURF PRO - EXTENSION EXPERT V2

Installation :

1) Copier engine_expert.py dans backend/modules/

2) Dans chatbot_turf.py ajouter :

from modules.engine_expert import analyser_course_expert

3) Appeler la fonction avant le moteur secours :

analyse = analyser_course_expert(contexte)

Si aucune analyse expert disponible :
continuer avec le moteur existant.

Modules futurs compatibles :
- cotes_history.py
- stats_backtest.py
- meteo_piste.py
- pronos_presse.py

Aucune route API existante n'est modifiée.
