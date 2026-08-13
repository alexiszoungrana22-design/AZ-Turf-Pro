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
    const plusJoues = donneesJournal.plus_joues || [];

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

    ${plusJoues.length ? `<p>🔥 <strong>Plus joués LONAB :</strong> ${plusJoues.join(" - ")}</p>` : ""}

    ${
    synthese.entraineurs_en_forme && synthese.entraineurs_en_forme.length
    ? `<p>🏆 <strong>Entraîneurs en forme :</strong> ${synthese.entraineurs_en_forme.join(", ")}</p>`
    : ""
    }

    ${donneesJournal.pdf_url ? `<p><a href="${donneesJournal.pdf_url}" target="_blank" class="btn-vip">📄 Télécharger le journal hippique du jour (PDF)</a></p>` : ""}
    ${donneesJournal.pdf_resultats_url ? `<p><a href="${donneesJournal.pdf_resultats_url}" target="_blank" class="btn-vip">💰 Télécharger les résultats et rapports LONAB (PDF)</a></p>` : ""}

    `;

}

function afficherArrivees(donneesJournal){const zone=document.getElementById("dernieres-arrivees");if(!zone)return;const r=donneesJournal?.resultats||donneesJournal?.actualites||[];if(!r.length){zone.innerHTML="<p>Les résultats officiels LONAB seront affichés dès leur publication.</p>";return;}zone.innerHTML=r.map(x=>`<div class="resultat-lonab"><strong>🏁 ${x.type_pari||"Résultat PMU'B"}</strong>${x.date?" — "+x.date:""}<br><span>${Array.isArray(x.arrivee)?x.arrivee.join(" - "):x.texte||"-"}</span></div>`).join("");}
function afficherRapports(donneesJournal){const zone=document.getElementById("rapports-courses");if(!zone)return;const r=donneesJournal?.rapports||[],m=donneesJournal?.masses_a_partager||[];if(!r.length&&!m.length){zone.innerHTML="<p>Les rapports LONAB seront affichés après leur publication officielle.</p>";return;}zone.innerHTML=[...r.map(x=>`<p>💰 ${x}</p>`),...m.map(x=>`<p>💰 Masse à partager : <strong>${x}</strong></p>`)].join("");}

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
