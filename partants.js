const API_PARTANTS = "https://az-turf-pro.onrender.com/api/partants";

document.addEventListener("DOMContentLoaded", chargerPartants);

async function chargerPartants() {
    const tbody = document.querySelector("table tbody");
    if (!tbody) return;

    try {
        const response = await fetch(API_PARTANTS, { cache: "no-store" });
        if (!response.ok) throw new Error(`API ${response.status}`);
        const data = await response.json();

        const chevaux = data.classement || data.chevaux || [];
        const nonPartants = new Set((data.non_partants || []).map(String));

        document.title = `Partants - ${data.course || "AZ Turf Pro"}`;

        const infos = document.querySelector(".course-box:nth-of-type(2)");
        if (infos) {
            const ps = infos.querySelectorAll("p");
            if (ps[0]) ps[0].textContent = `🏇 Hippodrome : ${data.hippodrome || "Non renseigné"}`;
            if (ps[1]) ps[1].textContent = `📅 Date : ${data.date || "Non renseignée"}`;
            if (ps[2]) ps[2].textContent = `🏆 Course : ${data.course || "Quinté+"} (${data.reunion || ""} ${data.course_numero || ""})`;
        }

        tbody.innerHTML = "";
        chevaux.forEach(c => {
            const tr = document.createElement("tr");
            const np = nonPartants.has(String(c.numero)) || c.est_non_partant;
            tr.innerHTML = `
                <td>${c.numero ?? "-"}</td>
                <td>${escapeHtml(c.nom || "Cheval")}</td>
                <td>${escapeHtml(c.jockey || "—")}</td>
                <td>${escapeHtml(c.entraineur || c.entraîneur || "—")}</td>
                <td>${c.cote ?? "—"}</td>
                <td>${c.indice_az ?? "—"}</td>
                <td>${np ? "NON PARTANT" : escapeHtml(c.statut || "PARTANT")}</td>
            `;
            tbody.appendChild(tr);
        });

        if (!chevaux.length) {
            tbody.innerHTML = `<tr><td colspan="7">Aucun partant disponible.</td></tr>`;
        }
    } catch (error) {
        console.error("Erreur partants :", error);
        tbody.innerHTML = `<tr><td colspan="7">Impossible de charger les partants actuellement.</td></tr>`;
    }
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
