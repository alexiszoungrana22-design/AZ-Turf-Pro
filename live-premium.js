// ==========================================
// FICHIER : live-premium.js
// Gestion du Live et du Tableau des Partants
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    const btnToggle = document.getElementById("btn-toggle-tableau");
    const conteneurTableau = document.getElementById("conteneur-tableau");

    if (btnToggle && conteneurTableau) {
        btnToggle.addEventListener("click", () => {
            // Si le tableau est masqué, on l'affiche et on charge les données
            if (conteneurTableau.style.display === "none") {
                conteneurTableau.style.display = "block";
                btnToggle.innerHTML = "📊 Masquer le Tableau des Partants";
                btnToggle.style.background = "#ef4444"; // Passe en rouge

                // Appel de l'API pour récupérer et afficher les chevaux
                chargerDonneesLive();
            } else {
                // Si le tableau est affiché, on le referme
                conteneurTableau.style.display = "none";
                btnToggle.innerHTML = "📊 Afficher le Tableau des Partants (Live)";
                btnToggle.style.background = "#10b981"; // Repasse en vert
            }
        });
    }
});

// Fonction pour interroger ton API et remplir le tableau
async function chargerDonneesLive() {
    const tableau = document.getElementById("all-horses");
    if (!tableau) return;

    // Message de chargement temporaire
    tableau.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #9ca3af; padding: 15px;">Chargement des partants en cours...</td></tr>`;

    try {
        // Requête vers ton API Render
        const reponse = await fetch("https://az-turf-pro.onrender.com/api/analyse"); 
        const data = await reponse.json();
        
        // On récupère précisément le tableau "classement" de ton JSON
        const listeCheval = data.classement;

        if (Array.isArray(listeCheval) && listeCheval.length > 0) {
            tableau.innerHTML = ""; // On vide le message de chargement
            
            // On génère chaque ligne du tableau pour chaque cheval
            listeCheval.forEach(cheval => {
                const rang = cheval.rang ?? "-";
                const numero = cheval.numero ?? "-"; 
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
        } else {
            tableau.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #ef4444; padding: 15px;">Aucun partant trouvé pour le moment.</td></tr>`;
        }
    } catch (erreur) {
        console.error("Erreur de chargement :", erreur);
        tableau.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #ef4444; padding: 15px;">Erreur de connexion à l'API Render.</td></tr>`;
    }
}
