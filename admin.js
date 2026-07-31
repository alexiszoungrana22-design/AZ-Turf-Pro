// =====================================
// AZ TURF PRO
// ADMIN JS
// Version 1
// =====================================


const API_ANALYSE =
"https://az-turf-pro.onrender.com/api/analyse";



document.addEventListener(
"DOMContentLoaded",
verifierAPI
);




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




// Préparation statistiques

chargerStatistiques(data);



}



catch(error){


console.error(
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
"Module paiement à connecter";

}



}
// =====================================
// VERIFICATION PREMIUM ADMIN
// =====================================


async function verifierUtilisateurPremium(){


const telephone =
document.getElementById(
"telephone-premium"
).value;



const resultat =
document.getElementById(
"resultat-premium"
);



if(!telephone){

resultat.innerHTML =
"⚠️ Entrez un numéro";

return;

}



try{


const response =

await fetch(

"https://az-turf-pro.onrender.com/api/premium/"
+
encodeURIComponent(telephone)

);



const data =
await response.json();



console.log(
"Premium:",
data
);



resultat.innerHTML =

JSON.stringify(data);



}


catch(error){


console.error(error);


resultat.innerHTML =
"❌ Erreur de connexion";


}


}
