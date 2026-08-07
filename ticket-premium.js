// =====================================
// AZ TURF PRO
// TICKET PREMIUM
// VERSION FINALE
// =====================================

const API_URL =
"https://az-turf-pro.onrender.com/api/analyse";

const API_PREMIUM =
"https://az-turf-pro.onrender.com/api/premium/";


document.addEventListener(
    "DOMContentLoaded",
    verifierAccesPremium
);


// =====================================
// VERIFICATION ACCES PREMIUM
// =====================================

async function verifierAccesPremium(){

    const telephone =
        localStorage.getItem("AZ_TURF_TELEPHONE");

    const contenu =
        document.getElementById("contenu-premium");

    const blocage =
        document.getElementById("message-blocage");


    if(!telephone){

        if(blocage){
            blocage.style.display = "block";
        }

        return;
    }


    try{

        const reponse = await fetch(
            API_PREMIUM + encodeURIComponent(telephone)
        );

        const data = await reponse.json();


        if(
            reponse.ok &&
            data.statut === "ACTIF"
        ){

            if(contenu){
                contenu.style.display = "block";
            }

            if(blocage){
                blocage.style.display = "none";
            }

            chargerPremium();

        }else{

            if(blocage){
                blocage.style.display = "block";
            }

        }

    }catch(error){

        console.error(
            "Erreur vérification Premium :",
            error
        );

        if(blocage){
            blocage.style.display = "block";
        }

    }

}


// =====================================
// CHARGEMENT PREMIUM
// =====================================

async function chargerPremium(){

    try{

        const response =
            await fetch(API_URL);


        if(!response.ok){
            throw new Error("Erreur API");
        }


        const data =
            await response.json();


        console.log(
            "Données Premium :",
            data
        );


        const premium =
            data.tickets?.premium || {};

        const classement =
            data.classement || [];


        // =====================================
        // SELECTION PREMIUM
        // EXACTEMENT 7 CHEVAUX
        // =====================================

        afficherListe(
            "selection-premium",
            classement
                .slice(0,7)
                .map(c => c.numero)
        );


        // =====================================
        // EXPLICATION
        // =====================================

        afficherTexte(
            "explication-premium",

            classement
                .slice(0,7)
                .map(c => `
                    <p>
                        🏇 N°${c.numero}
                        <br>
                        ${c.raison || "Analyse spécialisée en cours"}
                    </p>
                `)
                .join("")
        );


        // =====================================
        // QUINTE PREMIUM
        // EXACTEMENT 6 CHEVAUX
        // =====================================

        let quinte =
            premium.quinte || [];


        if(Array.isArray(quinte)){

            quinte =
                quinte.slice(0,6);

        }else{

            quinte = [];

        }


        afficherTicket(
            "quinte-premium",
            quinte
        );


        // =====================================
        // QUARTE PREMIUM
        // EXACTEMENT 5 CHEVAUX
        // =====================================

        let quarte =
            premium.quarte || [];


        if(Array.isArray(quarte)){

            quarte =
                quarte.slice(0,5);

        }else{

            quarte = [];

        }


        afficherTicket(
            "quarte-premium",
            quarte
        );


        // =====================================
        // TRIO PREMIUM
        // EXACTEMENT 3 CHEVAUX
        // =====================================

        let trio =
            premium.trio || [];


        if(Array.isArray(trio)){

            trio =
                trio.slice(0,3);

        }else{

            trio = [];

        }


        afficherTicket(
            "trio-premium",
            trio
        );


        // =====================================
        // COUPLES PREMIUM
        // 3 COUPLES COMPLETS
        //
        // Exemple :
        // 3-5 | 3-2 | 5-2
        // =====================================

        let couples =
            premium.couple_gagnant_place || [];


        if(Array.isArray(couples)){

            couples =
                couples
                    .slice(0,3)
                    .map(couple => {

                        if(Array.isArray(couple)){

                            return couple.join("-");

                        }

                        return couple;

                    })
                    .join(" | ");

        }


        afficherTexte(
            "couple-premium",
            couples || "Non disponible"
        );


        ajusterAffichage(
            "couple-premium"
        );


        // =====================================
        // CHAMP REDUIT
        // =====================================

        let champ =
            premium.champ_reduit?.format ||
            "Non disponible";


        afficherTexte(
            "champ-reduit-premium",
            champ
        );


        ajusterAffichage(
            "champ-reduit-premium"
        );


        // =====================================
        // DERNIERE MINUTE
        // EXACTEMENT 6 NUMEROS
        // =====================================

        let derniere =
            premium.ticket_derniere_minute?.selection || [];


        if(Array.isArray(derniere)){

            derniere =
                derniere.slice(0,6);

        }else{

            derniere = [];

        }


        afficherTicket(
            "derniere-minute-premium",
            derniere
        );


        // =====================================
        // ANALYSE
        // =====================================

        afficherTexte(

            "analyse-premium",

            `
            <h3>📈 Points forts</h3>

            <p>
            Analyse de la forme, régularité,
            distance, terrain et expérience.
            </p>

            <h3>📉 Points de vigilance</h3>

            <p>
            Évaluation des risques liés à la course.
            </p>
            `

        );


        // =====================================
        // MESSAGE FINAL
        // =====================================

        afficherTexte(

            "message-premium",

            premium.message_fin ||
            "🍀 Bonne chance ! Jouez avec discipline."

        );


    }catch(error){

        console.error(
            "Erreur Premium :",
            error
        );

    }

}


// =====================================
// AFFICHAGE RESPONSIVE
// AUCUN DEFILEMENT HORIZONTAL
// =====================================

function ajusterAffichage(id){

    const zone =
        document.getElementById(id);


    if(!zone){
        return;
    }


    zone.style.width = "100%";
    zone.style.maxWidth = "100%";
    zone.style.minWidth = "0";

    zone.style.boxSizing =
        "border-box";

    zone.style.textAlign =
        "center";

    zone.style.whiteSpace =
        "normal";

    zone.style.overflow =
        "visible";

    zone.style.overflowX =
        "visible";

    zone.style.overflowWrap =
        "break-word";

    zone.style.wordBreak =
        "normal";

    zone.style.letterSpacing =
        "0px";

}


// =====================================
// AFFICHAGE TICKET
// =====================================

function afficherTicket(id,liste){

    const zone =
        document.getElementById(id);


    if(!zone){
        return;
    }


    if(
        !liste ||
        liste.length === 0
    ){

        zone.innerHTML =
            "Non disponible";

        return;
    }


    zone.innerHTML =
        liste.join(" - ");


    ajusterAffichage(id);

}


// =====================================
// AFFICHAGE LISTE
// =====================================

function afficherListe(id,liste){

    const zone =
        document.getElementById(id);


    if(!zone){
        return;
    }


    if(
        !liste ||
        liste.length === 0
    ){

        zone.innerHTML =
            "Non disponible";

        return;
    }


    zone.innerHTML =
        liste.join(" - ");


    ajusterAffichage(id);

}


// =====================================
// AFFICHAGE TEXTE
// =====================================

function afficherTexte(id,contenu){

    const zone =
        document.getElementById(id);


    if(!zone){
        return;
    }


    zone.innerHTML =
        contenu;

}


// =====================================
// REAJUSTEMENT ECRAN
// =====================================

window.addEventListener(
    "resize",
    function(){

        const zones = [

            "selection-premium",
            "quinte-premium",
            "quarte-premium",
            "trio-premium",
            "couple-premium",
            "champ-reduit-premium",
            "derniere-minute-premium"

        ];


        zones.forEach(
            id => ajusterAffichage(id)
        );

    }
);
