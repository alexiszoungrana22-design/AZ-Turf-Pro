# Panneau Performance AZ — Historique

Patch additif pour afficher les performances de l'archive dans `historique.html`.

## Installation

Ajouter dans `<head>` de `historique.html` :

```html
<link rel="stylesheet" href="historique-performance.css?v=1">
```

Ajouter avant `</body>` :

```html
<script src="historique-performance.js?v=1"></script>
```

Le panneau se crée automatiquement dans `<main>` et appelle :

`GET /api/archive/performance`

Aucune route historique existante n'est supprimée ou remplacée.

## Important

Le script accepte `window.AZ_API_BASE` si le frontend est hébergé sur un domaine différent du backend. Sinon il utilise le même domaine que la page.
