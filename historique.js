const API = "https://az-turf-pro.onrender.com/api/analyse";


async function chargerHistorique(){


try{


const response = await fetch(API);



if(!response.ok){

throw new Error("Erreur API");

}



const data = await response.json();




const classement =
data.classement || data.chevaux || [];




const body =
document.getElementById("historique-body");



if(body){


body.innerHTML = "";



const date = new Date()
.toLocaleDateString("fr-FR");



const favori =
classement[0]
? `N°${classement[0].numero} - ${classement[0].nom}`
: "-";



const ticket =
data.tickets && data.tickets.quinte
? data.tickets.quinte.join(" - ")
: "-";





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
${ticket}
</td>


<td>
En attente
</td>


</tr>


`;



}







// Statistiques simples


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
