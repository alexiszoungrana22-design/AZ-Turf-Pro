// ==========================================================
// AZ TURF PRO - TICKETS PREMIUM
// Accès administrateur direct
// Utilisateurs : vérification Premium côté serveur
// Données : /api/analyse
// ==========================================================

const API_ANALYSE =
    "https://az-turf-pro.onrender.com/api/analyse";

const API_PREMIUM =
    "https://az-turf-pro.onrender.com/api/premium/";


function badgeTendancePremium(cheval) {

    const signal = String((cheval && cheval.signal_marche) || "NEUTRE");
    const variation = cheval && cheval.variation_cote_pct;
    const pct = (typeof variation === "number" && variation !== 0)
        ? ` (${variation > 0 ? "+" : ""}${variation}%)`
        : "";

    if (signal.includes("SMART_MONEY")) return `🔥 Smart Money${pct}`;
    if (signal.includes("SOUTENU")) return `📈 Soutenu${pct}`;
    if (signal.includes("DELAISSE")) return `📉 Délaissé${pct}`;

    return "– Stable";

}


document.addEventListener("DOMContentLoaded", function () {

    initialiserBoutonTableau();

    verifierAccesPremium();

});


// ==========================================================
// 1. DETECTION DU MODE ADMINISTRATEUR
// ==========================================================

async function estAdministrateur() {
    const key = sessionStorage.getItem("AZ_TURF_ADMIN_API_KEY") || "";
    if (!key) return false;

    try {
        const reponse = await fetch(
            "https://az-turf-pro.onrender.com/api/admin/verification",
            {
                method: "GET",
                cache: "no-store",
                headers: {
                    "Accept": "application/json",
                    "X-Admin-Key": key
                }
            }
        );
        return reponse.ok;
    } catch (_) {
        return false;
    }
}


// ==========================================================
// 2. VERIFICATION ACCES PREMIUM
// ==========================================================

async function verifierAccesPremium() {

    const blocage =
        document.getElementById("message-blocage");

    const contenu =
        document.getElementById("contenu-premium");


    // ------------------------------------------------------
    // ADMINISTRATEUR
    // ------------------------------------------------------

    if (await estAdministrateur()) {

        console.log(
            "AZ Turf Pro : accès administrateur direct aux Tickets Premium."
        );

        if (blocage) {
            blocage.classList.add("zone-masquee");
            blocage.style.display = "none";
        }

        if (contenu) {
            contenu.classList.remove("zone-masquee");
            contenu.style.display = "";
        }

        // L'administrateur n'a PAS besoin
        // d'un abonnement Premium.
        await chargerTicketsPremium();

        return;
    }


    // ------------------------------------------------------
    // UTILISATEUR NORMAL
    // ------------------------------------------------------

    const telephone =
        localStorage.getItem("AZ_TURF_TELEPHONE");


    if (!telephone) {

        afficherBlocagePremium();

        return;
    }


    try {

        const reponse = await fetch(
            API_PREMIUM +
            encodeURIComponent(telephone),
            {
                method: "GET",
                cache: "no-store",
                headers: {
                    "Accept": "application/json"
                }
            }
        );


        let data = {};

        try {
            data = await reponse.json();
        } catch (_) {
            data = {};
        }


        if (
            reponse.ok &&
            data.statut === "ACTIF"
        ) {

            if (blocage) {
                blocage.classList.add("zone-masquee");
                blocage.style.display = "none";
            }

            if (contenu) {
                contenu.classList.remove("zone-masquee");
                contenu.style.display = "";
            }

            await chargerTicketsPremium();

        } else {

            afficherBlocagePremium();

        }


    } catch (error) {

        console.error(
            "Erreur vérification Premium :",
            error
        );

        afficherBlocagePremium();

    }

}


// ==========================================================
// 3. BLOCAGE UTILISATEUR NON PREMIUM
// ==========================================================

function afficherBlocagePremium() {

    const blocage =
        document.getElementById("message-blocage");

    const contenu =
        document.getElementById("contenu-premium");


    if (blocage) {

        blocage.classList.remove("zone-masquee");

        blocage.style.display = "block";

    }


    if (contenu) {

        contenu.classList.add("zone-masquee");

        contenu.style.display = "none";

    }

}


// ==========================================================
// 4. CHARGEMENT DES TICKETS PREMIUM
// ==========================================================

async function chargerTicketsPremium() {

    try {

        const reponse =
            await fetch(
                API_ANALYSE,
                {
                    method: "GET",
                    cache: "no-store",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );


        if (!reponse.ok) {

            throw new Error(
                "Erreur API analyse : " +
                reponse.status
            );

        }


        const data =
            await reponse.json();


        const tickets =
            data.tickets &&
            data.tickets.premium
                ? data.tickets.premium
                : {};


        const classement =
            Array.isArray(data.classement)
                ? data.classement
                : [];


        // ==================================================
        // SELECTION PREMIUM
        // ==================================================

        const selectionPremium =
            Array.isArray(tickets.selection_quinte)
                ? tickets.selection_quinte
                    .map(Number)
                    .filter(Number.isFinite)
                    .slice(0, 8)
                : [];


        injecter(
            "selection-premium",
            selectionPremium.join(" - "),
            true
        );


        // ==================================================
        // EXPLICATION PREMIUM
        // ==================================================

        const favori =
            classement.length
                ? classement[0]
                : null;


        injecter(
            "explication-premium",

            favori

                ? `Le n°${favori.numero} (${favori.nom || ""}) ressort en tête de l'analyse AZ avec un indice de ${Math.round(favori.indice_az || 0)} et une confiance de ${favori.confiance ?? "-"}%.`

                : "Analyse Premium basée sur les données de la course, la forme, la régularité et les indicateurs AZ.",

            false
        );


        // ==================================================
        // QUINTE PREMIUM
        // ==================================================

        const quintePremium =
            Array.isArray(tickets.quinte)
                ? tickets.quinte
                    .map(Number)
                    .filter(Number.isFinite)
                    .slice(0, 6)
                : [];


        injecter(
            "quinte-premium",
            quintePremium.join(" - "),
            true
        );


        // ==================================================
        // QUARTE PREMIUM
        // ==================================================

        const quartePremium =
            Array.isArray(tickets.quarte)
                ? tickets.quarte
                    .map(Number)
                    .filter(Number.isFinite)
                    .slice(0, 5)
                : [];


        injecter(
            "quarte-premium",
            quartePremium.join(" - "),
            true
        );


        // ==================================================
        // TRIO PREMIUM
        // ==================================================

        const trioPremium =
            Array.isArray(tickets.trio)
                ? tickets.trio
                    .map(Number)
                    .filter(Number.isFinite)
                    .slice(0, 3)
                : [];


        injecter(
            "trio-premium",
            trioPremium.join(" - "),
            true
        );


        // ==================================================
        // COUPLES PREMIUM
        // ==================================================

        const couples =
            Array.isArray(tickets.couple_gagnant_place)
                ? tickets.couple_gagnant_place
                : [];


        injecter(
            "couple-premium",

            couples
                .filter(c => Array.isArray(c))
                .map(c =>
                    c
                        .map(Number)
                        .filter(Number.isFinite)
                        .join("-")
                )
                .filter(Boolean)
                .join(" | "),

            true
        );


        // ==================================================
        // CHAMP REDUIT
        // ==================================================

        const champReduit =
            tickets.champ_reduit || {};


        injecter(
            "champ-reduit-premium",

            champReduit.format ||
            "Non disponible",

            true
        );


        // ==================================================
        // DERNIERE MINUTE
        // IMPORTANT :
        // elle vient du bloc dédié et n'est pas forcée
        // à reprendre le Quinté Premium.
        // ==================================================

        const derniereMinute =
            tickets.ticket_derniere_minute &&
            Array.isArray(
                tickets.ticket_derniere_minute.selection
            )

                ? tickets.ticket_derniere_minute.selection
                    .map(Number)
                    .filter(Number.isFinite)

                : [];


        injecter(
            "derniere-minute-premium",

            derniereMinute.length
                ? derniereMinute.join(" - ")
                : "Non disponible",

            true
        );


        // ==================================================
        // ANALYSE COMPLETE
        // ==================================================

        injecter(
            "analyse-premium",

            tickets.explication ||
            "Analyse AZ Turf Pro basée sur les données disponibles de la course.",

            false
        );


        // ==================================================
        // MESSAGE FINAL
        // ==================================================

        injecter(
            "message-premium",

            tickets.message_fin ||
            "🍀 Bonne chance ! Jouez avec discipline et responsabilité.",

            false
        );


        console.log(
            "AZ Turf Pro : Tickets Premium chargés.",
            {
                selection: selectionPremium,
                quinte: quintePremium,
                quarte: quartePremium,
                trio: trioPremium,
                derniereMinute
            }
        );


    } catch (error) {

        console.error(
            "Erreur chargement tickets Premium :",
            error
        );


        const zones = [
            "selection-premium",
            "quinte-premium",
            "quarte-premium",
            "trio-premium",
            "couple-premium",
            "champ-reduit-premium",
            "derniere-minute-premium"
        ];


        zones.forEach(function (id) {

            const zone =
                document.getElementById(id);

            if (zone) {

                zone.textContent =
                    "Données Premium indisponibles";

            }

        });

    }

}


// ==========================================================
// 5. FORMATAGE DES NUMEROS
// ==========================================================

function convertirEnPastilles(texte) {

    if (!texte) {
        return "";
    }


    const parties =
        String(texte).split("/");


    function convertir(chaine) {

        return String(chaine)

            .split(/[-,\s]+/)

            .map(item =>
                item.trim()
            )

            .filter(Boolean)

            .map(num => {

                if (!isNaN(num)) {

                    return `
                        <span class="numero-cheval">
                            ${String(num).padStart(2, "0")}
                        </span>
                    `;

                }


                if (
                    num.toUpperCase() === "X"
                ) {

                    return `
                        <span
                            class="numero-cheval"
                            style="background-color:#d97706;"
                        >
                            X
                        </span>
                    `;

                }


                return num;

            })

            .join(" ");

    }


    if (parties.length > 1) {

        return (

            convertir(parties[0]) +

            `
            <strong
                style="
                    font-size:20px;
                    color:#0f172a;
                    margin:0 6px;
                "
            >
                /
            </strong>
            ` +

            convertir(parties[1])

        );

    }


    return convertir(texte);

}


// ==========================================================
// 6. INJECTION SECURISEE
// ==========================================================

function injecter(
    id,
    contenu,
    estCombine
) {

    const element =
        document.getElementById(id);


    if (!element) {
        return;
    }


    if (estCombine) {

        element.innerHTML =
            convertirEnPastilles(
                contenu
            );

    } else {

        element.textContent =
            contenu || "";

    }

}


// ==========================================================
// 7. TABLEAU LIVE
// ==========================================================

function initialiserBoutonTableau() {

    const btnTableau =
        document.getElementById(
            "btn-toggle-tableau"
        );


    const conteneurTableau =
        document.getElementById(
            "conteneur-tableau"
        );


    if (
        !btnTableau ||
        !conteneurTableau
    ) {

        return;

    }


    btnTableau.addEventListener(
        "click",
        async function () {

            if (
                conteneurTableau
                    .classList
                    .contains("zone-masquee")
            ) {

                conteneurTableau
                    .classList
                    .remove(
                        "zone-masquee"
                    );


                btnTableau.innerText =
                    "❌ Masquer le Tableau Live";


                await chargerTableauLive();


            } else {

                conteneurTableau
                    .classList
                    .add(
                        "zone-masquee"
                    );


                btnTableau.innerText =
                    "📊 Afficher le Tableau des Partants (Live)";

            }

        }
    );

}


// ==========================================================
// 8. TABLEAU DES PARTANTS LIVE
// ==========================================================

async function chargerTableauLive() {

    const tableau =
        document.getElementById(
            "all-horses"
        );


    if (!tableau) {
        return;
    }


    tableau.innerHTML = `
        <tr>
            <td
                colspan="6"
                style="
                    text-align:center;
                    padding:15px;
                "
            >
                Chargement...
            </td>
        </tr>
    `;


    try {

        const reponse =
            await fetch(
                API_ANALYSE,
                {
                    method: "GET",
                    cache: "no-store",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );


        if (!reponse.ok) {

            throw new Error(
                "Erreur API analyse"
            );

        }


        const data =
            await reponse.json();


        const classement =
            Array.isArray(data.classement)
                ? data.classement
                : [];


        if (!classement.length) {

            tableau.innerHTML = `
                <tr>
                    <td
                        colspan="6"
                        style="
                            text-align:center;
                            padding:15px;
                        "
                    >
                        Classement indisponible.
                    </td>
                </tr>
            `;

            return;

        }


        tableau.innerHTML =
            classement
                .map(function (cheval) {

                    const rang =
                        cheval.rang ?? "-";


                    const numero =
                        cheval.numero ?? "-";


                    const nom =
                        cheval.nom || "-";


                    const indice =
                        cheval.indice_az !== null &&
                        cheval.indice_az !== undefined

                            ? Math.round(
                                cheval.indice_az
                            )

                            : "-";


                    const confiance =
                        cheval.confiance !== null &&
                        cheval.confiance !== undefined

                            ? cheval.confiance + " %"

                            : "-";


                    const tendance =
                        badgeTendancePremium(cheval);


                    return `
                        <tr>

                            <td style="padding:10px;">
                                <strong>
                                    ${rang}
                                </strong>
                            </td>

                            <td style="padding:10px;">
                                <strong>
                                    ${numero}
                                </strong>
                            </td>

                            <td style="padding:10px;">
                                ${nom}
                            </td>

                            <td style="padding:10px;">
                                ${indice}
                            </td>

                            <td style="padding:10px;">
                                ${confiance}
                            </td>

                            <td style="padding:10px;">
                                ${tendance}
                            </td>

                        </tr>
                    `;

                })
                .join("");


    } catch (error) {

        console.error(
            "Erreur tableau live :",
            error
        );


        tableau.innerHTML = `
            <tr>
                <td
                    colspan="6"
                    style="
                        text-align:center;
                        padding:15px;
                    "
                >
                    Erreur de chargement.
                </td>
            </tr>
        `;

    }

            }
