// ===============================
// GESTION DU BOUTON ET DU TABLEAU DES PARTANTS
// ===============================

document.addEventListener("DOMContentLoaded", () => {
    const btnToggle = document.getElementById("btn-toggle-tableau");
    const conteneurTableau = document.getElementById("conteneur-tableau");

    if (btnToggle && conteneurTableau) {
        btnToggle.addEventListener("click", () => {
            // Si le tableau est masqué, on l'affiche et on charge les données
            if (conteneurTableau.style.display === "none") {
                conteneurTableau.style.display = "block";
                btnToggle.innerHTML = "📊 Masquer le Tableau des Partants";
                btnToggle.style.background = "#ef4444"; // Passe en rouge pour fermer

                // Fonction qui charge les données de l'API (si ce n'est pas déjà fait)
                chargerTableauPartants();
            } else {
                // Si le tableau est affiché, on le masque
                conteneurTableau.style.display = "none";
                btnToggle.innerHTML = "📊 Afficher le Tableau des Partants (Live)";
                btnToggle.style.background = "#10b981"; // Repasse en vert
            }
        });
    }
});

// Fonction de remplissage du tableau (SANS AUCUN PRÉFIXE NA / N°)
function chargerTableauPartants() {
    const tableau = document.getElementById("all-horses");
    if(!tableau) return;

    // Simulation ou appel de ton API existante (remplace par tes données)
    // Exemple avec ta variable "classement" :
    if (typeof classement !== 'undefined' && Array.isArray(classement)) {
        tableau.innerHTML = "";
        classement.forEach(cheval => {
            const rang = cheval.rang ?? "-";
            const numero = cheval.numero ?? "-"; // Uniquement le chiffre (ex: 1, 12...)
            const nom = cheval.nom || "-";
            const indice = cheval.indice_az ? Math.round(cheval.indice_az) : "-";
            const confiance = cheval.confiance ? cheval.confiance + " %" : "-";

            tableau.innerHTML += `
                <tr style="border-bottom: 1px solid #374151;">
                    <td style="padding: 12px;"><strong>${rang}</strong></td>
                    <td style="padding: 12px;"><strong>${numero}</strong></td>
                    <td style="padding: 12px;">${nom}</td>
                    <td style="padding: 12px;"><span style="background: #1f2937; padding: 4px 8px; border-radius: 4px; color: #10b981; font-weight: bold;">${indice}</span></td>
                    <td style="padding: 12px;">${confiance}</td>
                </tr>
            `;
        });
    }
}
