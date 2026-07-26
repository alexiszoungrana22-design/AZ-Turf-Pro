const API = "https://az-turf-pro.onrender.com/api/analyse";


async function chargerVIP(){

try{


const response = await fetch(API);


if(!response.ok){

throw new Error("Erreur API");

}


const data = await response.json();



const chevaux =
data.classement || data.chevaux || [];




// BASE VIP

const baseBox =
document.getElementById("base-vip");


if(baseBox && chevaux.length){


baseBox.innerHTML = `

<div class="vip-choice">

⭐ Base 1 :
<strong>
N°${chevaux[0].numero} - ${chevaux[0].nom}
</strong>

</div>


<div class="vip-choice">

⭐ Base 2 :
<strong>
N°${chevaux[1].numero} - ${chevaux[1].nom}
</strong>

</div>

`;

}






// CHAMP REDUIT VIP


if(data.tickets && data.tickets.champ_reduit){


const bases =
data.tickets.champ_reduit.bases || [];


const complements =
data.tickets.champ_reduit.complements || [];




const base =
document.getElementById("vip-base");


if(base){

base.textContent =
bases.join(" - ");

}





const systeme =
document.getElementById("vip-systeme");


if(systeme){


systeme.textContent =

`${bases[0] || "X"} - X - ${bases[1] || "X"} - X - X / ${complements.join(" - ")}`;


}





const comp =
document.getElementById("vip-complements");


if(comp){

comp.textContent =
complements.join(" - ");

}



}







// CHEVAL SURVEILLE


const surveille =
document.getElementById("cheval-surveille");



if(surveille && chevaux[2]){


surveille.innerHTML = `

🎯 Cheval à surveiller :

<br>

<strong>
N°${chevaux[2].numero} - ${chevaux[2].nom}
</strong>

<br>

Indice AZ :
${chevaux[2].indice_az}

`;

}







// TICKET VIP


const ticket =
document.getElementById("ticket-vip");



if(ticket && data.tickets){


ticket.innerHTML = `


<p>
🏆 Quinté VIP :
<br>

<strong>
${data.tickets.quinte.join(" - ")}
</strong>

</p>


<p>
🥉 Tiercé VIP :
<br>

<strong>
${data.tickets.trio.join(" - ")}
</strong>

</p>


<p>
🔒 Champ réduit :
<br>

<strong>
${data.tickets.champ_reduit.bases.join(" - ")}
</strong>

/

<strong>
${data.tickets.champ_reduit.complements.join(" - ")}
</strong>

</p>


`;

}



}


catch(error){

console.log("Erreur VIP :",error);

}


}




document.addEventListener(
"DOMContentLoaded",
chargerVIP
);
