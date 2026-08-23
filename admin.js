/* AZ Turf Pro — Administration v33
 * Authentification serveur unique via X-Admin-Key.
 */
(function () {
  "use strict";

  const KEY_NAMES = [
    "AZ_ADMIN_API_KEY",
    "AZ_TURF_ADMIN_API_KEY",
    "AZ_TURF_ADMIN_KEY",
    "ADMIN_API_KEY",
    "admin_api_key"
  ];

  function getAdminKey() {
    for (const name of KEY_NAMES) {
      const v = sessionStorage.getItem(name) || localStorage.getItem(name) || "";
      if (v.trim()) return v.trim();
    }
    return "";
  }

  function setAdminKey(key) {
    sessionStorage.setItem("AZ_TURF_ADMIN_API_KEY", key);
    localStorage.setItem("AZ_TURF_ADMIN_API_KEY", key);
  }

  function clearAdminKey() {
    for (const name of KEY_NAMES) {
      sessionStorage.removeItem(name);
      localStorage.removeItem(name);
    }
  }

  function adminHeaders() {
    const key = getAdminKey();
    return key ? { "X-Admin-Key": key } : {};
  }

  async function readResponse(response) {
    let data = null;
    try { data = await response.json(); } catch (_) {}
    if (!response.ok) {
      throw new Error(data?.detail || `Erreur serveur (${response.status})`);
    }
    return data;
  }

  async function verifierCleAdmin(key) {
    const response = await fetch("/api/admin/verification", {
      method: "GET",
      headers: { "X-Admin-Key": key },
      cache: "no-store"
    });
    return readResponse(response);
  }

  window.enregistrerCleAdmin = async function () {
    const input = document.getElementById("admin-api-key");
    const state = document.getElementById("etat-cle-admin");
    const key = (input?.value || "").trim();

    if (!key) {
      if (state) state.textContent = "⚠️ Saisissez la clé administrateur.";
      return false;
    }

    if (state) state.textContent = "⏳ Vérification auprès du serveur…";

    try {
      await verifierCleAdmin(key);
      setAdminKey(key);
      if (state) state.textContent = "✅ Clé administrateur validée par le serveur.";
      await window.chargerStatistiquesAdmin();
      await window.chargerAbonnements();
      return true;
    } catch (error) {
      clearAdminKey();
      if (state) state.textContent = `❌ ${error.message}`;
      return false;
    }
  };

  window.chargerStatistiquesAdmin = async function () {
    const key = getAdminKey();
    const apiState = document.getElementById("etat-api");
    if (!key) {
      if (apiState) apiState.textContent = "🔒 Clé administrateur requise";
      return;
    }

    try {
      const response = await fetch("/api/admin/statistiques", {
        headers: adminHeaders(), cache: "no-store"
      });
      const data = await readResponse(response);
      const total = data.total ?? data.total_abonnements ?? data.abonnements ?? 0;
      const actifs = data.actifs ?? data.premium_actifs ?? data.nombre_premium ?? 0;
      const attente = data.attente ?? data.paiements_attente ?? data.en_attente ?? 0;
      const expires = data.expires ?? data.expire ?? data.abonnements_expires ?? 0;

      const put = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.textContent = String(value);
      };
      put("total-abonnements", typeof total === "number" ? total : (data.abonnements_total ?? 0));
      put("nombre-premium", actifs);
      put("paiements-attente", attente);
      put("abonnements-expire", expires);
      if (apiState) apiState.textContent = "✅ Administrateur authentifié";
    } catch (error) {
      if (apiState) apiState.textContent = `❌ ${error.message}`;
    }
  };

  window.chargerAbonnements = async function () {
    const container = document.getElementById("liste-abonnements");
    const key = getAdminKey();
    if (!container || !key) return;

    try {
      const response = await fetch("/api/admin/abonnements", {
        headers: adminHeaders(), cache: "no-store"
      });
      const data = await readResponse(response);
      const items = Array.isArray(data) ? data : (data.abonnements || []);
      if (!items.length) {
        container.textContent = "Aucun abonnement.";
        return;
      }
      container.innerHTML = items.map((a, i) => {
        const tel = a.telephone || a.phone || "—";
        const statut = a.statut || a.status || "—";
        const ref = a.reference || a.reference_paiement || "—";
        return `<div style="padding:10px;border-bottom:1px solid #ddd"><b>${i + 1}. ${String(tel)}</b><br>Statut : ${String(statut)}<br>Référence : ${String(ref)}</div>`;
      }).join("");
    } catch (error) {
      container.textContent = `❌ ${error.message}`;
    }
  };

  window.verifierUtilisateurPremium = async function () {
    const key = getAdminKey();
    const tel = (document.getElementById("telephone-premium")?.value || "").trim();
    const out = document.getElementById("resultat-premium");
    if (!key) { if (out) out.textContent = "🔒 Clé administrateur requise."; return; }
    if (!tel) { if (out) out.textContent = "⚠️ Numéro téléphone obligatoire."; return; }
    try {
      const r = await fetch(`/api/premium/${encodeURIComponent(tel)}`, { cache: "no-store" });
      const d = await readResponse(r);
      if (out) out.textContent = `✅ ${d.statut || d.status || "Abonnement trouvé"}`;
    } catch (e) { if (out) out.textContent = `❌ ${e.message}`; }
  };

  window.activerPremium = async function () {
    const key = getAdminKey();
    const telephone = (document.getElementById("activation-telephone")?.value || "").trim();
    const reference = (document.getElementById("activation-reference")?.value || "").trim();
    const out = document.getElementById("resultat-activation");
    if (!key) { if (out) out.textContent = "🔒 Clé administrateur requise."; return; }
    if (!telephone || !reference) { if (out) out.textContent = "⚠️ Téléphone et référence obligatoires."; return; }
    try {
      const r = await fetch("/api/activation", {
        method: "POST",
        headers: { "Content-Type": "application/json", ...adminHeaders() },
        body: JSON.stringify({ telephone, reference })
      });
      const d = await readResponse(r);
      if (out) out.textContent = `✅ ${d.message || "Premium activé"}`;
      await window.chargerStatistiquesAdmin();
      await window.chargerAbonnements();
    } catch (e) { if (out) out.textContent = `❌ ${e.message}`; }
  };

  window.actualiserAdmin = async function () {
    const key = getAdminKey();
    const state = document.getElementById("etat-cle-admin");
    if (!key) {
      if (state) state.textContent = "⚠️ Saisissez d'abord la clé administrateur serveur.";
      return;
    }
    try {
      await verifierCleAdmin(key);
      if (state) state.textContent = "✅ Clé administrateur validée par le serveur.";
      await Promise.all([window.chargerStatistiquesAdmin(), window.chargerAbonnements()]);
    } catch (e) {
      clearAdminKey();
      if (state) state.textContent = `❌ ${e.message}`;
    }
  };

  document.addEventListener("DOMContentLoaded", () => {
    const key = getAdminKey();
    if (key) window.actualiserAdmin();
  });
})();
