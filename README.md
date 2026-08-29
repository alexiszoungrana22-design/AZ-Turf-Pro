# AZ Turf Pro — Historique v8 / interface Performance

## Installation
Remplacer uniquement à la racine du frontend :
- `historique.html`
- `historique.js`

Le `historique.js` v8 utilise en priorité :
- `GET /api/archive/courses?limit=100`
- `GET /api/archive/performance`

Puis conserve un fallback vers l'ancien `GET /api/historique`, puis le localStorage.

Aucune route API existante n'est supprimée.

## Important
Cette version corrige le problème où l'ancienne page Historique restait affichée : le chargement du panneau Performance est désormais directement intégré à `historique.html` au lieu d'attendre un script externe séparé.
