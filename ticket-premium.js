// ==========================================================
// AZ TURF PRO - TICKETS PREMIUM
// Vérification d'accès réelle + données réelles (/api/analyse)
// ==========================================================

const API_ANALYSE =
"https://az-turf-pro.onrender.com/api/analyse";

const API_PREMIUM =
"https://az-turf-pro.onrender.com/api/premium/";


document.addEventListener("DOMContentLoaded", function () {

    initialiserBoutonTableau();

    verifierAccesPremium();

});


// =====================================
// 1. VERIFICATION ACCES PREMIUM
// (aucun contenu affiche tant que ce
// n'est pas confirme cote serveur)
// =====================================

async function verifierAccesPremium(){

    const telephone =
    localStorage.getItem("AZ_TURF_TELEPHONE");

    const blocage =
    document.getElementById("message-blocage");

    const contenu =
    document.getElementById("contenu-premium");

    if(!telephone){

        if(blocage) blocage.classList.remove("zone-masquee");
        if(contenu) contenu.classList.add("zone-masquee");

        return;

    }

    try{

        const reponse = await fetch(
            API_PREMIUM + encodeURIComponent(telephone)
        );

        const data = await reponse.json();

        if(reponse.ok && data.statut === "ACTIF"){

            if(blocage) blocage.classList.add("zone-masquee");
            if(contenu) contenu.classList.remove("zone-masquee");

            chargerTicketsPremium();

        }else{

            if(blocage) blocage.classList.remove("zone-masquee");
            if(contenu) contenu.classList.add("zone-masquee");

        }

    }catch(error){

        console.error("Erreur vérification Premium :", error);

        if(blocage) blocage.classList.remove("zone-masquee");
        if(contenu) contenu.classList.add("zone-masquee");

    }

}


// =====================================
// 2. CHARGEMENT DES VRAIS TICKETS
// (deja calcules cote serveur par
// quinte.py - on ne les recalcule pas)
// =====================================

async function chargerTicketsPremium(){

    try{

        const reponse = await fetch(API_ANALYSE);

        if(!reponse.ok){
            throw new Error("Erreur API analyse");
        }

        const data = await reponse.json();

        const tickets =
        (data.tickets && data.tickets.premium) || {};

        const classement = data.classement || [];


        // ---- Selection Premium (8 chevaux) ----
        injecter(
            "selection-premium",
            (tickets.selection_quinte || []).join(" - "),
            true
        );


        // ---- Explication ----
        const favori = classement[0];

        injecter(
            "explication-premium",
            favori
            ? `Le n°${favori.numero} (${favori.nom || ""}) ressort en tête de l'analyse AZ avec un indice de ${Math.round(favori.indice_az || 0)} et une confiance de ${favori.confiance ?? "-"}%.`
            : "Analyse basée sur la forme, la régularité et le classement AZ du jour.",
            false
        );


        // ---- Tickets ----
        injecter("quinte-premium", (tickets.quinte || []).join(" - "), true);
        injecter("quarte-premium", (tickets.quarte || []).join(" - "), true);
        injecter("trio-premium", (tickets.trio || []).join(" - "), true);

        const couples = tickets.couple_gagnant_place || [];
        injecter(
            "couple-premium",
            couples.map(c => c.join("-")).join(" | "),
            true
        );

        const champReduit = tickets.champ_reduit || {};
        injecter(
            "champ-reduit-premium",
            champReduit.format || "Non disponible",
            true
        );


        // ---- Derniere minute ----
        const derniereMinute =
        (tickets.ticket_derniere_minute &&
        tickets.ticket_derniere_minute.selection) || [];

        injecter(
            "derniere-minute-premium",
            derniereMinute.length
            ? derniereMinute.join(" - ")
            : "Non disponible",
            true
        );


        // ---- Analyse complete ----
        injecter(
            "analyse-premium",
            tickets.explication ||
            "Analyse AZ Turf Pro basée sur l'indice AZ, la forme récente et la régularité de chaque cheval.",
            false
        );


        // ---- Message final ----
        injecter(
            "message-premium",
            tickets.message_fin ||
            "🍀 Bonne chance à tous les abonnés Premium pour cette course !",
            false
        );

    }catch(error){

        console.error("Erreur chargement tickets Premium :", error);

        [
            "selection-premium", "quinte-premium", "quarte-premium",
            "trio-premium", "couple-premium", "champ-reduit-premium",
            "derniere-minute-premium"
        ].forEach(id => {
            const el = document.getElementById(id);
            if(el) el.textContent = "Indisponible pour le moment";
        });

    }

}


// =====================================
// FORMATAGE DES PASTILLES
// (conserve tel quel - c'est une bonne
// amelioration visuelle)
// =====================================

function convertirEnPastilles(texte){

    if(!texte) return "";

    const parties = String(texte).split("/");

    function convertir(chaine){
        return String(chaine)
            .split(/[-,\s]+/)
            .map(item => item.trim())
            .filter(Boolean)
            .map(num => {
                if(!isNaN(num)){
                    return `<span class="numero-cheval">${String(num).padStart(2, "0")}</span>`;
                }else if(num.toUpperCase() === "X"){
                    return `<span class="numero-cheval" style="background-color: #d97706;">X</span>`;
                }
                return num;
            })
            .join(" ");
    }

    if(parties.length > 1){
        return convertir(parties[0]) +
            ` <strong style="font-size: 20px; color: #0f172a; margin: 0 6px;">/</strong> ` +
            convertir(parties[1]);
    }

    return convertir(texte);

}


function injecter(id, contenu, estCombine){

    const el = document.getElementById(id);

    if(!el) return;

    if(estCombine){
        el.innerHTML = convertirEnPastilles(contenu);
    }else{
        el.textContent = contenu || "";
    }

}


// =====================================
// 3. TABLEAU LIVE (partants complets)
// =====================================

function initialiserBoutonTableau(){

    const btnTableau =
    document.getElementById("btn-toggle-tableau");

    const conteneurTableau =
    document.getElementById("conteneur-tableau");

    if(!btnTableau || !conteneurTableau) return;

    btnTableau.addEventListener("click", async function(){

        if(conteneurTableau.classList.contains("zone-masquee")){

            conteneurTableau.classList.remove("zone-masquee");
            btnTableau.innerText = "❌ Masquer le Tableau Live";

            await chargerTableauLive();

        }else{

            conteneurTableau.classList.add("zone-masquee");
            btnTableau.innerText = "📊 Afficher le Tableau des Partants (Live)";

        }

    });

}


async function chargerTableauLive(){

    const tableau =
    document.getElementById("all-horses");

    if(!tableau) return;

    tableau.innerHTML =
    `<tr><td colspan="5" style="text-align:center; padding:15px;">Chargement...</td></tr>`;

    try{

        const reponse = await fetch(API_ANALYSE);

        if(!reponse.ok){
            throw new Error("Erreur API analyse");
        }

        const data = await reponse.json();

        const classement = data.classement || [];

        if(!classement.length){

            tableau.innerHTML =
            `<tr><td colspan="5" style="text-align:center; padding:15px;">Classement indisponible.</td></tr>`;

            return;

        }

        tableau.innerHTML = classement.map(cheval => {

            const rang = cheval.rang ?? "-";
            const numero = cheval.numero ?? "-";
            const nom = cheval.nom || "-";

            const indice =
            (cheval.indice_az !== null && cheval.indice_az !== undefined)
            ? Math.round(cheval.indice_az)
            : "-";

            const confiance =
            (cheval.confiance !== null && cheval.confiance !== undefined)
            ? cheval.confiance + " %"
            : "-";

            return `
                <tr>
                    <td style="padding:10px;"><strong>${rang}</strong></td>
                    <td style="padding:10px;"><strong>${numero}</strong></td>
                    <td style="padding:10px;">${nom}</td>
                    <td style="padding:10px;">${indice}</td>
                    <td style="padding:10px;">${confiance}</td>
                </tr>
            `;

        }).join("");

    }catch(error){

        console.error("Erreur tableau live :", error);

        tableau.innerHTML =
        `<tr><td colspan="5" style="text-align:center; padding:15px;">Erreur de chargement.</td></tr>`;

    }

    }
    
