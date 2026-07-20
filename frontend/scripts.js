console.log("AZ Turf-Pro V1 chargé");


const buttons = document.querySelectorAll("button");


buttons.forEach(button => {

    button.addEventListener("click", () => {

        document.querySelector(".ticket-result").innerHTML =
        "Ticket sélectionné : " + button.innerHTML;

    });

});
