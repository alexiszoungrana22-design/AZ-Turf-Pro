/**
 * AZ Turf Pro - Historique des analyses et arrivées
 * Affichage robuste des anciennes et nouvelles structures de données.
 */

const HISTORIQUE_STORAGE_KEY = "AZ_TURF_HISTORIQUE_COURSES_V1";
const API_HISTORIQUE = "/api/historique";

document.addEventListener("DOMContentLoaded", () => {
    afficherPageHistorique();
});

function lireLocal() {
    try {
        const valeur = JSON.parse(localStorage.getItem(HISTORIQUE_STORAGE_KEY) || "[]");
        return Array.isArray(valeur) ? valeur : [];
    } catch (e) {
        return [];
    }
}

function texte(valeur, fallback = "") {
    if (valeur === null || valeur === undefined) return fallback;
    if (typeof valeur === "string" || typeof valeur === "number") return String(valeur);
    return fallback;
}

function numeroCheval(valeur) {
    if (valeur && typeof valeur === "object") return texte(valeur.numero, "");
    return texte(valeur, "");
}

function nomCheval(valeur) {
    if (valeur && typeof valeur === "object") {
        const nom = texte(valeur.nom || valeur.name, "");
        const numero = numeroCheval(valeur);
        if (numero && nom) return `N°${numero} ${nom}`;
        if (numero) return `N°${numero}`;
        if (nom) return nom;
    }
    return texte(valeur, "-");
}

function valeurListe(valeur) {
    if (!Array.isArray(valeur)) return [];
    return valeur.map(item => {
        if (item && typeof item === "object") return numeroCheval(item) || nomCheval(item);
        return texte(item, "");
    }).filter(Boolean);
}

function extraireNomCourse(courseInfo, entree) {
    if (courseInfo && typeof courseInfo === "object") {
        const direct = [
            courseInfo.nom,
            courseInfo.nom_course,
            courseInfo.nom_prix,
            courseInfo.prix,
            courseInfo.libelle,
            courseInfo.course
        ];
        for (const valeur of direct) {
            if (typeof valeur === "string" && valeur.trim()) return valeur.trim();
            if (valeur && typeof valeur === "object") {
                const nom = valeur.nom || valeur.libelle || valeur.name;
                if (typeof nom === "string" && nom.trim()) return nom.trim();
            }
        }
    }
    for (const valeur of [entree?.nom, entree?.nom_course, entree?.libelle]) {
        if (typeof valeur === "string" && valeur.trim()) return valeur.trim();
    }
    return "Course";
}

function formaterDate(valeur) {
    if (!valeur) return "-";
    const brut = String(valeur).trim();

    // Format PMU compact : 21082026 -> 21/08/2026
    if (/^\d{8}$/.test(brut)) {
        return `${brut.slice(0, 2)}/${brut.slice(2, 4)}/${brut.slice(4)}`;
    }

    const dt = new Date(brut.replace(" ", "T"));
    if (!Number.isNaN(dt.getTime())) {
        const date = dt.toLocaleDateString("fr-FR");
        const heure = dt.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
        return `${date} ${heure}`;
    }

    return brut;
}

function normaliserEntree(c) {
    if (!c || typeof c !== "object") return null;

    const tickets = c.tickets && typeof c.tickets === "object" ? c.tickets : {};
    const gratuit = tickets.gratuit && typeof tickets.gratuit === "object" ? tickets.gratuit : {};
    const premium = tickets.premium && typeof tickets.premium === "object" ? tickets.premium : {};
    const courseInfo = c.course && typeof c.course === "object" ? c.course : {};

    const classement = Array.isArray(c.classement) ? c.classement : [];
    const selection = c.selection_az ?? gratuit.quinte ?? c.selection ?? [];
    const selectionPremium = c.selection_premium ?? premium.selection_quinte ?? premium.quinte ?? [];
    const arriveeBrute = c.arrivee_quinte ?? c.arrivee ?? [];
    const arrivee = valeurListe(arriveeBrute).slice(0, 5);

    const favoriBrut = c.favori ?? (classement.length ? classement[0] : "-");
    const favori = nomCheval(favoriBrut);

    const dateBrute = c.date || courseInfo.date || c.date_analyse || "";
    const reunion = texte(c.reunion || courseInfo.reunion || courseInfo.reunion_numero, "");
    const numero = texte(c.course_numero || courseInfo.course_numero || courseInfo.numero_course, "");

    // Les anciennes entrées sans aucune identité de course sont ignorées.
    const identiteValide = Boolean(
        reunion || numero ||
        (courseInfo && Object.keys(courseInfo).length) ||
        c.hippodrome || c.nom || c.nom_course
    );
    if (!identiteValide) return null;

    return {
        date: formaterDate(dateBrute),
        dateBrute,
        reunion,
        numero,
        course: extraireNomCourse(courseInfo, c),
        hippodrome: texte(courseInfo.hippodrome || c.hippodrome, ""),
        favori,
        selection: valeurListe(selection),
        selectionPremium: valeurListe(selectionPremium),
        arrivee,
        statut: arrivee.length >= 5 ? "ARRIVÉE OFFICIELLE" : "EN ATTENTE"
    };
}

async function chargerHistorique() {
    try {
        const r = await fetch(API_HISTORIQUE, { cache: "no-store" });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const data = await r.json();
        const liste = Array.isArray(data.historique) ? data.historique : [];
        if (liste.length) {
            try {
                localStorage.setItem(HISTORIQUE_STORAGE_KEY, JSON.stringify(liste));
            } catch (e) {}
            return liste.map(normaliserEntree).filter(Boolean);
        }
    } catch (e) {
        console.warn("Historique API indisponible, utilisation locale", e);
    }

    return lireLocal().map(normaliserEntree).filter(Boolean);
}

function eliminerDoublons(liste) {
    const coursesVues = new Set();
    return liste.filter(c => {
        const date = c.dateBrute || c.date || "";
        const identifiant = `${date}-${c.reunion}-${c.numero}-${c.course}`;
        if (coursesVues.has(identifiant)) return false;
        coursesVues.add(identifiant);
        return true;
    });
}

function echapperHTML(valeur) {
    return String(valeur ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function afficherPageHistorique() {
    const tbody = document.getElementById("historique-body") || document.getElementById("historique-table-body");
    const container = document.getElementById("historique-container");
    if (!tbody && !container) return;

    chargerHistorique().then(listeBrute => {
        const liste = eliminerDoublons(listeBrute);

        if (tbody) {
            tbody.innerHTML = "";
            if (!liste.length) {
                tbody.innerHTML = '<tr><td colspan="5">Aucune course enregistrée pour le moment.</td></tr>';
                return;
            }

            liste.forEach(c => {
                const selection = c.selection.length ? c.selection.join(" - ") : (c.selectionPremium.length ? c.selectionPremium.join(" - ") : "-");
                const arrivee = c.arrivee.length ? c.arrivee.join(" - ") : "En attente";
                const affichageReunion = c.numero ? `${c.reunion || ""} N°${c.numero}`.trim() : (c.reunion || "Course");
                const nomCourse = echapperHTML(c.course);
                const hippo = c.hippodrome ? `<br><small>${echapperHTML(c.hippodrome)}</small>` : "";

                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${echapperHTML(c.date)}</td>
                    <td><strong>${echapperHTML(affichageReunion)}</strong><br>${nomCourse}${hippo}</td>
                    <td><strong style="color:#08783f;">${echapperHTML(c.favori)}</strong></td>
                    <td><strong style="color:#b8860b;letter-spacing:1px;">${echapperHTML(selection)}</strong></td>
                    <td><strong class="badge-arrivee">${echapperHTML(arrivee)}</strong></td>`;
                tbody.appendChild(tr);
            });
        } else if (container) {
            container.innerHTML = liste.map(c => {
                const selection = c.selection.length ? c.selection.join(" - ") : (c.selectionPremium.length ? c.selectionPremium.join(" - ") : "-");
                return `
                    <article class="historique-card">
                        <h3>${echapperHTML(c.reunion)} ${c.numero ? `N°${echapperHTML(c.numero)}` : ""} - ${echapperHTML(c.course)}</h3>
                        <p>${echapperHTML(c.hippodrome || "Hippodrome non disponible")}</p>
                        <p><strong>Date :</strong> ${echapperHTML(c.date)}</p>
                        <p><strong>Favori :</strong> ${echapperHTML(c.favori)}</p>
                        <p><strong>Sélection Premium AZ :</strong> ${echapperHTML(selection)}</p>
                        <p><strong>Arrivée officielle :</strong> ${echapperHTML(c.arrivee.join(" - ") || "En attente")}</p>
                    </article>`;
            }).join("");
        }
    });
}

function reinitialiserHistorique() {
    if (confirm("Voulez-vous vraiment effacer tout l'historique local ?")) {
        localStorage.removeItem(HISTORIQUE_STORAGE_KEY);
        afficherPageHistorique();
    }
}
