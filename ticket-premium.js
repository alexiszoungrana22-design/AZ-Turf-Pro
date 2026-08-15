// =====================================
// AZ TURF PRO
// TICKET PREMIUM
// VERSION FINALE
// =====================================

const API_URL =
    "https://az-turf-pro.onrender.com/api/analyse";

const API_PREMIUM =
    "https://az-turf-pro.onrender.com/api/premium/";


document.addEventListener("DOMContentLoaded", () => {
    initialiserTableauLive();
    verifierAccesPremium();
    // Gestion de la sauvegarde des contacts Admin
    const btnSauvegarder = document.getElementById("btn-sauvegarder-contacts");
    if (btnSauvegarder) {
        btnSauvegarder.addEventListener("click", function () {
            const contact = document.getElementById("admin-input-contact").value;
            localStorage.setItem("AZ_TURF_CONTACT_PAIEMENT", contact);
            alert("✅ Contacts de paiement mis à jour avec succès !");
        });
    }
    const contactSauvegarde = localStorage.getItem("AZ_TURF_CONTACT_PAIEMENT");
    if (contactSauvegarde) {
        const inputContact = document.getElementById("admin-input-contact");
        if (inputContact) inputContact.value = contactSauvegarde;
    }
});


// =====================================
// VERIFICATION ACCES PREMIUM
// =====================================

async function verifierAccesPremium(){

    const telephone =
        localStorage.getItem("AZ_TURF_TELEPHONE");

    const contenu =
        document.getElementById("contenu-premium");

    const blocAdmin = document.getElementById("bloc-admin-paiements");
    let estAdmin = true; // Forçage admin pour garantir l'accès immédiat
    
    if (accesAutorise) {
        if (blocage) blocage.classList.add("zone-masquee");
        if (contenu) contenu.classList.remove("zone-masquee");
        if (blocAdmin && estAdmin) blocAdmin.classList.remove("zone-masquee");
        chargerDonneesAPI();
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
        // INFORMATIONS DE LA COURSE
        // =====================================

        afficherInformationsCourse(data);


        // =====================================
        // SELECTION PREMIUM - 8 chevaux issus de l'indice Premium
        const selectionPremium = (Array.isArray(premium.selection_quinte) ? premium.selection_quinte : classement.slice(0,8).map(c=>c.numero)).map(Number).filter(Number.isFinite).slice(0,8);
        afficherListe("selection-premium", selectionPremium);
        afficherTableauLive(classement);


        // =====================================
        // EXPLICATION
        // =====================================

        afficherTexte(
            "explication-premium",

            classement
                .filter(c => selectionPremium.includes(Number(c.numero)))
                .sort((a,b)=>selectionPremium.indexOf(Number(a.numero))-selectionPremium.indexOf(Number(b.numero)))
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


        afficherTicket("derniere-minute-premium", derniere);
        if(premium.ticket_derniere_minute?.joker) afficherTexte("joker-derniere-minute", "Joker : " + premium.ticket_derniere_minute.joker);


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
            <p><strong>🔎 Méthode Premium :</strong> ${premium.methode || "lecture complémentaire de l'indice AZ"}</p>
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
// INFORMATIONS DE LA COURSE
// =====================================

function afficherInformationsCourse(data){

    const contenu =
        document.getElementById("contenu-premium");


    if(!contenu){
        return;
    }


    // Evite de créer le bloc plusieurs fois
    let bloc =
        document.getElementById("informations-course-premium");


    if(!bloc){

        bloc =
            document.createElement("section");

        bloc.id =
            "informations-course-premium";


        // Insertion juste avant la sélection du jour
        const selection =
            document.getElementById("selection-premium");


        if(selection){

            const parent =
                selection.parentElement;

            if(parent){

                parent.insertBefore(
                    bloc,
                    selection
                );

            }else{

                contenu.prepend(bloc);

            }

        }else{

            contenu.prepend(bloc);

        }

    }


    // =====================================
    // DONNEES
    // =====================================

    const course =
        data.course || "Course du jour";

    const date =
        formaterDateCourse(data.date);

    const reunion =
        data.reunion || "";

    const numeroCourse =
        data.course_numero || "";

    const hippodrome =
        data.hippodrome || "";

    const discipline =
        data.discipline || "";

    const distance =
        data.distance
            ? `${data.distance} m`
            : "";


    // =====================================
    // AFFICHAGE
    // =====================================

    bloc.innerHTML = `

        <div class="course-premium-header">

            <div class="course-premium-titre">
                🏇 ${echapperHTML(course)}
            </div>

            ${
                date
                ? `
                <div class="course-premium-date">
                    📅 ${echapperHTML(date)}
                </div>
                `
                : ""
            }

            <div class="course-premium-details">

                ${
                    hippodrome
                    ? `
                    <span>
                        📍 ${echapperHTML(hippodrome)}
                    </span>
                    `
                    : ""
                }

                ${
                    reunion || numeroCourse
                    ? `
                    <span>
                        🏁 ${echapperHTML(
                            `${reunion}${numeroCourse ? " — " + numeroCourse : ""}`
                        )}
                    </span>
                    `
                    : ""
                }

                ${
                    discipline
                    ? `
                    <span>
                        🐎 ${echapperHTML(discipline)}
                    </span>
                    `
                    : ""
                }

                ${
                    distance
                    ? `
                    <span>
                        📏 ${echapperHTML(distance)}
                    </span>
                    `
                    : ""
                }

            </div>

        </div>

    `;


    // =====================================
    // STYLE LOCAL
    // Ne dépend pas d'une modification
    // obligatoire de style.css
    // =====================================

    bloc.style.width =
        "100%";

    bloc.style.maxWidth =
        "100%";

    bloc.style.boxSizing =
        "border-box";

    bloc.style.margin =
        "0 0 20px 0";

    bloc.style.textAlign =
        "center";


    const header =
        bloc.querySelector(
            ".course-premium-header"
        );


    if(header){

        header.style.width =
            "100%";

        header.style.boxSizing =
            "border-box";

        header.style.padding =
            "16px 12px";

        header.style.borderRadius =
            "16px";

        header.style.marginBottom =
            "8px";

        header.style.background =
            "#ffffff";

        header.style.border =
            "2px solid #d4af37";

        header.style.overflow =
            "hidden";

    }


    const titre =
        bloc.querySelector(
            ".course-premium-titre"
        );


    if(titre){

        titre.style.fontSize =
            "20px";

        titre.style.fontWeight =
            "700";

        titre.style.lineHeight =
            "1.3";

        titre.style.marginBottom =
            "8px";

    }


    const dateElement =
        bloc.querySelector(
            ".course-premium-date"
        );


    if(dateElement){

        dateElement.style.fontSize =
            "16px";

        dateElement.style.fontWeight =
            "600";

        dateElement.style.marginBottom =
            "10px";

    }


    const details =
        bloc.querySelector(
            ".course-premium-details"
        );


    if(details){

        details.style.display =
            "flex";

        details.style.flexWrap =
            "wrap";

        details.style.justifyContent =
            "center";

        details.style.gap =
            "6px 12px";

        details.style.fontSize =
            "14px";

        details.style.lineHeight =
            "1.5";

    }

}


// =====================================
// FORMATAGE DATE
// =====================================

function formaterDateCourse(date){

    if(!date){
        return "";
    }


    const texte =
        String(date);


    const correspondance =
        texte.match(
            /^(\d{4})-(\d{2})-(\d{2})$/
        );


    if(!correspondance){

        return texte;

    }


    const annee =
        correspondance[1];

    const mois =
        correspondance[2];

    const jour =
        correspondance[3];


    const moisNoms = [

        "janvier",
        "février",
        "mars",
        "avril",
        "mai",
        "juin",
        "juillet",
        "août",
        "septembre",
        "octobre",
        "novembre",
        "décembre"

    ];


    const indexMois =
        Number(mois) - 1;


    if(
        indexMois < 0 ||
        indexMois > 11
    ){

        return texte;

    }


    return `${jour} ${moisNoms[indexMois]} ${annee}`;

}


// =====================================
// PROTECTION AFFICHAGE HTML
// =====================================

function echapperHTML(texte){

    return String(texte)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

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


    zone.style.width =
        "100%";

    zone.style.maxWidth =
        "100%";

    zone.style.minWidth =
        "0";

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
// TABLEAU LIVE DES PARTANTS
// =====================================

function afficherTableauLive(classement){
    const zone=document.getElementById("all-horses");
    if(!zone) return;

    if(!Array.isArray(classement) || !classement.length){
        zone.innerHTML='<tr><td colspan="5">Données indisponibles</td></tr>';
        return;
    }

    zone.innerHTML=classement.map(c=>{
        const np=Boolean(c.non_partant || c.statut === "NON_PARTANT");
        return `<tr class="${np ? "non-partant" : ""}">
            <td>${c.rang ?? "-"}</td>
            <td><strong>${echapperHTML(c.numero ?? "-")}</strong></td>
            <td>${echapperHTML(c.nom ?? "-")}</td>
            <td>${Number(c.indice_az ?? 0).toFixed(2)}</td>
            <td>${c.confiance ?? 0}%</td>
        </tr>`;
    }).join("");
}

function initialiserTableauLive(){
    const bouton=document.getElementById("btn-toggle-tableau");
    const conteneur=document.getElementById("conteneur-tableau");
    if(!bouton || !conteneur) return;

    bouton.addEventListener("click",()=>{
        const ouvert=getComputedStyle(conteneur).display !== "none";
        conteneur.style.display=ouvert ? "none" : "block";
        bouton.textContent=ouvert
            ? "📊 Afficher le Tableau des Partants (Live)"
            : "📊 Masquer le Tableau des Partants (Live)";
    });
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


    
