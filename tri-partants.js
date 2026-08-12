// =====================================
// MODULE INDEPENDANT : TRI DES PARTANTS
// =====================================

document.addEventListener("DOMContentLoaded", () => {
    // Attendre un court instant que l'accueil ait fini de charger le tableau
    setTimeout(initialiserFiltresTri, 800);
});

function initialiserFiltresTri() {
    const tableau = document.getElementById("all-horses") || document.getElementById("corps-tableau-partants");
    if (!tableau) return;

    // Creer une barre de boutons de tri au-dessus du tableau si elle n'existe pas deja
    const parentTable = tableau.closest("table") || tableau.parentElement;
    if (!document.getElementById("barre-tri-partants")) {
        const barreTri = document.createElement("div");
        barreTri.id = "barre-tri-partants";
        barreTri.style.cssText = "margin-bottom: 12px; display: flex; gap: 8px; flex-wrap: wrap;";
        barreTri.innerHTML = `
            <button id="btn-tri-numero" class="btn-tri" style="padding: 6px 12px; font-size: 12px; cursor: pointer;">Trier par Numero</button>
            <button id="btn-tri-cote" class="btn-tri" style="padding: 6px 12px; font-size: 12px; cursor: pointer;">Trier par Cote</button>
        `;
        parentTable.before(barreTri);

        // Evenements sur les boutons
        document.getElementById("btn-tri-numero").addEventListener("click", () => trierTableauPar("numero"));
        document.getElementById("btn-tri-cote").addEventListener("click", () => trierTableauPar("cote"));
    }
}

function trierTableauPar(critere) {
    const tableau = document.getElementById("all-horses") || document.getElementById("corps-tableau-partants");
    if (!tableau) return;

    const lignes = Array.from(tableau.querySelectorAll("tr"));
    if (lignes.length === 0) return;

    lignes.sort((a, b) => {
        const colsA = a.querySelectorAll("td");
        const colsB = b.querySelectorAll("td");
        if (colsA.length < 5 || colsB.length < 5) return 0;

        if (critere === "numero") {
            const numA = parseInt(colsA[0].textContent.trim()) || 0;
            const numB = parseInt(colsB[0].textContent.trim()) || 0;
            return numA - numB;
        } 
        
        if (critere === "cote") {
            // Nettoyage de la cote pour comparer les nombres
            const coteAStr = colsA[4].textContent.trim().replace(",", ".");
            const coteBStr = colsB[4].textContent.trim().replace(",", ".");
            const coteA = parseFloat(coteAStr) || 9999;
            const coteB = parseFloat(coteBStr) || 9999;
            return coteA - coteB;
        }

        return 0;
    });

    // Reinjection des lignes triees dans le tableau
    tableau.innerHTML = "";
    lignes.forEach(ligne => tableau.appendChild(ligne));
}
