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

    afficherArrivees();

    afficherRapports();

    await chargerJournalLonab();

}


// =====================================
// JOURNAL LONAB DU JOUR
// (programme telechargeable + indices)
// =====================================

async function chargerJournalLonab(){

    const zone =
    document.getElementById(
        "journal-lonab"
    );

    if(!zone) return;

    try{

        const reponse =
        await fetch(API_JOURNAL);

        if(!reponse.ok){
            throw new Error("Journal indisponible");
        }

        const data =
        await reponse.json();

        const entete = data.entete || {};
        const synthese = data.synthese || {};

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
        data.pdf_url
        ? `<p><a href="${data.pdf_url}" target="_blank" class="btn-vip">📄 Télécharger le journal hippique du jour (PDF)</a></p>`
        : ""
        }

        `;

    }catch(error){

        console.log("Erreur journal LONAB :", error);

        zone.innerHTML = `
            <p>
            📄 Journal hippique bientôt disponible.
            </p>
        `;

    }

}

function afficherArrivees(){

    const zone =
    document.getElementById(
        "dernieres-arrivees"
    );

    if(!zone) return;

    zone.innerHTML = `
        <p>
        Les dernières arrivées seront disponibles
        après la publication officielle.
        </p>
    `;

}

function afficherRapports(){

    const zone =
    document.getElementById(
        "rapports-courses"
    );

    if(!zone) return;

    zone.innerHTML = `
        <p>
        Les rapports PMU seront affichés
        après validation des résultats.
        </p>
    `;

}
