// =====================================
// AZ TURF PRO
// TICKET PREMIUM
// AFFICHAGE FINAL
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


        if(reponse.ok && data.statut === "ACTIF"){

            if(contenu){
                contenu.style.display = "block";
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

                        ${c.raison || "Analyse spécialisée en cours"}

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
        // Exemple :
        // 3-5 | 3-2 | 5-2
        // =====================================

        if(premium.couple_gagnant_place){

            let couple =
                premium.couple_gagnant_place;


            if(Array.isArray(couple)){

                couple = couple
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


            ajusterTailleUneLigne(
                "couple-premium"
            );

        }



        // =====================================
        // CHAMP REDUIT
        // =====================================

        if(premium.champ_reduit){

            let champ =
                premium.champ_reduit.format ||
                "Non disponible";


            afficherTexte(

                "champ-reduit-premium",

                champ

            );


            ajusterTailleUneLigne(
                "champ-reduit-premium"
            );

        }



        // =====================================
        // DERNIERE MINUTE
        // 6 NUMEROS
        // =====================================

        if(premium.ticket_derniere_minute){

            let derniere =
                premium.ticket_derniere_minute.selection || [];


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
        // MESSAGE
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
// AJUSTEMENT AUTOMATIQUE
// GARDE LES NUMEROS SUR UNE LIGNE
// =====================================

function ajusterTailleUneLigne(id){

    const zone =
        document.getElementById(id);

    if(!zone){
        return;
    }

    zone.style.whiteSpace = "normal";
    zone.style.overflow = "visible";
    zone.style.letterSpacing = "0px";
}


    let taille =
        parseInt(
            window.getComputedStyle(zone).fontSize
        ) || 24;


    const tailleMinimum = 14;


    zone.style.whiteSpace =
        "nowrap";


    zone.style.letterSpacing =
        "0px";


    zone.style.overflow =
        "visible";


    let securite = 0;


    while(

        zone.scrollWidth >
        zone.clientWidth &&

        taille >
        tailleMinimum &&

        securite <
        60

    ){

        taille -= 1;


        zone.style.fontSize =
            taille + "px";


        securite++;

    }

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


    if(!liste || liste.length === 0){

        zone.innerHTML =
            "Non disponible";

        return;

    }


    zone.innerHTML =
        liste.join(" - ");


    ajusterTailleUneLigne(id);

}



// =====================================
// AFFICHAGE LISTE
// =====================================

function afficherListe(id,liste){

    const zone =
        document.getElementById(id);


    if(zone){

        zone.innerHTML =
            liste.join(" - ");


        ajusterTailleUneLigne(id);

    }

}



// =====================================
// AFFICHAGE TEXTE
// =====================================

function afficherTexte(id,contenu){

    const zone =
        document.getElementById(id);


    if(zone){

        zone.innerHTML =
            contenu;

    }

}
```
