// =====================================
// AZ TURF PRO
// JOURNAL HIPPIQUE
// =====================================

const API_JOURNAL =
"https://az-turf-pro.onrender.com/api/journal";


document.addEventListener(
    "DOMContentLoaded",
    chargerJournal
);

async function chargerJournal(){

    let donneesJournal = null;

    try{

        const reponse =
        await fetch(API_JOURNAL);

        if(reponse.ok){
            donneesJournal = await reponse.json();
        }

    }catch(error){

        console.log("Erreur journal LONAB :", error);

    }

    afficherArrivees(donneesJournal);

    afficherRapports(donneesJournal);

    afficherActualitesHippiques(donneesJournal);

    afficherJournalLonab(donneesJournal);

}


// =====================================
// JOURNAL LONAB DU JOUR
// (programme telechargeable + indices)
// =====================================

function afficherJournalLonab(donneesJournal){

    const zone =
    document.getElementById(
        "journal-lonab"
    );

    if(!zone) return;

    if(!donneesJournal){

        zone.innerHTML = `
            <p>
            📄 Journal hippique bientôt disponible.
            </p>
        `;

        return;

    }

    const entete = donneesJournal.entete || {};
    const synthese = donneesJournal.synthese || {};

    zone.innerHTML = `

    <p>
    🏇 <strong>${entete.libelle_course || "Course du jour"}</strong>
    <br>
    📍 ${entete.hippodrome || "-"}
    ${entete.type_pari ? " — " + entete.type_pari : ""}
    ${entete.distance ? " — " + entete.distance : ""}
    </p>

    ${
    synthese.favoris && synthese.favoris.length
    ? `<p>⭐ <strong>Favoris :</strong> ${synthese.favoris.join(" - ")}</p>`
    : ""
    }

    ${
    synthese.entraineurs_en_forme && synthese.entraineurs_en_forme.length
    ? `<p>🏆 <strong>Entraîneurs en forme :</strong> ${synthese.entraineurs_en_forme.join(", ")}</p>`
    : ""
    }

    ${
    donneesJournal.pdf_url
    ? `<p><a href="${donneesJournal.pdf_url}" target="_blank" class="btn-vip">📄 Télécharger le journal hippique du jour (PDF)</a></p>`
    : ""
    }

    `;

}

function afficherArrivees(donneesJournal){

    const zone =
    document.getElementById(
        "dernieres-arrivees"
    );

    if(!zone) return;

    const actualites =
    donneesJournal && donneesJournal.actualites;

    if(!actualites || !actualites.length){

        zone.innerHTML = `
            <p>
            Les dernières arrivées seront disponibles
            après la publication officielle.
            </p>
        `;

        return;

    }

    zone.innerHTML =

    actualites.map(a => `
        <p>
        🏁 <strong>${a.type_pari}</strong> du ${a.date} :
        ${a.arrivee.join(" - ")}
        </p>
    `).join("");

}

function afficherRapports(donneesJournal){

    const zone =
    document.getElementById(
        "rapports-courses"
    );

    if(!zone) return;

    const masses =
    donneesJournal && donneesJournal.masses_a_partager;

    if(!masses || !masses.length){

        zone.innerHTML = `
            <p>
            Les rapports PMU seront affichés
            après validation des résultats.
            </p>
        `;

        return;

    }

    zone.innerHTML =

    masses.map(m => `
        <p>💰 Masse à partager : <strong>${m}</strong></p>
    `).join("");

}

function afficherActualitesHippiques(donneesJournal){

    const zone =
    document.getElementById(
        "actualites-hippiques"
    );

    if(!zone) return;

    const commentaires =
    donneesJournal && donneesJournal.commentaires_chevaux;

    if(!commentaires || !commentaires.length){
        return;
    }

    zone.innerHTML =

    "<ul>" +

    commentaires.map(c => `
        <li>
        🏇 N°${c.numero} <strong>${c.nom}</strong> :
        ${c.commentaire}
        </li>
    `).join("") +

    "</ul>";

        }
