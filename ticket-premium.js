const API =
"https://az-turf-pro.onrender.com/api/analyse";



async function chargerTicketPremium(){


try{


const response =
await fetch(API);



if(!response.ok){

throw new Error("Erreur API");

}



const data =
await response.json();




const chevaux =
data.classement ||
data.chevaux ||
[];





if(chevaux.length === 0){

throw new Error("Aucun cheval reçu");

}






// Sélection des 7 meilleurs AZ

const premium =
chevaux.slice(0,7);







// ============================
// SELECTION PREMIUM
// ============================


const selection =
document.getElementById(
"selection-premium"
);



if(selection){


selection.innerHTML =

premium.map(c =>

`
<strong>${c.numero}</strong>
${c.nom || "Cheval"}

`

).join(" - ");


}









// ============================
// QUINTE PREMIUM 6 CHEVAUX
// ============================


const quinte =
premium.slice(0,6)
.map(c=>c.numero)
.join(" - ");



document.getElementById(
"quinte-premium"
).textContent = quinte;









// ============================
// QUARTE PREMIUM 5 CHEVAUX
// ============================


const quarte =
premium.slice(0,5)
.map(c=>c.numero)
.join(" - ");



document.getElementById(
"quarte-premium"
).textContent = quarte;









// ============================
// TRIO PREMIUM 4 CHEVAUX
// ============================


const trio =
premium.slice(0,4)
.map(c=>c.numero)
.join(" - ");



document.getElementById(
"trio-premium"
).textContent = trio;









// ============================
// CHAMP REDUIT
// ============================


const champ =
premium.map(c=>c.numero)
.join(" - ");



document.getElementById(
"champ-premium"
).textContent = champ;









// ============================
// COUPLE GAGNANT
// ============================


const coupleGagnant =

premium
.slice(0,2)
.map(c=>c.numero)
.join(" - ");




document.getElementById(
"couple-gagnant"
).textContent = coupleGagnant;









// ============================
// COUPLE PLACE
// ============================


const couplePlace =

premium
.filter(c => c.confiance)
.sort(
(a,b)=>
b.confiance - a.confiance
)
.slice(0,2)
.map(c=>c.numero)
.join(" - ");




document.getElementById(
"couple-place"
).textContent = couplePlace;









// ============================
// ANALYSE PREMIUM
// ============================


const analyse =
document.getElementById(
"analyse-premium"
);



if(analyse){


const favori =
premium[0];


const outsider =
premium[5];



analyse.innerHTML = `


<p>
⭐ Base Premium :
<strong>
N°${favori.numero}
${favori.nom || ""}
</strong>
</p>



<p>
🔥 Cheval à surveiller :
<strong>
N°${outsider.numero}
${outsider.nom || ""}
</strong>
</p>



<p>
📊 Confiance :
<strong>
${favori.confiance || "-"} %
</strong>
</p>


`;



}





}

catch(error){


console.log(
"Erreur Ticket Premium :",
error
);


const zone =
document.getElementById(
"analyse-premium"
);



if(zone){

zone.innerHTML =
"❌ Impossible de charger le ticket Premium.";

}



}



}





document.addEventListener(

"DOMContentLoaded",

chargerTicketPremium

);
