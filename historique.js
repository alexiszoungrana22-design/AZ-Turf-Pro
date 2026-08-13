/**
 * AZ TURF PRO - Gestionnaire d'Historique Durable
 * Fichier complet à remplacer : historique.js
 */

const HISTORIQUE_STORAGE_KEY = 'AZ_TURF_HISTORIQUE_COURSES_V1';

document.addEventListener('DOMContentLoaded', () => {
    // Si nous sommes sur la page d'historique, afficher le tableau
    if (document.getElementById('historique-table-body') || document.getElementById('historique-container')) {
        afficherPageHistorique();
    }
});

/**
 * Sauvegarde les courses terminées dans le LocalStorage (accessible par tous les scripts)
 * @param {Array} courses - Liste des courses venant de l'API
 */
function sauvegarderDansHistorique(courses) {
    if (!courses || !Array.isArray(courses)) return;

    try {
        const historiqueActuel = JSON.parse(localStorage.getItem(HISTORIQUE_STORAGE_KEY)) || [];
        let modifie = false;

        courses.forEach(course => {
            // Identifier les courses vraiment finies
            const estFinie = course.statut === 'ARRIVE' || 
                             course.statut === 'FINI' || 
                             (Array.isArray(course.arrivee) && course.arrivee.length > 0);

            if (estFinie) {
                // Recherche si la course est déjà stockée (par ID ou Réunion/Course/Date)
                const idUnique = course.id || `${course.date || 'D'}_${course.reunion}_${course.course}`;
                const index = historiqueActuel.findIndex(h => (h.id || `${h.date || 'D'}_${h.reunion}_${h.course}`) === idUnique);

                if (index === -1) {
                    // Nouvelle course passée à ajouter
                    historiqueActuel.push({
                        id: idUnique,
                        date: course.date || new Date().toLocaleDateString('fr-FR'),
                        reunion: course.reunion,
                        course: course.course,
                        nom: course.nom,
                        arrivee: course.arrivee || [],
                        partants: course.partants || [],
                        statut: 'FINI'
                    });
                    modifie = true;
                } else {
                    // Mettre à jour l'arrivée si elle s'est affinée
                    if (JSON.stringify(historiqueActuel[index].arrivee) !== JSON.stringify(course.arrivee)) {
                        historiqueActuel[index].arrivee = course.arrivee;
                        modifie = true;
                    }
                }
            }
        });

        if (modifie) {
            localStorage.setItem(HISTORIQUE_STORAGE_KEY, JSON.stringify(historiqueActuel));
        }
    } catch (e) {
        console.error("Erreur lors de l'enregistrement de l'historique :", e);
    }
}

/**
 * Récupère l'intégralité de l'historique sauvegardé
 * @returns {Array} Liste des courses passées
 */
function obtenirHistoriqueComplet() {
    try {
        return JSON.parse(localStorage.getItem(HISTORIQUE_STORAGE_KEY)) || [];
    } catch (e) {
        console.error("Erreur lors de la lecture de l'historique :", e);
        return [];
    }
}

/**
 * Affiche l'historique des courses passées dans le tableau HTML
 */
function afficherPageHistorique() {
    const tableBody = document.getElementById('historique-table-body');
    const containerDiv = document.getElementById('historique-container');
    const listeHistorique = obtenirHistoriqueComplet();

    // Tri du plus récent au plus ancien
    listeHistorique.reverse();

    if (tableBody) {
        tableBody.innerHTML = '';

        if (listeHistorique.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="4" class="text-center">Aucune course enregistrée dans l'historique pour le moment.</td></tr>`;
            return;
        }

        listeHistorique.forEach(c => {
            const tr = document.createElement('tr');
            
            // Formatage propre de l'arrivée sous forme "N° X - N° Y - N° Z"
            const arriveeTexte = (c.arrivee && c.arrivee.length > 0)
                ? c.arrivee.map(num => `N° ${num}`).join(' - ')
                : 'Non communiquée';

            tr.innerHTML = `
                <td>${c.date || '-'}</td>
                <td><strong>${c.reunion || ''} ${c.course || ''}</strong> - ${c.nom || 'Course'}</td>
                <td><span class="badge-arrivee">${arriveeTexte}</span></td>
                <td><span class="badge badge-fini">🏁 Terminée</span></td>
            `;
            tableBody.appendChild(tr);
        });
    } else if (containerDiv) {
        // En cas d'affichage par cartes
        containerDiv.innerHTML = '';

        if (listeHistorique.length === 0) {
            containerDiv.innerHTML = `<div class="message-vide">Aucun historique disponible.</div>`;
            return;
        }

        listeHistorique.forEach(c => {
            const card = document.createElement('div');
            card.className = 'historique-card';
            
            const arriveeTexte = (c.arrivee && c.arrivee.length > 0)
                ? c.arrivee.map(num => `N° ${num}`).join(' - ')
                : 'Arrivée indisponible';

            card.innerHTML = `
                <div class="historique-card-header">
                    <span>${c.date || ''}</span>
                    <strong>${c.reunion || ''} ${c.course || ''}</strong>
                </div>
                <div class="historique-card-body">
                    <h4>${c.nom || 'Course'}</h4>
                    <p class="arrivee-resultat"><strong>Arrivée :</strong> ${arriveeTexte}</p>
                </div>
            `;
            containerDiv.appendChild(card);
        });
    }
}

/**
 * Efface complètement l'historique local (pour la réinitialisation si besoin)
 */
function reinitialiserHistorique() {
    if (confirm("Voulez-vous vraiment effacer tout l'historique des courses passées ?")) {
        localStorage.removeItem(HISTORIQUE_STORAGE_KEY);
        afficherPageHistorique();
    }
}
