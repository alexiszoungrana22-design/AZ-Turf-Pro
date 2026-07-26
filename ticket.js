const API = "https://az-turf-pro.onrender.com/api/analyse";



async function chargerTicket(){


try{


const response =
await fetch(API);



if(!response.ok){

throw new Error("Erreur API");

}



const data =
await response.json();





const tickets =
data.tickets || {};






// QUINTE


const quinte =
document.getElementById("quinte-ticket");



if(quinte){


quinte.innerHTML = `

<p>

<strong>
${tickets.quinte
? tickets.quinte.join(" - ")
: "-"
}

</strong>

</p>

`;

}







// TRIO


const trio =
document.getElementById("trio-ticket");



if(trio){


trio.innerHTML = `

<p>

<strong>
${tickets.trio
? tickets.trio.join(" - ")
: "-"
}

</strong>

</p>

`;

}








// CHAMP REDUIT


const champ =
document.getElementById("champ-ticket");



if(champ && tickets.champ_reduit){


const bases =
tickets.champ_reduit.bases || [];



const complements =
tickets.champ_reduit.complements || [];



champ.innerHTML = `


<p>
Base principale :
<strong>
${bases.join(" - ") || "-"}
</strong>
</p>


<p>
Compléments :
<strong>
${complements.join(" - ") || "-"}
</strong>
</p>


`;

}








// FAVORI ET CHEVAL SURVEILLE


const chevaux =
data.classement ||
data.chevaux ||
[];




const favori =
document.getElementById("ticket-favori");



if(favori && chevaux[0]){


favori.innerHTML = `

⭐ Favori du jour :

<strong>
N°${chevaux[0].numero}
${chevaux[0].nom || ""}
</strong>

`;

}







}


catch(error){


console.log(
"Erreur ticket :",
error
);


}


}





document.addEventListener(
"DOMContentLoaded",
chargerTicket
);
