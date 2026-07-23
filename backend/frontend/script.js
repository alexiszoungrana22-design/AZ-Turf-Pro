const API_URL =
"https://az-turf-pro.onrender.com/analyse";



// Animation écran d'ouverture

window.addEventListener("load",()=>{

setTimeout(()=>{

document.getElementById("splash").style.display="none";

},3000);


});





const bouton = document.getElementById("analyse");


console.log("AZ Turf Pro chargé", bouton);



if(bouton){


bouton.addEventListener("click", async()=>{


document.getElementById("chevaux").innerHTML = `


<div class="loading">

🏇 Analyse AZ en cours...

<br><br>

<span>
Analyse de la forme...
</span>

<br>

<span>
Calcul indice AZ...
</span>

<br>

<span>
Création du ticket...
</span>


</div>


`;



try{


const response = await fetch(API_URL);


const data = await response.json();



afficherResultats(data);



}

catch(error){


document.getElementById("chevaux").innerHTML =

"❌ Erreur de connexion AZ Turf Pro";


console.log(error);


}



});


}





function afficherResultats(data){


let chevaux=data.chevaux;



if(!chevaux || chevaux.length===0){

document.getElementById("chevaux").innerHTML=
"Aucun cheval trouvé.";

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



document.getElementById("favori").innerHTML=`

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
