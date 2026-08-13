/**
 * AZ TURF PRO - Gestionnaire d'Historique Durable
 * Fichier complet à remplacer : historique.js
 */

const HISTORIQUE_STORAGE_KEY = 'AZ_TURF_HISTORIQUE_COURSES_V1';
const API_HISTORIQUE = 'https://az-turf-pro.onrender.com/api/historique';

document.addEventListener('DOMContentLoaded', () => {
    // Si nous sommes sur la page d'historique, afficher le tableau
    if (document.getElementById('historique-body') || document.getElementById('historique-table-body') || document.getElementById('historique-container')) {
        synchroniserHistoriqueServeur().finally(() => afficherPageHistorique());
    }
});

/**
 * Sauvegarde les courses terminées dans le LocalStorage (accessible par tous les scripts)
 * @param {Array} courses - Liste des courses venant de l'API
 */
function sauvegarderDansHistorique(courses) {
    if (!courses) return;
    const liste = Array.isArray(courses) ? courses : [courses];
    try {
        const historiqueActuel = JSON.parse(localStorage.getItem(HISTORIQUE_STORAGE_KEY)) || [];
        liste.forEach(course => {
            const idUnique = course.id || course.cle || `${course.date||''}_${course.reunion||''}_${course.course_numero||course.course||''}`;
            const index = historiqueActuel.findIndex(h => (h.id || h.cle) === idUnique);
            const entree = {
                id: idUnique,
                cle: course.cle || idUnique,
                date: course.date || '',
                reunion: course.reunion || '',
                course_numero: course.course_numero || '',
                course: course.course || '',
                hippodrome: course.hippodrome || '',
                arrivee: Array.isArray(course.arrivee) ? course.arrivee : [],
                rapports: course.rapports || [],
                statut: course.statut || (course.arrivee && course.arrivee.length ? 'FINI' : 'ANALYSEE'),
                favori: course.favori || {},
                selection: course.selection || [],
                premium: course.premium || {},
                date_enregistrement: course.date_enregistrement || new Date().toISOString()
            };
            if(index >= 0) historiqueActuel[index] = {...historiqueActuel[index], ...entree};
            else historiqueActuel.unshift(entree);
        });
        localStorage.setItem(HISTORIQUE_STORAGE_KEY, JSON.stringify(historiqueActuel.slice(0,100)));
    } catch(e) { console.error('Erreur historique local :', e); }
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

async function synchroniserHistoriqueServeur(){
    try {
        const response = await fetch(API_HISTORIQUE, {cache:'no-store'});
        if(!response.ok) return;
        const data = await response.json();
        const serveur = data.historique || [];
        const local = obtenirHistoriqueComplet();
        serveur.forEach(item => {
            const course = item.course || {};
            sauvegarderDansHistorique({
                id: item.id || `${course.date||''}_${course.reunion||''}_${course.course_numero||''}`,
                date: course.date || item.date || '',
                reunion: course.reunion || item.reunion || '',
                course_numero: course.course_numero || item.course_numero || '',
                course: course.course || item.course || '',
                hippodrome: course.hippodrome || item.hippodrome || '',
                arrivee: item.arrivee || [],
                rapports: item.rapports || [],
                statut: item.arrivee && item.arrivee.length ? 'FINI' : 'ANALYSEE',
                favori: item.favori || {},
                selection: item.tickets?.gratuit?.quinte || [],
                premium: item.tickets?.premium || {}
            });
        });
    } catch(e) { console.log('Historique serveur indisponible', e); }
}

/**
 * Affiche l'historique des courses passées dans le tableau HTML
 */
function afficherPageHistorique() {
    const tableBody = document.getElementById('historique-body') || document.getElementById('historique-table-body');
    const containerDiv = document.getElementById('historique-container');
    const listeHistorique = obtenirHistoriqueComplet();

    // Tri du plus récent au plus ancien
    listeHistorique.reverse();

    if (tableBody) {
        tableBody.innerHTML = '';

        if (listeHistorique.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center">Aucune course enregistrée dans l'historique pour le moment.</td></tr>`;
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
                <td><strong>${c.reunion || ''} C${c.course_numero || ''}</strong> - ${c.course || 'Course'}</td>
                <td>${c.hippodrome || '-'}</td>
                <td><span class="badge-arrivee">${arriveeTexte}</span></td>
                <td><span class="badge badge-fini">${c.statut === "FINI" ? "🏁 Terminée" : "📊 Analysée"}</span></td>
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
