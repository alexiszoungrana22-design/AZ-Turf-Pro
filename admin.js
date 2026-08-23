// =====================================
// AZ TURF PRO
// ADMIN JS
// Version 5
// =====================================


const API_BASE =
"https://az-turf-pro.onrender.com/api";


const API_ANALYSE =
API_BASE + "/analyse";


const API_PREMIUM =
API_BASE + "/premium";


const API_ACTIVATION =
API_BASE + "/admin/valider-reference";


const API_STATISTIQUES =
API_BASE + "/admin/statistiques";


const API_ABONNEMENTS =
API_BASE + "/admin/abonnements";

function getAdminKey(){
    return sessionStorage.getItem("AZ_TURF_ADMIN_API_KEY") || "";
}

function enregistrerCleAdmin(){
    const input = document.getElementById("admin-api-key");
    const key = input ? input.value.trim() : "";
    if(!key){ alert("Veuillez saisir la clé administrateur."); return; }
    sessionStorage.setItem("AZ_TURF_ADMIN_API_KEY", key);
    if(input) input.value = "";
    alert("Clé administrateur enregistrée pour cette session.");
    actualiserAdmin();
}

function headersAdmin(extra={}){
    return Object.assign({"X-Admin-Key": getAdminKey()}, extra);
}





document.addEventListener(
"DOMContentLoaded",
initialiserAdmin
);





// =====================================
// INITIALISATION ADMIN
// =====================================

async function initialiserAdmin(){

    await verifierAPI();

    await chargerStatistiquesAdmin();

    await chargerAbonnements();

}







// =====================================
// FORMAT DATE
// =====================================

function formaterDate(date){

    if(!date){

        return "Non définie";

    }


    try{

        const d =
        new Date(date);


        return d.toLocaleDateString("fr-FR")
        +
        " à "
        +
        d.toLocaleTimeString(
            "fr-FR",
            {
                hour:"2 chiffres",
                minute:"2 chiffres"
            }
        );


    }catch{

        return date;

    }

}







// =====================================
// VERIFICATION API
// =====================================

async function verifierAPI(){


const etat =
document.getElementById(
"etat-api"
);



try{


const response =
await fetch(API_ANALYSE);



if(!response.ok){

throw new Error(
"API indisponible"
);

}



await response.json();



if(etat){

etat.innerHTML =
"✅ Connectée";

}



}



catch(error){


console.error(
"Erreur API :",
error
);



if(etat){

etat.innerHTML =
"❌ Hors ligne";

}


}

}







// =====================================
// STATISTIQUES ADMIN
// =====================================

async function chargerStatistiquesAdmin(){

    const champs = [
        "total-abonnements",
        "nombre-premium",
        "paiements-attente",
        "abonnements-expire"
    ];

    const afficher = (valeur) => {
        champs.forEach((id) => {
            const element = document.getElementById(id);
            if (element) element.textContent = valeur;
        });
    };

    const key = getAdminKey();
    if(!key){
        afficher("🔐 Clé requise");
        return;
    }

    try{
        const response = await fetch(
            API_STATISTIQUES,
            {headers: headersAdmin()}
        );

        let data = {};
        try { data = await response.json(); } catch (_) {}

        if(!response.ok){
            const message = response.status === 401
                ? "🔒 Non autorisé"
                : response.status === 503
                    ? "⚠️ Clé serveur indisponible"
                    : "⚠️ Indisponible";
            afficher(message);
            console.warn("Statistiques admin refusées:", response.status, data.detail || "");
            return;
        }

        afficher("0");
        document.getElementById("total-abonnements").textContent = Number.isFinite(Number(data.total)) ? data.total : 0;
        document.getElementById("nombre-premium").textContent = Number.isFinite(Number(data.actifs)) ? data.actifs : 0;
        document.getElementById("paiements-attente").textContent = Number.isFinite(Number(data.en_attente)) ? data.en_attente : 0;
        document.getElementById("abonnements-expire").textContent = Number.isFinite(Number(data.expires)) ? data.expires : 0;

    } catch(error){
        console.error("Erreur statistiques :", error);
        afficher("⚠️ Erreur");
    }
}







// =====================================
// LISTE ABONNEMENTS
// =====================================

async function chargerAbonnements(){

    const liste = document.getElementById("liste-abonnements");
    const key = getAdminKey();

    if(!key){
        if(liste) liste.textContent = "🔐 Clé administrateur requise";
        return;
    }

    try{
        const response = await fetch(
            API_ABONNEMENTS,
            {headers: headersAdmin()}
        );

        let data = {};
        try { data = await response.json(); } catch (_) {}

        if(!response.ok){
            if(liste){
                liste.textContent = response.status === 401
                    ? "🔒 Accès administrateur refusé"
                    : "⚠️ Données administrateur indisponibles";
            }
            return;
        }



// La liste est initialisée au début de chargerAbonnements().



if(!liste){

return;

}



liste.innerHTML = "";



if(
!data.abonnements ||
data.abonnements.length === 0
){


liste.innerHTML =
"Aucun abonnement";


return;


}



data.abonnements.forEach(
(abonnement)=>{


liste.innerHTML += `

<div class="abonnement">

<p>
📱 ${abonnement.telephone}
</p>

<p>
🎟️ Offre :
${abonnement.offre}
</p>

<p>
Statut :
<strong>
${abonnement.statut}
</strong>
</p>

<p>
📅 Fin :
${formaterDate(abonnement.date_fin)}
</p>


</div>

`;



}

);



}



catch(error){

console.error(
"Erreur abonnements :",
error
);

}

}









// =====================================
// VERIFICATION PREMIUM
// =====================================

async function verifierUtilisateurPremium(){


const telephone =
document.getElementById(
"telephone-premium"
).value.trim();



const resultat =
document.getElementById(
"resultat-premium"
);



if(!telephone){


resultat.innerHTML =
"⚠️ Veuillez entrer un numéro";


return;

}





try{


const response =
await fetch(

API_PREMIUM
+
"/"
+
encodeURIComponent(telephone)

);



const data =
await response.json();




if(response.ok){


resultat.innerHTML = `

✅ Statut :
<strong>${data.statut}</strong>

<br>

📅 Fin :
${formaterDate(data.date_fin)}

`;



}else{


resultat.innerHTML =
"❌ Utilisateur introuvable";


}



}



catch(error){


console.error(error);


resultat.innerHTML =
"❌ Erreur connexion API";


}



}









// =====================================
// ACTIVATION PREMIUM
// =====================================

async function activerPremium(){



const telephone =
document.getElementById(
"activation-telephone"
).value.trim();



const reference =
document.getElementById(
"activation-reference"
).value.trim();



const resultat =
document.getElementById(
"resultat-activation"
);





if(!telephone || !reference){


resultat.innerHTML =
"⚠️ Téléphone et référence obligatoires";


return;

}





try{



const response =

await fetch(

API_ACTIVATION,

{

method:"POST",

headers: headersAdmin({"Content-Type":"application/json"}),


body:JSON.stringify({

telephone:telephone,

reference:reference

})


}

);





const data =
await response.json();





if(response.ok){


resultat.innerHTML = `

✅ ${data.message}

<br>

Statut :
${data.statut}

<br>

Fin :
${formaterDate(data.date_fin)}

`;



await chargerStatistiquesAdmin();

await chargerAbonnements();



}else{


resultat.innerHTML =
"❌ Activation impossible";


}



}



catch(error){


console.error(error);


resultat.innerHTML =
"❌ Erreur connexion API";


}



  }
