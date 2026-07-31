// =====================================
// AZ TURF PRO
// ADMIN JS
// Version 3
// =====================================


const API_ANALYSE =
"https://az-turf-pro.onrender.com/api/analyse";


const API_PREMIUM =
"https://az-turf-pro.onrender.com/api/premium";


const API_ACTIVATION =
"https://az-turf-pro.onrender.com/api/activation";





document.addEventListener(
"DOMContentLoaded",
initialiserAdmin
);






// =====================================
// INITIALISATION ADMIN
// =====================================


async function initialiserAdmin(){

await verifierAPI();

}







// =====================================
// VERIFICATION API ANALYSE
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



chargerStatistiques(data);



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
// STATISTIQUES
// =====================================


function chargerStatistiques(data){


const premium =
document.getElementById(
"nombre-premium"
);



const attente =
document.getElementById(
"paiements-attente"
);



if(premium){

premium.innerHTML =
"Gestion Premium prête";

}



if(attente){

attente.innerHTML =
"Module paiement prêt";

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
