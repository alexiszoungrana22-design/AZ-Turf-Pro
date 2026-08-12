// ===============================
// AZ TURF PRO - AFFICHAGE TICKETS
// Compatible ticket.html + API Premium
// ===============================


const API_URL =
"https://az-turf-pro.onrender.com/api/analyse";



document.addEventListener(
"DOMContentLoaded",
chargerTickets
);




async function chargerTickets(){


try{


const response = await fetch(API_URL);



if(!response.ok){

throw new Error("Erreur API");

}



const data = await response.json();



console.log(
"JSON AZ Turf :",
data
);



const tickets =
data.tickets || {};



const gratuit =
tickets.gratuit || {};



const premium =
tickets.premium || {};




// ===============================
// GRATUIT
// ===============================


afficherListe(
"quinte",
gratuit.quinte
);



afficherListe(
"couple-place",
gratuit.couple_place
);




// ===============================
// PREMIUM
// ===============================


afficherListe(
"premium-quinte",
premium.quinte
);



afficherListe(
"premium-quarte",
premium.quarte
);



afficherListe(
"premium-trio",
premium.trio
);




// Couplé gagnant/placé Premium

const couple =
document.getElementById(
"couple-gagnant-place"
);



if(
couple
&&
premium.couple_gagnant_place
){


couple.innerHTML =

premium.couple_gagnant_place
.map(
c => c.join("-")
)
.join(" | ");


}




// Champ réduit

const champ =
document.getElementById(
"champ-reduit"
);



if(
champ
&&
premium.champ_reduit
){


champ.textContent =

premium.champ_reduit.format
+
" | Bases : "
+
premium.champ_reduit.bases.join("-")
+
" | Compléments : "
+
premium.champ_reduit.complements.join("-");


}




// Dernière minute

const derniere =
document.getElementById(
"derniere-minute"
);



if(
derniere
&&
premium.ticket_derniere_minute
){


derniere.textContent =

premium.ticket_derniere_minute.format;


}




// Message Premium

const message =
document.getElementById(
"message-fin"
);



if(message){


message.textContent =

premium.message_fin || "";


}



}

catch(error){


console.error(
"Erreur affichage tickets :",
error
);


}



}





function afficherListe(id, liste){


const element =
document.getElementById(id);



if(!element){

return;

}



if(
!liste
||
liste.length === 0
){


element.textContent =
"Non disponible";


return;

}




if(Array.isArray(liste[0])){


element.textContent =

liste
.map(
c => c.join("-")
)
.join(" | ");


}

else{


element.textContent =

liste.join(" - ");


}



}
// ===============================
// GESTION DU BOUTON ET DU TABLEAU DES PARTANTS
// ===============================

document.addEventListener("DOMContentLoaded", () => {
    const btnToggle = document.getElementById("btn-toggle-tableau");
    const conteneurTableau = document.getElementById("conteneur-tableau");

    if (btnToggle && conteneurTableau) {
        btnToggle.addEventListener("click", () => {
            // Si le tableau est masqué, on l'affiche et on charge les données
            if (conteneurTableau.style.display === "none") {
                conteneurTableau.style.display = "block";
                btnToggle.innerHTML = "📊 Masquer le Tableau des Partants";
                btnToggle.style.background = "#ef4444"; // Passe en rouge pour fermer

                // Fonction qui charge les données de l'API (si ce n'est pas déjà fait)
                chargerTableauPartants();
            } else {
                // Si le tableau est affiché, on le masque
                conteneurTableau.style.display = "none";
                btnToggle.innerHTML = "📊 Afficher le Tableau des Partants (Live)";
                btnToggle.style.background = "#10b981"; // Repasse en vert
            }
        });
    }
});

// Fonction de remplissage du tableau (SANS AUCUN PRÉFIXE NA / N°)
function chargerTableauPartants() {
    const tableau = document.getElementById("all-horses");
    if(!tableau) return;

    // Simulation ou appel de ton API existante (remplace par tes données)
    // Exemple avec ta variable "classement" :
    if (typeof classement !== 'undefined' && Array.isArray(classement)) {
        tableau.innerHTML = "";
        classement.forEach(cheval => {
            const rang = cheval.rang ?? "-";
            const numero = cheval.numero ?? "-"; // Uniquement le chiffre (ex: 1, 12...)
            const nom = cheval.nom || "-";
            const indice = cheval.indice_az ? Math.round(cheval.indice_az) : "-";
            const confiance = cheval.confiance ? cheval.confiance + " %" : "-";

            tableau.innerHTML += `
                <tr style="border-bottom: 1px solid #374151;">
                    <td style="padding: 12px;"><strong>${rang}</strong></td>
                    <td style="padding: 12px;"><strong>${numero}</strong></td>
                    <td style="padding: 12px;">${nom}</td>
                    <td style="padding: 12px;"><span style="background: #1f2937; padding: 4px 8px; border-radius: 4px; color: #10b981; font-weight: bold;">${indice}</span></td>
                    <td style="padding: 12px;">${confiance}</td>
                </tr>
            `;
        });
    }
}
