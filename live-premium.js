// ===============================
// MODULE SUIVI LIVE PREMIUM (GRATUIT)
// ===============================

function mettreAJourLivePremium() {
    const zoneLive = document.getElementById("zone-live-premium");
    if (!zoneLive) return;

    // Style de la carte (aux couleurs d'AZ Turf Pro)
    zoneLive.style.cssText = `
        background: #111827; 
        color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #374151;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin: 20px 0;
        font-family: inherit;
    `;

    // Simulation d'un statut en direct (tu pourras l'adapter avec les heures réelles de tes courses)
    const maintenant = new Date();
    const heure = maintenant.getHours();
    const minutes = maintenant.getMinutes();

    let statutTexte = "En attente du départ de la prochaine course";
    let couleurBadge = "#f59e0b"; // Orange par défaut
    let animationPulse = "";

    // Exemple simple basé sur l'heure (modifiable selon tes besoins)
    if (heure >= 13 && heure <= 18) {
        statutTexte = "Course imminente / Suivi actif sur les pistes";
        couleurBadge = "#10b981"; // Vert
        animationPulse = "animation: pulse 1.5s infinite;";
    }

    zoneLive.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 18px; display: flex; align-items: center; gap: 8px;">
                <span style="width: 12px; height: 12px; background: ${couleurBadge}; border-radius: 50%; display: inline-block; ${animationPulse}"></span>
                Live VIP - AZ Turf Pro
            </h3>
            <span style="font-size: 12px; background: #1f2937; padding: 4px 8px; border-radius: 6px; color: #9ca3af;">Exclusif Abonnés</span>
        </div>
        
        <div style="background: #1f2937; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
            <p style="margin: 0; font-size: 14px; color: #e5e7eb;">Statut actuel : <strong>${statutTexte}</strong></p>
        </div>

        <p style="margin: 0; font-size: 13px; color: #9ca3af; line-height: 1.4;">
            💡 Restez connectés sur cette page. Les indices AZ et les pronostics de dernière minute s'actualisent automatiquement avant chaque départ.
        </p>
    `;
}

// Lancement au chargement de la page
document.addEventListener("DOMContentLoaded", () => {
    mettreAJourLivePremium();
    // Actualisation automatique toutes les 60 secondes
    setInterval(mettreAJourLivePremium, 60000);
});
