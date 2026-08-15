// =====================================
// AZ TURF PRO - HISTORIQUE
// Chargement dynamique des données SQL
// =====================================

document.addEventListener("DOMContentLoaded", () => {
    chargerHistorique();
});

async function chargerHistorique() {
    const tbody = document.getElementById("historique-body");
    
    try {
        // Envoi de la requête vers l'API backend Python
        const response = await fetch("/api/historique");
        
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération de l'historique");
        }
        
        const courses = await response.json();
        
        // Réinitialisation du tableau HTML
        tbody.innerHTML = "";

        if (courses.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">Aucune course enregistrée pour le moment.</td></tr>`;
            mettreAJourStatistiques([]);
            return;
        }

        // Remplissage dynamique des lignes
        courses.forEach(c => {
            const row = document.createElement("tr");
            
            row.innerHTML = `
                <td>${c.date || '-'}</td>
                <td><strong>${c.course || '-'}</strong></td>
                <td>${c.favori || '-'}</td>
                <td><span class="badge-selection">${c.selection_az || '-'}</span></td>
                <td><span class="badge-arrivee">${c.arrivee || 'En attente'}</span></td>
            `;
            
            tbody.appendChild(row);
        });

        // Mise à jour des cartes KPI
        mettreAJourStatistiques(courses);

    } catch (error) {
        console.error("Erreur historique :", error);
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:red;">Impossible de charger l'historique.</td></tr>`;
    }
}

// =====================================
// CALCUL ET AFFICHAGE DES STATISTIQUES
// =====================================

function mettreAJourStatistiques(courses) {
    const totalCoursesEl = document.getElementById("total-courses");
    const favorisGagnantsEl = document.getElementById("favoris-gagnants");
    const ticketsReussisEl = document.getElementById("tickets-reussis");

    if (!totalCoursesEl || !favorisGagnantsEl || !ticketsReussisEl) return;

    // Total des courses analysées
    const total = courses.length;
    totalCoursesEl.textContent = total;

    let favorisGagnants = 0;
    let ticketsReussis = 0;

    courses.forEach(c => {
        if (c.arrivee && c.arrivee !== "En attente") {
            const premierArrive = c.arrivee.split("-")[0]?.trim();

            // Vérification si le favori est dans l'arrivée
            if (c.favori && c.arrivee.includes(c.favori)) {
                favorisGagnants++;
            }

            // Vérification si un des numéros de la sélection AZ est 1er
            if (c.selection_az && premierArrive && c.selection_az.includes(premierArrive)) {
                ticketsReussis++;
            }
        }
    });

    favorisGagnantsEl.textContent = favorisGagnants;
    ticketsReussisEl.textContent = ticketsReussis;
}
