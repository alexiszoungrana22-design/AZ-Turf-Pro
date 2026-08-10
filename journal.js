// =====================================
// AZ TURF PRO - JOURNAL HIPPIQUE
// =====================================

const API_JOURNAL = "https://az-turf-pro.onrender.com/api/journal";
const API_ANALYSE = "https://az-turf-pro.onrender.com/api/analyse";

document.addEventListener("DOMContentLoaded", chargerJournal);

async function chargerJournal(){
    await chargerCourseDuJour();
    await chargerHistoriqueJournal();
    afficherArriveesEtRapports();
}

function texte(v, fallback="-"){
    return v === null || v === undefined || v === "" ? fallback : v;
}

async function chargerCourseDuJour(){
    try{
        const response = await fetch(API_ANALYSE);
        if(!response.ok) throw new Error("API analyse indisponible");
        const data = await response.json();

        const zone = document.getElementById("journal-lonab");
        if(zone){
            zone.innerHTML = `
                <div class="journal-course">
                    <p><strong>Course :</strong> ${texte(data.course)}</p>
                    <p><strong>Date :</strong> ${texte(data.date)}</p>
                    <p><strong>Réunion :</strong> ${texte(data.reunion)}${texte(data.course_numero,"")}</p>
                    <p><strong>Hippodrome :</strong> ${texte(data.hippodrome,"Non communiqué par l'API PMU")}</p>
                    <p><strong>Discipline :</strong> ${texte(data.discipline)}</p>
                    <p><strong>Distance :</strong> ${data.distance ? data.distance+" m" : "-"}</p>
                    <p><strong>Partants :</strong> ${texte(data.partants)}</p>
                    <p><strong>Source :</strong> ${data.source === "pmu_live" ? "PMU réel" : "Démonstration"}</p>
                </div>`;
        }

        const actualites = document.getElementById("actualites-hippiques");
        if(actualites){
            actualites.innerHTML = `
                <ul>
                    <li>🏇 Course suivie : ${texte(data.course)}</li>
                    <li>📊 ${texte(data.partants)} partants analysés</li>
                    <li>⭐ Favori : N°${texte(data.favori?.numero)} ${texte(data.favori?.nom,"")}</li>
                </ul>`;
        }
    }catch(error){
        console.error("Journal course :", error);
    }
}

async function chargerHistoriqueJournal(){
    try{
        const response = await fetch(API_JOURNAL);
        if(!response.ok) throw new Error("Journal indisponible");
        const data = await response.json();

        const analyses = Array.isArray(data.analyses) ? data.analyses : [];
        const zone = document.getElementById("dernieres-arrivees");
        if(zone){
            if(!analyses.length){
                zone.innerHTML = "<p>Aucune analyse enregistrée pour le moment.</p>";
                return;
            }
            zone.innerHTML = analyses.slice(0,10).map(item => {
                const c = item.course || {};
                const classement = Array.isArray(item.classement) ? item.classement : [];
                return `
                <article class="journal-entry">
                    <h3>🏇 ${texte(c.course,"Course analysée")}</h3>
                    <p>📅 ${texte(c.date,item.date_analyse)}</p>
                    <p>📍 ${texte(c.hippodrome,"Hippodrome non communiqué")}</p>
                    <p>${texte(c.reunion,"R?")}${texte(c.course_numero,"")} · ${texte(c.discipline)}</p>
                    <p>👥 ${texte(c.partants,classement.length)} partants</p>
                    <p>⭐ Favori : N°${texte(classement[0]?.numero)} ${texte(classement[0]?.nom,"")}</p>
                </article>`;
            }).join("");
        }
    }catch(error){
        console.error("Journal historique :", error);
        const zone = document.getElementById("dernieres-arrivees");
        if(zone) zone.innerHTML = "<p>Le journal sera alimenté après la prochaine analyse enregistrée.</p>";
    }
}

function afficherArriveesEtRapports(){
    const zone = document.getElementById("rapports-courses");
    if(zone){
        zone.innerHTML = `
            <p>Les résultats et rapports officiels seront affichés dès qu'une source de résultats les fournira.</p>
            <p><strong>Aucun résultat n'est inventé.</strong></p>`;
    }
                                 }
