// =====================================
// AZ TURF PRO
// TICKET PREMIUM
// AFFICHAGE FINAL
// VERSION RESPONSIVE
// =====================================

const API_URL =
"https://az-turf-pro.onrender.com/api/analyse";

const API_PREMIUM =
"https://az-turf-pro.onrender.com/api/premium/";


// =====================================
// DEMARRAGE
// =====================================

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


        const data =
            await reponse.json();


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

            throw new Error(
                "Erreur API"
            );

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
        // 7 CHEVAUX
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

                        ${
                            c.raison ||
                            "Analyse spécialisée en cours"
                        }

                    </p>

                `)
                .join("")

        );



        // =====================================
        // QUINTE PREMIUM
        // 6 CHEVAUX
        // =====================================

        let quintePremium =
            premium.quinte || [];


        if(Array.isArray(quintePremium)){

            quintePremium =
                quintePremium.slice(0,6);

        }


        afficherTicket(

            "quinte-premium",

            quintePremium

        );



        // =====================================
        // QUARTE PREMIUM
        // 4 CHEVAUX
        // =====================================

        let quartePremium =
            premium.quarte || [];


        if(Array.isArray(quartePremium)){

            quartePremium =
                quartePremium.slice(0,4);

        }


        afficherTicket(

            "quarte-premium",

            quartePremium

        );



        // =====================================
        // TRIO PREMIUM
        // 3 CHEVAUX
        // =====================================

        let trioPremium =
            premium.trio || [];


        if(Array.isArray(trioPremium)){

            trioPremium =
                trioPremium.slice(0,3);

        }


        afficherTicket(

            "trio-premium",

            trioPremium

        );



        // =====================================
        // COUPLES PREMIUM
        // 3 COUPLES COMPLETS
        //
        // Exemple :
        // 3-5 | 3-2 | 5-2
        // =====================================

        if(
            premium.couple_gagnant_place
        ){

            let couple =
                premium.couple_gagnant_place;


            if(Array.isArray(couple)){

                couple =
                    couple
                        .map(c => {

                            if(Array.isArray(c)){

                                return c.join("-");

                            }

                            return c;

                        })
                        .join(" | ");

            }


            afficherTexte(

                "couple-premium",

                couple

            );


            ajusterAffichage(
                "couple-premium"
            );

        }



        // =====================================
        // CHAMP REDUIT
        // =====================================

        if(
            premium.champ_reduit
        ){

            let champ =
                premium.champ_reduit.format ||
                "Non disponible";


            afficherTexte(

                "champ-reduit-premium",

                champ

            );


            ajusterAffichage(
                "champ-reduit-premium"
            );

        }



        // =====================================
        // DERNIERE MINUTE
        // 6 NUMEROS
        // =====================================

        if(
            premium.ticket_derniere_minute
        ){

            let derniere =
                premium
                    .ticket_derniere_minute
                    .selection || [];


            derniere =
                derniere.slice(0,6);


            afficherTicket(

                "derniere-minute-premium",

                derniere

            );

        }



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
// AJUSTEMENT RESPONSIVE
//
// IMPORTANT :
// Aucun défilement horizontal.
// Aucun forçage en nowrap.
// Le navigateur peut adapter le texte
// à la largeur disponible.
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

    zone.style.boxSizing = "border-box";

    zone.style.textAlign = "center";

    zone.style.whiteSpace = "normal";

    zone.style.overflow = "visible";

    zone.style.overflowX = "visible";

    zone.style.overflowWrap = "break-word";

    zone.style.wordBreak = "normal";

    zone.style.letterSpacing = "0px";

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
// SECURITE AFFICHAGE MOBILE
// =====================================

window.addEventListener(
    "resize",
    function(){

        const ids = [

            "selection-premium",

            "quinte-premium",

            "quarte-premium",

            "trio-premium",

            "couple-premium",

            "champ-reduit-premium",

            "derniere-minute-premium"

        ];


        ids.forEach(
            id => ajusterAffichage(id)
        );

    }
);

