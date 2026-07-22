async function analyser(){

    const resultat = document.getElementById("resultat");

    resultat.innerHTML = "Analyse AZ Turf en cours...";

    try{

        const response = await fetch("http://127.0.0.1:8000/analyse");

        const data = await response.json();

        resultat.innerHTML = `
        <h3>Ticket conseillé</h3>
        <p>${data.message}</p>
        <p>Chevaux : ${data.chevaux.join(" - ")}</p>
        `;

    }catch(error){

        resultat.innerHTML =
        "Serveur AZ Turf non connecté";

    }

}
