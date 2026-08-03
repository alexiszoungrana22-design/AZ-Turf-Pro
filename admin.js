// =====================================
// AZ TURF PRO
// ADMIN JS
// Version 4
// =====================================


const API_BASE =
"https://az-turf-pro.onrender.com/api";


const API_ANALYSE =
API_BASE + "/analyse";


const API_PREMIUM =
API_BASE + "/premium";


const API_ACTIVATION =
API_BASE + "/activation";


const API_STATISTIQUES =
API_BASE + "/admin/statistiques";


const API_ABONNEMENTS =
API_BASE + "/admin/abonnements";





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



const data =
await response.json();



console.log(
"API AZ Turf :",
data
);



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
// CHARGEMENT STATISTIQUES ADMIN
// =====================================

async function chargerStatistiquesAdmin(){


try{


const response =
await fetch(
API_STATISTIQUES
);



const data =
await response.json();



console.log(
"Statistiques admin :",
data
);



const total =
document.getElementById(
"total-abonnements"
);



const actifs =
document.getElementById(
"nombre-premium"
);



const attente =
document.getElementById(
"paiements-attente"
);



const expires =
document.getElementById(
"abonnements-expire"
);




if(total){

total.innerHTML =
data.total;

}



if(actifs){

actifs.innerHTML =
data.actifs;

}



if(attente){

attente.innerHTML =
data.en_attente;

}



if(expires){

expires.innerHTML =
data.expires;

}



}



catch(error){


console.error(
"Erreur statistiques :",
error
);


}

}








// =====================================
// LISTE DES ABONNEMENTS
// =====================================


async function chargerAbonnements(){


try{


const response =
await fetch(
API_ABONNEMENTS
);



const data =
await response.json();



console.log(
"Abonnements :",
data
);



const liste =
document.getElementById(
"liste-abonnements"
);



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
Offre :
${abonnement.offre}
</p>

<p>
Statut :
${abonnement.statut}
</p>

<p>
Fin :
${abonnement.date_fin}
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
// VERIFICATION UTILISATEUR PREMIUM
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



console.log(
"Résultat Premium :",
data
);





if(response.ok){


resultat.innerHTML = `

✅ Vérification terminée

<br>

${JSON.stringify(data)}

`;



}else{


resultat.innerHTML =

"❌ Utilisateur Premium introuvable";


}



}



catch(error){


console.error(
"Erreur Premium :",
error
);



resultat.innerHTML =

"❌ Erreur de connexion API";


}



}









// =====================================
// ACTIVATION PREMIUM ADMIN
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

headers:{

"Content-Type":
"application/json"

},


body:JSON.stringify({

telephone:telephone,

reference:reference

})


}

);






const data =

await response.json();



console.log(
"Activation Premium :",
data
);





if(response.ok){


resultat.innerHTML = `

✅ ${data.message}

<br>

Statut :
${data.statut}

<br>

Fin :
${data.date_fin}

`;



await chargerStatistiquesAdmin();

await chargerAbonnements();



}else{


resultat.innerHTML =

"❌ Activation impossible";


}



}



catch(error){


console.error(
"Erreur activation :",
error
);



resultat.innerHTML =

"❌ Erreur connexion API";


}



  }
