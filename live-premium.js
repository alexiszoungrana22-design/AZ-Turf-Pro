/**
 * AZ TURF PRO - Live & Premium Management
 * Fichier complet à remplacer : live-premium.js
 */

// Configuration globale
const API_CONFIG = {
    ENDPOINT_LIVE: '/api/live-courses',
    REFRESH_INTERVAL: 20000 // Rafraîchissement toutes les 20 secondes
};

document.addEventListener('DOMContentLoaded', () => {
    initLivePremium();
});

/**
 * Initialisation de la page Live / Premium
 */
async function initLivePremium() {
    await chargerEtAfficherDonnees();
    
    // Auto-rafraîchissement en arrière-plan
    setInterval(async () => {
        await chargerEtAfficherDonnees();
    }, API_CONFIG.REFRESH_INTERVAL);
}

/**
 * Récupère les données depuis l'API et met à jour l'interface
 */
async function chargerEtAfficherDonnees() {
    try {
        const response = await fetch(API_CONFIG.ENDPOINT_LIVE);
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        const courses = data.courses || [];

        // 1. Sauvegarde automatique des courses finies dans l'historique local
        if (typeof sauvegarderDansHistorique === 'function') {
            sauvegarderDansHistorique(courses);
        }

        // 2. Affichage des cartes dans la section Live Premium
        afficherCoursesLive(courses);

    } catch (erreur) {
        console.error("Erreur lors du chargement Live/Premium :", erreur);
    }
}

/**
 * Générateur de tickets garanti sans doublon entre Gratuit et Premium
 * @param {Array} partants - Liste des chevaux partants
 * @returns {Object} { gratuit: [], premium: [] }
 */
function genererTicketsDistincts(partants) {
    if (!partants || !Array.isArray(partants) || partants.length < 4) {
        return { gratuit: [], premium: [] };
    }

    // Copie et tri des partants par cote croissante (plus petite cote = favori)
    const partantsTries = [...partants].sort((a, b) => {
        const coteA = parseFloat(a.cote) || 999;
        const coteB = parseFloat(b.cote) || 999;
        return coteA - coteB;
    });

    // --- TICKET GRATUIT (Favoris logiques : rangs 1 à 4) ---
    const ticketGratuit = partantsTries.slice(0, 4).map(p => String(p.num || p.numero));

    // --- TICKET PREMIUM (Stratégie Mixte : Favoris + Outsiders ciblés) ---
    const favori1 = String(partantsTries[0]?.num || partantsTries[0]?.numero);
    const favori2 = String(partantsTries[1]?.num || partantsTries[1]?.numero);
    
    // Sélection d'outsiders spéculatifs (rangs 4 à 8 dans le tableau trié)
    const candidatsOutsiders = partantsTries.slice(3, 8).map(p => String(p.num || p.numero));
    
    // On construit le ticket Premium avec le top favori + 3 outsiders uniques
    let ticketPremium = [favori1];
    
    for (let num of candidatsOutsiders) {
        if (!ticketPremium.includes(num) && ticketPremium.length < 5) {
            ticketPremium.push(num);
        }
    }

    // Compléter si le ticket Premium manque de numéros
    if (ticketPremium.length < 4 && favori2 && !ticketPremium.includes(favori2)) {
        ticketPremium.push(favori2);
    }

    // SÉCURITÉ STRICTE : Si par hasard les tickets sont identiques, on force une différence
    const strGratuit = [...ticketGratuit].sort().join('-');
    const strPremium = [...ticketPremium].sort().join('-');

    if (strGratuit === strPremium) {
        // Remplacer le dernier numéro du ticket Premium par un autre partant
        const restant = partantsTries.find(p => {
            const numStr = String(p.num || p.numero);
            return !ticketGratuit.includes(numStr);
        });

        if (restant) {
            ticketPremium[ticketPremium.length - 1] = String(restant.num || restant.numero);
        }
    }

    return {
        gratuit: ticketGratuit,
        premium: ticketPremium
    };
}

/**
 * Injection dynamique du DOM pour le Live/Premium
 * @param {Array} courses - Liste des courses
 */
function afficherCoursesLive(courses) {
    const conteneur = document.getElementById('live-premium-container');
    if (!conteneur) return;

    if (!courses || courses.length === 0) {
        conteneur.innerHTML = `<div class="message-vide">Aucune course en direct pour le moment.</div>`;
        return;
    }

    conteneur.innerHTML = '';

    courses.forEach(course => {
        const tickets = genererTicketsDistincts(course.partants || []);
        
        const card = document.createElement('div');
        card.className = 'course-card-premium';

        // Badge de statut
        let badgeStatut = '<span class="badge badge-attente">⏳ À VENIR</span>';
        if (course.statut === 'EN_COURS') {
            badgeStatut = '<span class="badge badge-live">🔴 EN DIRECT</span>';
        } else if (course.statut === 'ARRIVE' || course.statut === 'FINI') {
            badgeStatut = '<span class="badge badge-fini">🏁 TERMINÉE</span>';
        }

        // Structure HTML
        card.innerHTML = `
            <div class="course-header">
                <div class="course-title">
                    <h3>${course.reunion || 'R'} ${course.course || 'C'} - ${course.nom || 'Course'}</h3>
                    <span class="heure">${course.heure || ''}</span>
                </div>
                ${badgeStatut}
            </div>

            <div class="tickets-section">
                <!-- TICKET GRATUIT -->
                <div class="ticket-box ticket-gratuit">
                    <div class="ticket-header">
                        <h4>🎫 Ticket Gratuit</h4>
                    </div>
                    <div class="num-list">
                        ${tickets.gratuit.length > 0 
                            ? tickets.gratuit.map(n => `<span class="num-badge">N° ${n}</span>`).join('') 
                            : '<span>En attente...</span>'}
                    </div>
                </div>

                <!-- TICKET PREMIUM -->
                <div class="ticket-box ticket-premium">
                    <div class="ticket-header">
                        <h4>⭐ Ticket Premium AZ Pro</h4>
                    </div>
                    <div class="num-list">
                        ${tickets.premium.length > 0 
                            ? tickets.premium.map(n => `<span class="num-badge premium">N° ${n}</span>`).join('') 
                            : '<span>En attente...</span>'}
                    </div>
                </div>
            </div>

            ${(course.arrivee && course.arrivee.length > 0) ? `
                <div class="arrivee-officielle">
                    <strong>Arrivée officielle :</strong> ${course.arrivee.join(' - ')}
                </div>
            ` : ''}
        `;

        conteneur.appendChild(card);
    });
      }
