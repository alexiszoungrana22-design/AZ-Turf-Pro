// ===============================
// AZ TURF PRO - VIP.JS COMPLET
// ===============================


const API = "https://az-turf-pro.onrender.com/api/analyse";


// ===============================
// CODE ACCES VIP
// ===============================


const CODE_VIP = "AZVIP2026";



function connexionVIP(){


    const champ =
    document.getElementById("code-vip");


    const message =
    document.getElementById("message-vip");



    if(!champ) return;



    const code =
    champ.value.trim();



    if(code === CODE_VIP){


        localStorage.setItem(
            "az_vip_access",
            "true"
        );


        window.location.href =
        "espace-vip.html";


    } else {


        if(message){

            message.innerHTML =
            "❌ Code VIP invalide";

            message.style.color =
            "red";

        }

    }


}





// ===============================
// VERIFICATION ACCES ESPACE VIP
// ===============================


function verifierAccesVIP(){


    const page =
    window.location.pathname;



    const acces =
    localStorage.getItem(
        "az_vip_access"
    );



    if(
        page.includes("espace-vip.html")
        &&
        acces !== "true"
    ){


        window.location.href =
        "vip.html";


    }


}




verifierAccesVIP();






// ===============================
// CHARGEMENT DES DONNEES VIP
// ===============================


async function chargerVIP(){


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




// ===============================
// BASE DU JOUR
// ===============================


const baseBox =
document.getElementById("base-vip");



if(baseBox && chevaux.length){


baseBox.innerHTML = `


<div class="vip-choice">

⭐ Base 1 :

<strong>

N°${chevaux[0].numero}
-
${chevaux[0].nom || ""}

</strong>

</div>



<div class="vip-choice">

⭐ Base 2 :

<strong>

N°${chevaux[1]?.numero || "-"}
-
${chevaux[1]?.nom || ""}

</strong>

</div>


`;

}







// ===============================
// CHAMP REDUIT
// ===============================


if(
data.tickets &&
data.tickets.vip &&
data.tickets.vip.champ_reduit
){


const champ =
data.tickets.vip.champ_reduit;



const bases =
champ.bases || [];



const complements =
champ.complements || [];



const vipBase =
document.getElementById("vip-base");



if(vipBase){

vipBase.textContent =
bases.join(" - ") || "-";

}





const systeme =
document.getElementById("vip-systeme");



if(systeme){

systeme.textContent =
"Bases principales + compléments";

}





const comp =
document.getElementById("vip-complements");



if(comp){

comp.textContent =
complements.join(" - ") || "-";

}


}







// ===============================
// CHEVAL A SURVEILLER
// ===============================


const surveille =
document.getElementById(
"cheval-surveille"
);



if(
surveille &&
chevaux[2]
){


surveille.innerHTML = `


🎯 Cheval à surveiller :


<br>


<strong>

N°${chevaux[2].numero}
-
${chevaux[2].nom || ""}

</strong>


<br>


Indice :
${chevaux[2].indice_az || "-"}


`;

}








// ===============================
// TICKETS VIP
// ===============================


if(data.tickets){



const vip =
data.tickets.vip || {};





const ticket7 =
document.getElementById(
"vip-ticket-7"
);



if(ticket7){

ticket7.innerHTML =
vip.ticket_7
?
vip.ticket_7.join(" - ")
:
"-";

}





const ticket5 =
document.getElementById(
"vip-ticket-5"
);



if(ticket5){

ticket5.innerHTML =
vip.ticket_5
?
vip.ticket_5.join(" - ")
:
"-";

}







const champ =
document.getElementById(
"vip-champ"
);



if(champ && vip.champ_reduit){


champ.innerHTML =
vip.champ_reduit.format
||
"-";


}






const gagnant =
document.getElementById(
"couple-gagnant"
);



if(gagnant){

gagnant.innerHTML =
data.tickets.couple_gagnant
?
data.tickets.couple_gagnant.join(" - ")
:
"-";

}





const place =
document.getElementById(
"couple-place"
);



if(place){

place.innerHTML =
data.tickets.couple_place
?
data.tickets.couple_place
.map(
c => c.join("-")
)
.join("<br>")
:
"-";

}





const ticket =
document.getElementById(
"ticket-vip"
);



if(ticket){


ticket.innerHTML = `


<p>
🏆 Quinté :
<br>

<strong>
${
data.tickets.quinte
?
data.tickets.quinte.join(" - ")
:
"-"
}

</strong>

</p>



<p>
🥉 Tiercé :
<br>

<strong>
${
data.tickets.trio
?
data.tickets.trio.join(" - ")
:
"-"
}

</strong>

</p>


`;


}



}



}



catch(error){


console.log(
"Erreur VIP :",
error
);


}



}





document.addEventListener(
"DOMContentLoaded",
chargerVIP
);
