# Historique AZ Turf sans disque Render payant

## Fonctionnement

Le serveur continue d'enregistrer `backend/data/historique_az.json` comme avant.
En plus, chaque réponse de `/api/analyse` est sauvegardée dans le navigateur
(`localStorage`) sous `AZ_TURF_HISTORIQUE_COURSES_V1`.

Après un redémarrage/re-déploiement Render, `historique.js` envoie automatiquement
la copie locale vers `/api/historique/synchroniser`, qui fusionne les courses
sans doublons dans l'historique serveur.

## Limite honnête

Cette solution ne remplace pas un stockage persistant global : elle protège
l'historique pour le même navigateur/appareil tant que son stockage local n'est
pas effacé. Elle ne garantit pas une synchronisation multi-appareils.

Quand un stockage persistant sera disponible, définir `HISTORIQUE_DATA_DIR`
vers son répertoire monté. Aucun changement de logique métier ne sera nécessaire.
