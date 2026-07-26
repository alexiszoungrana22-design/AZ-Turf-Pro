alert("Script AZ chargé");
const API = "https://az-turf-pro.onrender.com/api/analyse";


const tableBody = document.getElementById("table-body");
const btnRefresh = document.getElementById("btn-refresh");

const kpiFavorite = document.getElementById("kpi-favorite");
const kpiConfidence = document.getElementById("kpi-confidence");
const kpiOutsider = document.getElementById("kpi-outsider");

const topCombination = document.getElementById("top-combination");
const ticketsBox = document.getElementById("tickets");


async function chargerAnalyse() {

    try {

        alert("Je lance API : " + API);

const response = await fetch(API);
alert(JSON.stringify(data.chevaux));
alert("Réponse API : " + response.status);
        }

        let data;

try {
    data = await response.json();
    alert("JSON reçu");
}
catch(e) {
    alert("Erreur JSON : " + e);
}

        // Informations course

        const metaCourse = document.getElementById("meta-course");
        if (metaCourse)
            metaCourse.textContent = data.course || "-";


        const metaHippodrome = document.getElementById("meta-hippodrome");
        if (metaHippodrome)
            metaHippodrome.textContent = data.hippodrome || "-";


        const metaDiscipline = document.getElementById("meta-discipline");
        if (metaDiscipline)
            metaDiscipline.textContent = data.discipline || "-";


        const metaDistance = document.getElementById("meta-distance");
        if (metaDistance)
            metaDistance.textContent =
            (data.distance_course || "-") + " m";


        const metaPartants = document.getElementById("meta-partants");
        if (metaPartants)
            metaPartants.textContent = data.partants || "-";



        // Liste chevaux

        const chevaux = data.classement || data.chevaux || [];


        if (tableBody) {

            tableBody.innerHTML = "";


            chevaux.forEach((cheval,index)=>{


                const tr = document.createElement("tr");


                tr.innerHTML = `

                <td>
                    <span class="num-badge">
                    ${cheval.numero || "-"}
                    </span>
                </td>


                <td>
                    <strong>
                    ${cheval.nom || "Cheval"}
                    </strong>
                </td>


                <td>
                    ${cheval.jockey || "-"}
                </td>


                <td>
                    ${cheval.entraineur || "-"}
                </td>


                <td>
                    ${cheval.forme || cheval.musique || "-"}
                </td>


                <td>

                <div class="score-bar-container">

                    <span>
                    ${cheval.indice_az || cheval.score || 0}
                    </span>


                    <div class="score-bar">

                        <div class="score-fill"
                        style="width:${Math.min(cheval.indice_az || 0,100)}%">
                        </div>

                    </div>

                </div>

                </td>


                <td>

                <span class="badge-rank ${
                    index === 0 ? "top1" :
                    index < 3 ? "top3" :
                    "outsider"
                }">

                ${cheval.rang || index+1}

                </span>

                </td>

                `;


                tableBody.appendChild(tr);

            });

        }



        // KPI

        if(chevaux.length){


            if(kpiFavorite)
                kpiFavorite.textContent =
                `${chevaux[0].numero || "-"} - ${chevaux[0].nom || "-"}`;


            if(kpiConfidence)
                kpiConfidence.textContent =
                (chevaux[0].confiance || 88) + "%";



            const outsider =
            chevaux.find(c=>c.rang>=3)
            || chevaux[chevaux.length-1];


            if(kpiOutsider)
                kpiOutsider.textContent =
                `${outsider.numero || "-"} - ${outsider.nom || "-"}`;

        }




        // Pronostic

        if(data.tickets && topCombination){


            topCombination.innerHTML = `

            <div class="combo-pill">
            <span>Q+</span>
            ${data.tickets.quinte.join(" - ")}
            </div>


            <div class="combo-pill">
            <span>Q</span>
            ${data.tickets.quarte.join(" - ")}
            </div>


            <div class="combo-pill">
            <span>T</span>
            ${data.tickets.trio.join(" - ")}
            </div>

            `;

        }




        // Tickets détaillés

        if(data.tickets && ticketsBox){


            ticketsBox.innerHTML = `

            <p>
            🥇 Couplé gagnant :
            <strong>
            ${data.tickets.couple_gagnant.join(" - ")}
            </strong>
            </p>


            <p>
            🥈 Couplés placés :
            <br>
            ${data.tickets.couple_place
            .map(c=>c.join(" - "))
            .join("<br>")}
            </p>


            <p>
            🔒 Champ réduit :
            <br>

            Bases :
            <strong>
            ${data.tickets.champ_reduit.bases.join(" - ")}
            </strong>

            <br>

            Compléments :
            <strong>
            ${data.tickets.champ_reduit.complements.join(" - ")}
            </strong>

            </p>

            `;

        }



    }

    catch(error){

        console.log("Erreur API :", error);

    }

}





if(btnRefresh){

    btnRefresh.onclick = ()=>{

        chargerAnalyse();

    };

}



document.addEventListener(
"DOMContentLoaded",
chargerAnalyse
);
