// =====================================
// AZ TURF PRO
// JOURNAL HIPPIQUE
// =====================================

document.addEventListener(
    "DOMContentLoaded",
    chargerJournal
);

function chargerJournal(){

    afficherArrivees();

    afficherRapports();

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
