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

    // Les statistiques/abonnements exigent la clé admin : on ne les
    // charge qu'après connexion (voir connexionAdmin() dans admin.html),
    // ou immédiatement si une session admin est déjà active.
    if (window.AZAuth && window.AZAuth.isAdmin()) {
        await chargerStatistiquesAdmin();
        await chargerAbonnements();
    }

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


try{


const response =
await fetch(
API_STATISTIQUES,
{ headers: window.AZAuth.authHeaders() }
);



const data =
await response.json();



if(document.getElementById("total-abonnements"))
document.getElementById("total-abonnements").innerHTML =
data.total;



if(document.getElementById("nombre-premium"))
document.getElementById("nombre-premium").innerHTML =
data.actifs;



if(document.getElementById("paiements-attente"))
document.getElementById("paiements-attente").innerHTML =
data.en_attente;



if(document.getElementById("abonnements-expire"))
document.getElementById("abonnements-expire").innerHTML =
data.expires;



}



catch(error){

console.error(
"Erreur statistiques :",
error
);

}

}







// =====================================
// LISTE ABONNEMENTS
// =====================================

async function chargerAbonnements(){


try{


const response =
await fetch(
API_ABONNEMENTS,
{ headers: window.AZAuth.authHeaders() }
);



const data =
await response.json();



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
// VALIDATION PAIEMENT (avant activation)
// =====================================

async function validerPaiement(){
  const telephone = document.getElementById("validation-telephone").value.trim();
  const reference = document.getElementById("validation-reference").value.trim();
  const resultat = document.getElementById("resultat-validation");

  if (!telephone || !reference) {
    resultat.innerHTML = "⚠️ Téléphone et référence obligatoires";
    return;
  }

  try {
    const response = await fetch(
      API_BASE + "/admin/valider-paiement?telephone=" + encodeURIComponent(telephone) + "&reference=" + encodeURIComponent(reference),
      { method: "POST", headers: window.AZAuth.authHeaders() }
    );
    const data = await response.json();

    if (!response.ok) {
      resultat.innerHTML = "❌ " + (data.detail || "Erreur de validation");
      return;
    }

    resultat.innerHTML = "✅ Paiement validé. Le client peut maintenant activer avec cette référence.";
  } catch (erreur) {
    resultat.innerHTML = "❌ Erreur réseau : " + erreur.message;
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

headers:{

"Content-Type":
"application/json",
...window.AZAuth.authHeaders()

},


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
