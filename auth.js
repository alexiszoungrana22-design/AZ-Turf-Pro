/* AZ Turf Pro — Accès unifié (admin + premium)
   Point de vérité UNIQUE pour tout le frontend.
   Ne change rien côté backend : réutilise /api/admin/verification,
   l'en-tête X-Admin-Key et les jetons Premium déjà émis par le serveur.
*/
(function (global) {
  "use strict";

  const KEY_ADMIN = "AZ_TURF_ADMIN_KEY";       // sessionStorage — effacée à la fermeture de l'onglet
  const KEY_PREMIUM = "AZ_TURF_PREMIUM_TOKEN"; // localStorage — jeton signé par le serveur (voir security.py)

  // MODE DEV LOCAL UNIQUEMENT — ne s'active jamais en production.
  // Permet de continuer à construire l'app sans être bloqué par la
  // clé admin/premium pendant que tu es en localhost.
  // ⚠️ N'a AUCUN effet sur ton domaine Render réel : les utilisateurs
  // et les vrais abonnés ne sont jamais concernés par ceci.
  function estEnLocal() {
    const h = global.location && global.location.hostname;
    return h === "localhost" || h === "127.0.0.1" || h === "";
  }

  function getAdminKey() {
    return sessionStorage.getItem(KEY_ADMIN) || "";
  }

  function getPremiumToken() {
    return localStorage.getItem(KEY_PREMIUM) || "";
  }

  function setPremiumToken(token) {
    if (token) localStorage.setItem(KEY_PREMIUM, token);
  }

  function clearAccess() {
    sessionStorage.removeItem(KEY_ADMIN);
    localStorage.removeItem(KEY_PREMIUM);
  }

  function hasAccess() {
    if (estEnLocal()) return true;
    return Boolean(getAdminKey() || getPremiumToken());
  }

  function isAdmin() {
    if (estEnLocal()) return true;
    return Boolean(getAdminKey());
  }

  function authHeaders() {
    const adminKey = getAdminKey();
    if (adminKey) return { "X-Admin-Key": adminKey };
    const token = getPremiumToken();
    if (token) return { "Authorization": "Bearer " + token };
    return {};
  }

  // Vérifie la clé admin auprès du serveur AVANT de l'enregistrer.
  // On ne fait jamais confiance à une clé saisie sans validation backend.
  async function loginAdmin(key) {
    try {
      const res = await fetch("/api/admin/verification", {
        headers: { "X-Admin-Key": key || "" }
      });
      if (!res.ok) return false;
      sessionStorage.setItem(KEY_ADMIN, key);
      return true;
    } catch (e) {
      return false;
    }
  }

  global.AZAuth = {
    getAdminKey,
    getPremiumToken,
    setPremiumToken,
    clearAccess,
    hasAccess,
    isAdmin,
    authHeaders,
    loginAdmin
  };
})(window);
