const API = "https://az-turf-pro.onrender.com/api/analyse";


async function chargerHistorique(){


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






const body =
document.getElementById("historique-body");



if(body){


body.innerHTML = "";



const date =
new Date()
.toLocaleDateString("fr-FR");



const favori =
chevaux[0]
?
"N°"+chevaux[0].numero+
" "+(chevaux[0].nom || "")
:
"-";





const selection =
data.tickets &&
data.tickets.quinte
?
data.tickets.quinte.join(" - ")
:
"-";






body.innerHTML = `

<tr>

<td>
${date}
</td>


<td>
Course du jour
</td>


<td>
${favori}
</td>


<td>
${selection}
</td>


<td>
En attente
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




const favoris =
document.getElementById("favoris-gagnants");


if(favoris){

favoris.textContent = "0";

}





const tickets =
document.getElementById("tickets-reussis");


if(tickets){

tickets.textContent = "0";

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
