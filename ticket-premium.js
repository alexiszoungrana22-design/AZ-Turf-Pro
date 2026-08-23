/* AZ Turf Pro — affichage Premium robuste v25
   Ne modifie pas le moteur Premium. Lit /api/analyse et normalise
   les différentes formes de tickets retournées par le backend.
*/
(function () {
  "use strict";

  const API = "/api/premium/ticket";
  const ABS_API = "https://az-turf-pro.onrender.com/api/premium/ticket";

  function el(id) { return document.getElementById(id); }

  function put(id, value, fallback = "Indisponible") {
    const node = el(id);
    if (!node) return;
    node.textContent = value === undefined || value === null || value === ""
      ? fallback
      : String(value);
  }

  function nums(value) {
    if (Array.isArray(value)) {
      return value.map(v => {
        if (v && typeof v === "object") return v.numero ?? v.numPmu ?? v.num ?? v.nom ?? "";
        return v;
      }).filter(v => v !== "");
    }
    if (value && typeof value === "object") {
      if (Array.isArray(value.selection)) return nums(value.selection);
      if (Array.isArray(value.chevaux)) return nums(value.chevaux);
      return [];
    }
    if (typeof value === "string") {
      return value.split(/[\s,-]+/).map(x => x.trim()).filter(Boolean);
    }
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

    const quinte =
      p.quinte ??
      p.selection_quinte ??
      p.quinte_premium ??
      p.quintePremium;

    const quarte =
      p.quarte ??
      p.quarte_premium ??
      p.quartePremium;

    const trio =
      p.trio ??
      p.trio_premium ??
      p.trioPremium;

    const couple =
      p.couple_gagnant_place ??
      p.couple_place ??
      p.couple_gagnant ??
      p.couple;

    const champ =
      p.champ_reduit ??
      p.champ_reduit_premium ??
      p.champReduit;

    const derniere =
      p.ticket_derniere_minute ??
      p.derniere_minute ??
      p.derniereMinute;

    put("quinte-premium", join(quinte));
    put("quarte-premium", join(quarte));
    put("trio-premium", join(trio));

    if (couple && typeof couple === "object" && !Array.isArray(couple)) {
      const gagnant = nums(couple.gagnant || couple.couple_gagnant || couple.selection);
      const place = nums(couple.place || couple.couple_place);
      const parts = [];
      if (gagnant.length) parts.push("Gagnant : " + gagnant.join(" - "));
      if (place.length) parts.push("Placé : " + place.join(" - "));
      put("couple-premium", parts.join(" | ") || join(couple));
    } else {
      put("couple-premium", join(couple));
    }

    if (champ && typeof champ === "object" && !Array.isArray(champ)) {
      const format = champ.format || champ.selection || champ.bases;
      put("champ-reduit-premium", Array.isArray(format) ? format.join(" - ") : format);
    } else {
      put("champ-reduit-premium", join(champ));
    }

    if (derniere && typeof derniere === "object") {
      const selection = nums(derniere.selection || derniere.quinte || derniere.chevaux);
      const joker = derniere.joker;
      let text = selection.length ? selection.join(" - ") : "";
      if (joker !== undefined && joker !== null && joker !== "") {
        text += (text ? " | " : "") + "Joker : " + joker;
      }
      put("derniere-minute-premium", text);
    } else {
      put("derniere-minute-premium", join(derniere));
    }

    const explication =
      p.lecture_course ||
      p.explication ||
      p.methode ||
      data?.explication_premium;

    if (explication && typeof explication === "object") {
      const points = [
        explication.methode,
        explication.lecture,
        ...(Array.isArray(explication.points_forts) ? explication.points_forts.map(x => "✅ " + x) : []),
        ...(Array.isArray(explication.points_attention) ? explication.points_attention.map(x => "⚠️ " + x) : [])
      ].filter(Boolean);
      put("explication-premium", points.join("\n") || "Analyse Premium disponible.");
    } else {
      put("explication-premium", explication || "Analyse Premium disponible.");
    }

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
    } else {
      put("analyse-premium", lecture || "Analyse Premium disponible.");
    }

    put("message-premium",
      p.message_fin ||
      p.message ||
      data?.message_premium ||
      "🍀 Bonne chance ! Les tickets Premium sont générés séparément du ticket gratuit."
    );
  }

  function renderPartants(data) {
    const body = el("all-horses");
    if (!body) return;

    const horses = data?.partants_complets || data?.chevaux || data?.classement || [];
    if (!Array.isArray(horses) || !horses.length) {
      body.innerHTML = '<tr><td colspan="6">Partants indisponibles.</td></tr>';
      return;
    }

    body.innerHTML = horses.map(h => {
      const numero = h.numero ?? h.numPmu ?? "-";
      const nom = h.nom ?? "-";
      const indice = h.indice_az ?? "-";
      const confiance = h.confiance ?? "-";
      const cote = h.cote_brute ?? h.cote ?? "-";
      return `<tr>
        <td style="padding:10px">${h.rang ?? "-"}</td>
        <td style="padding:10px"><strong>${numero}</strong></td>
        <td style="padding:10px">${nom}</td>
        <td style="padding:10px">${indice}</td>
        <td style="padding:10px">${confiance}</td>
        <td style="padding:10px">${cote}</td>
      </tr>`;
    }).join("");
  }

  async function load() {
    try {
      const headers = { "Accept": "application/json" };
      const adminKey =
        sessionStorage.getItem("AZ_TURF_ADMIN_API_KEY") ||
        localStorage.getItem("AZ_TURF_ADMIN_API_KEY") ||
        sessionStorage.getItem("AZ_TURF_ADMIN_KEY") ||
        localStorage.getItem("AZ_TURF_ADMIN_KEY") ||
        sessionStorage.getItem("ADMIN_API_KEY") ||
        localStorage.getItem("ADMIN_API_KEY") ||
        sessionStorage.getItem("admin_api_key") ||
        localStorage.getItem("admin_api_key") ||
        "";
      const token =
        localStorage.getItem("AZ_TURF_PREMIUM_TOKEN") ||
        sessionStorage.getItem("AZ_TURF_PREMIUM_TOKEN") ||
        "";

      if (adminKey) headers["X-Admin-Key"] = adminKey;
      else if (token) headers["Authorization"] = `Bearer ${token}`;

      const response = await fetch(API + "?t=" + Date.now(), {
        cache: "no-store",
        headers
      });

      if (!response.ok) {
        // Même domaine Render : second essai absolu.
        const retry = await fetch(ABS_API + "?t=" + Date.now(), {
          cache: "no-store",
          headers
        });
        if (!retry.ok) throw new Error("API analyse indisponible (" + retry.status + ")");
        render(await retry.json());
        return;
      }

      render(await response.json());
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

  function render(data) {
    const blocage = el("message-blocage");
    const contenu = el("contenu-premium");
    if (blocage) blocage.style.display = "none";
    if (contenu) contenu.classList.remove("zone-masquee");
    renderTickets(data);
    renderPartants(data);

    put("meta-course", data.course || "");
    put("meta-hippodrome", data.hippodrome || "");
    put("meta-discipline", data.discipline || "");
    put("meta-distance", data.distance ? data.distance + " m" : "");
    put("meta-partants", data.partants || "");
  }

  document.addEventListener("DOMContentLoaded", load);
  window.azPremiumReload = load;
})();
