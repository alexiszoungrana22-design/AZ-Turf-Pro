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
            ðŸ“„ Journal hippique bientÃ´t disponible.
            </p>
        `;

        return;

    }

    const entete = donneesJournal.entete || {};
    const synthese = donneesJournal.synthese || {};

    zone.innerHTML = `

    <p>
    ðŸ‡ <strong>${entete.libelle_course || "Course du jour"}</strong>
    <br>
    ðŸ“ ${entete.hippodrome || "-"}
    ${entete.type_pari ? " â€” " + entete.type_pari : ""}
    ${entete.distance ? " â€” " + entete.distance : ""}
    </p>

    ${
    synthese.favoris && synthese.favoris.length
    ? `<p>â­ <strong>Favoris :</strong> ${synthese.favoris.join(" - ")}</p>`
    : ""
    }

    ${
    synthese.entraineurs_en_forme && synthese.entraineurs_en_forme.length
    ? `<p>ðŸ† <strong>EntraÃ®neurs en forme :</strong> ${synthese.entraineurs_en_forme.join(", ")}</p>`
    : ""
    }

    ${
    donneesJournal.pdf_url
    ? `<p><a href="${donneesJournal.pdf_url}" target="_blank" class="btn-vip">ðŸ“„ TÃ©lÃ©charger le journal hippique du jour (PDF)</a></p>`
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
            Les derniÃ¨res arrivÃ©es seront disponibles
            aprÃ¨s la publication officielle.
            </p>
        `;

        return;

    }

    zone.innerHTML =

    actualites.map(a => `
        <p>
        ðŸ <strong>${a.type_pari}</strong> du ${a.date} :
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
            Les rapports PMU seront affichÃ©s
            aprÃ¨s validation des rÃ©sultats.
            </p>
        `;

        return;

    }

    zone.innerHTML =

    masses.map(m => `
        <p>ðŸ’° Masse Ã  partager : <strong>${m}</strong></p>
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
        ðŸ‡ NÂ°${c.numero} <strong>${c.nom}</strong> :
        ${c.commentaire}
        </li>
    `).join("") +

    "</ul>";

}
