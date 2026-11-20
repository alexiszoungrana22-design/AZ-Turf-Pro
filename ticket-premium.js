/* AZ Turf Pro — affichage Premium + tableau des partants Live
   V32 : branche le bouton présent dans ticket-premium.html.
   Le moteur de tickets Premium et les routes backend restent inchangés.
*/
(function () {
  "use strict";

  const API = window.azApiUrl('/api/analyse');
  const API_PARTANTS = window.azApiUrl('/api/partants');

  function el(id) { return document.getElementById(id); }
  function put(id, value, fallback = "Indisponible") {
    const node = el(id);
    if (!node) return;
    node.textContent = value === undefined || value === null || value === ""
      ? fallback
      : String(value);
  }

  function afficherMessageLive(message, erreur = false) {
    let zone = el("message-tableau-live");
    if (!zone) {
      zone = document.createElement("p");
      zone.id = "message-tableau-live";
      zone.setAttribute("role", "status");
      zone.style.cssText = "margin:10px 0;padding:9px 12px;border-radius:8px;";
      const bouton = el("btn-toggle-tableau");
      if (bouton && bouton.parentNode) bouton.parentNode.insertBefore(zone, bouton.nextSibling);
    }
    zone.textContent = message;
    zone.style.color = erreur ? "#991b1b" : "#166534";
    zone.style.background = erreur ? "#fee2e2" : "#dcfce7";
    zone.style.display = message ? "block" : "none";
  }

  function nums(value) {
    if (Array.isArray(value)) {
      return value.map(v => {
        if (Array.isArray(v)) return v.join("-");
        if (v && typeof v === "object") return v.numero ?? v.numPmu ?? v.num ?? v.nom ?? "";
        return v;
      }).filter(v => v !== "");
    }
    if (value && typeof value === "object") {
      if (Array.isArray(value.selection)) return nums(value.selection);
      if (Array.isArray(value.chevaux)) return nums(value.chevaux);
      return [];
    }
    if (typeof value === "string") return value.split(/[\s,-]+/).map(x => x.trim()).filter(Boolean);
    return [];
  }

  function join(value, separator = " - ") {
    const a = nums(value);
    return a.length ? a.join(separator) : "Indisponible";
  }

  function premiumObject(data) {
    const t = data?.tickets || {};
    return t.premium || t.Premium || data?.premium || {};
  }

  function renderTickets(data) {
    const p = premiumObject(data);
    const quinte = p.quinte ?? p.selection_quinte ?? p.quinte_premium ?? p.quintePremium;
    const quarte = p.quarte ?? p.quarte_premium ?? p.quartePremium;
    const trio = p.trio ?? p.trio_premium ?? p.trioPremium;
    const couple = p.couple_gagnant_place ?? p.couple_place ?? p.couple_gagnant ?? p.couple;
    const champ = p.champ_reduit ?? p.champ_reduit_premium ?? p.champReduit;
    const derniere = p.ticket_derniere_minute ?? p.derniere_minute ?? p.derniereMinute;

    put("quinte-premium", join(quinte));
    put("quarte-premium", join(quarte));
    put("trio-premium", join(trio));
    put("selection-premium", join(p.selection_quinte ?? p.selection ?? quinte));

    if (couple && typeof couple === "object" && !Array.isArray(couple)) {
      const gagnant = nums(couple.gagnant || couple.couple_gagnant || couple.selection);
      const place = nums(couple.place || couple.couple_place);
      const parts = [];
      if (gagnant.length) parts.push("Gagnant : " + gagnant.join(" - "));
      if (place.length) parts.push("Placé : " + place.join(" - "));
      put("couple-premium", parts.join(" | ") || join(couple));
    } else put("couple-premium", join(couple));

    if (champ && typeof champ === "object" && !Array.isArray(champ)) {
      const format = champ.format || champ.selection || champ.bases;
      put("champ-reduit-premium", Array.isArray(format) ? format.join(" - ") : format);
    } else put("champ-reduit-premium", join(champ));

    if (derniere && typeof derniere === "object") {
      const selection = nums(derniere.selection || derniere.quinte || derniere.chevaux);
      const joker = derniere.joker;
      let text = selection.length ? selection.join(" - ") : "";
      if (joker !== undefined && joker !== null && joker !== "") text += (text ? " | " : "") + "Joker : " + joker;
      put("derniere-minute-premium", text);
    } else put("derniere-minute-premium", join(derniere));

    const explication = p.lecture_course || p.explication || p.methode || data?.explication_premium;
    if (explication && typeof explication === "object") {
      const points = [explication.methode, explication.lecture,
        ...(Array.isArray(explication.points_forts) ? explication.points_forts.map(x => "✅ " + x) : []),
        ...(Array.isArray(explication.points_attention) ? explication.points_attention.map(x => "⚠️ " + x) : [])].filter(Boolean);
      put("explication-premium", points.join("\n") || "Analyse Premium disponible.");
    } else put("explication-premium", explication || "Analyse Premium disponible.");

    const lecture = p.lecture_course || data?.lecture_course || data?.analyse_premium;
    if (lecture && typeof lecture === "object") {
      const lines = [];
      if (lecture.profil?.discipline) lines.push("Discipline : " + lecture.profil.discipline);
      if (lecture.profil?.distance) lines.push("Distance : " + lecture.profil.distance + " m");
      if (lecture.profil?.partants) lines.push("Partants : " + lecture.profil.partants);
      if (lecture.profil?.confiance !== undefined) lines.push("Confiance : " + lecture.profil.confiance);
      if (Array.isArray(lecture.points_forts)) lines.push("Points forts : " + lecture.points_forts.join(" ; "));
      if (Array.isArray(lecture.points_attention)) lines.push("Points d'attention : " + lecture.points_attention.join(" ; "));
      put("analyse-premium", lines.join("\n") || "Analyse Premium disponible.");
    } else put("analyse-premium", lecture || "Analyse Premium disponible.");

    put("message-premium", p.message_fin || p.message || data?.message_premium ||
      "🍀 Bonne chance ! Les tickets Premium sont générés séparément du ticket gratuit.");
  }

  function renderPartants(data) {
    const body = el("all-horses");
    if (!body) return;
    const horses = Array.isArray(data) ? data :
      (data?.partants || data?.partants_complets || data?.chevaux || data?.classement || []);
    if (!Array.isArray(horses) || !horses.length) {
      body.innerHTML = '<tr><td colspan="6">Aucun partant disponible pour le moment.</td></tr>';
      return false;
    }
    body.innerHTML = "";
    horses.forEach((h, index) => {
      const row = document.createElement("tr");
      const values = [h.rang ?? h.position ?? index + 1, h.numero ?? h.numPmu ?? h.num ?? "—",
        h.nom ?? h.cheval ?? "—", h.indice_az ?? h.indice ?? "—",
        h.confiance ?? "—", h.cote_brute ?? h.cote ?? h.tendance ?? "—"];
      values.forEach(value => {
        const cell = document.createElement("td");
        cell.style.padding = "10px";
        cell.textContent = value === null || value === undefined || value === "" ? "—" : String(value);
        row.appendChild(cell);
      });
      body.appendChild(row);
    });
    return true;
  }

  async function obtenirAccesTableau() {
    if (!window.AZAuth) {
      afficherMessageLive("Module de sécurité indisponible. Rechargez la page.", true);
      return false;
    }
    if (window.AZAuth.getPremiumToken()) return true;

    const key = window.AZAuth.getAdminKey();
    if (key) {
      try {
        const response = await fetch(window.azApiUrl('/api/admin/verification'), {
          method: "GET", cache: "no-store",
          headers: { "X-Admin-Key": key, "Accept": "application/json" }
        });
        if (response.ok) return true;
      } catch (_) {
        afficherMessageLive("Impossible de vérifier l'accès administrateur. Vérifiez votre connexion.", true);
        return false;
      }
    }

    const entered = window.prompt("Accès administrateur requis. Entrez votre clé administrateur AZ Turf Pro :");
    if (!entered || !entered.trim()) {
      afficherMessageLive("Connexion annulée. Le tableau Live reste protégé.", true);
      return false;
    }
    afficherMessageLive("Vérification de la clé administrateur…");
    const ok = await window.AZAuth.loginAdmin(entered.trim());
    if (!ok) afficherMessageLive("Clé administrateur incorrecte ou serveur indisponible.", true);
    return ok;
  }

  async function chargerTableauLive() {
    const body = el("all-horses");
    if (!body) throw new Error("Zone du tableau des partants introuvable.");
    body.innerHTML = '<tr><td colspan="6">Chargement des partants…</td></tr>';
    const response = await fetch(API_PARTANTS + "?t=" + Date.now(), {
      method: "GET", cache: "no-store",
      headers: { "Accept": "application/json", ...window.AZAuth.authHeaders() }
    });
    if (!response.ok) {
      let detail = "";
      try { const error = await response.json(); detail = error.detail || error.message || ""; } catch (_) {}
      throw new Error(detail || "Erreur de chargement des partants (HTTP " + response.status + ").");
    }
    const data = await response.json();
    if (!renderPartants(data)) throw new Error("Le serveur n'a retourné aucun partant.");
    afficherMessageLive("Tableau Live chargé.");
  }

  async function load() {
    try {
      const response = await fetch(API + "?t=" + Date.now(), {
        cache: "no-store",
        headers: { "Accept": "application/json", ...window.AZAuth.authHeaders() }
      });
      if (!response.ok) throw new Error("API analyse indisponible (" + response.status + ")");
      const data = await response.json();
      renderTickets(data);
      if (!el("all-horses")?.children.length) renderPartants(data);
      put("meta-course", data.course || "");
      put("meta-hippodrome", data.hippodrome || "");
      put("meta-discipline", data.discipline || "");
      put("meta-distance", data.distance ? data.distance + " m" : "");
      put("meta-partants", data.partants || "");
    } catch (error) {
      console.error("AZ Premium :", error);
      put("quinte-premium", "Données Premium indisponibles");
      put("quarte-premium", "Données Premium indisponibles");
      put("trio-premium", "Données Premium indisponibles");
      put("couple-premium", "Données Premium indisponibles");
      put("champ-reduit-premium", "Données Premium indisponibles");
      put("derniere-minute-premium", "Données Premium indisponibles");
      put("analyse-premium", "Impossible de charger l'analyse Premium.");
      put("message-premium", "Vérifiez la connexion au serveur.");
    }
  }

  function initAcces() {
    const messageBlocage = el("message-blocage");
    const contenuPremium = el("contenu-premium");
    if (!window.AZAuth || !window.AZAuth.hasAccess()) {
      if (contenuPremium) contenuPremium.classList.add("zone-masquee");
      if (messageBlocage) messageBlocage.style.display = "";
    } else {
      if (messageBlocage) messageBlocage.style.display = "none";
      if (contenuPremium) contenuPremium.classList.remove("zone-masquee");
      load();
    }

    // IMPORTANT : le bouton visible sur ticket-premium.html est piloté ici.
    const button = el("btn-toggle-tableau");
    const container = el("conteneur-tableau");
    if (!button || !container) return;
    button.disabled = false;
    button.addEventListener("click", async function () {
      if (!container.classList.contains("zone-masquee")) {
        container.classList.add("zone-masquee");
        button.textContent = "📊 Afficher le Tableau des Partants (Live)";
        return;
      }
      button.disabled = true;
      try {
        const allowed = await obtenirAccesTableau();
        if (!allowed) return;
        await chargerTableauLive();
        container.classList.remove("zone-masquee");
        button.textContent = "❌ Masquer le Tableau Live";
      } catch (error) {
        console.error("Tableau des partants Live :", error);
        const body = el("all-horses");
        if (body) body.innerHTML = '<tr><td colspan="6">' +
          String(error.message || "Données indisponibles.").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])) +
          '</td></tr>';
        afficherMessageLive(error.message || "Impossible de charger le tableau Live.", true);
      } finally {
        button.disabled = false;
      }
    });
  }

  document.addEventListener("DOMContentLoaded", initAcces);
  window.azPremiumReload = load;
})();
