// =================================
// AZ Turf Pro - Historique
// =================================


const API = "https://az-turf-pro.onrender.com/api/analyse";



async function chargerHistorique(){


try{


const response = await fetch(API);



if(!response.ok){

throw new Error("Erreur API");

}



const data = await response.json();





const classement =
data.classement ||
data.chevaux ||
[];





const body =
document.getElementById("historique-body");





if(body){


body.innerHTML = "";



const date =
new Date()
.toLocaleDateString("fr-FR");




const selection =

classement
.slice(0,7)
.map(cheval => cheval.numero)
.join(" - ");





body.innerHTML = `


<tr>


<td>
${date}
</td>



<td>
Course du jour
</td>



<td>
${selection || "-"}
</td>



<td>
En attente
</td>



<td>
À définir
</td>


</tr>


`;



}







// Statistiques


const total =
document.getElementById("total-courses");


if(total){

total.textContent = "1";

}






const resultats =
document.getElementById("favoris-gagnants");


if(resultats){

resultats.textContent = "0";

}






const selections =
document.getElementById("tickets-reussis");


if(selections){

selections.textContent = "0";

}






}


catch(error){


console.log(
"Erreur historique :",
error
);


}



}






document.addEventListener(
"DOMContentLoaded",
chargerHistorique
);
