const API_URL =
"https://az-turf-pro.onrender.com/analyse";



// disparition écran démarrage

window.addEventListener("load",()=>{

setTimeout(()=>{

document.getElementById("splash").style.display="none";

},2500);


});




const bouton=document.getElementById("analyse");



if(bouton){


bouton.addEventListener("click",async()=>{


document.getElementById("chevaux").innerHTML=

"⏳ Analyse AZ en cours...";



try{


const response=await fetch(API_URL);


const data=await response.json();



afficherResultats(data);



}

catch(error){


document.getElementById("chevaux").innerHTML=

"❌ Erreur connexion API";


console.log(error);


}


});


}





function afficherResultats(data){


let chevaux=data.chevaux;


if(!chevaux){

return;

}



let html="";



chevaux.forEach((cheval,index)=>{


html+=`

<div class="cheval">

<strong>

${index+1} 🏇 N°${cheval.numero}

</strong>

<br>

Indice AZ :

<b>${cheval.indice_az}</b>

<br>

Confiance :

<span class="confiance">

${cheval.confiance} %

</span>

<br>

Catégorie :

${cheval.type}


</div>

`;


});



document.getElementById("chevaux").innerHTML=html;




let premier=chevaux[0];


document.getElementById("favori").innerHTML=

`

🏇 Cheval N°${premier.numero}

<br>

Indice AZ : ${premier.indice_az}

<br>

Confiance : ${premier.confiance} %

`;




let ticket=chevaux

.slice(0,5)

.map(c=>c.numero)

.join(" - ");



document.getElementById("ticket").innerHTML=

"🎫 Quinté conseillé : "+ticket;



}
