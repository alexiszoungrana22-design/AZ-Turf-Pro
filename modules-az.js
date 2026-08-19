/* ========================================================= */
/* AZ TURF PRO - LOGIQUE CLIENT (CHATBOT & BACKTEST)         */
/* ========================================================= */

// Stockage dynamique du résultat d'analyse courant
let derniereAnalyseCourse = null;

/* --- LOGIQUE CHATBOT --- */

function toggleChatbot() {
  const win = document.getElementById("az-chatbot-window");
  win.classList.toggle("chat-hidden");
}

function handleKeyPress(e) {
  if (e.key === "Enter") {
    envoyerQuestion();
  }
}

function envoyerQuestionRaccourci(texte) {
  document.getElementById("chat-input").value = texte;
  envoyerQuestion();
}

async function envoyerQuestion() {
  const input = document.getElementById("chat-input");
  const text = input.value.trim();
  if (!text) return;

  // 1. Ajouter le message de l'utilisateur dans l'interface
  ajouterMessage(text, "user");
  input.value = "";

  try {
    // 2. Appel vers le backend Render
    const res = await fetch("/assistant/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: text,
        contexte: { moteur: derniereAnalyseCourse }
      })
    });
    
    const data = await res.json();
    ajouterMessage(data.reponse, "bot");
  } catch (err) {
    ajouterMessage("Désolé, une erreur est survenue lors de la connexion.", "bot");
  }
}

function ajouterMessage(texte, type) {
  const container = document.getElementById("chat-messages");
  const msg = document.createElement("div");
  msg.className = `message ${type}`;
  msg.innerHTML = texte;
  container.appendChild(msg);
  container.scrollTop = container.scrollHeight;
}


/* --- LOGIQUE SIMULATEUR BACKTEST --- */

async function lancerBacktest() {
  const coteMin = document.getElementById("bt-cote-min").value;
  const coteMax = document.getElementById("bt-cote-max").value;
  const mise = document.getElementById("bt-mise").value;

  // Récupération de l'historique enregistré localement
  const historiqueExemple = JSON.parse(localStorage.getItem("az_historique_courses") || "[]");

  try {
    const res = await fetch("/stats/backtest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        historique: historiqueExemple,
        filtres: {
          cote_min: coteMin,
          cote_max: coteMax,
          mise_de_base: mise
        }
      })
    });

    const data = await res.json();

    // Mise à jour de l'affichage
    document.getElementById("res-mises").innerText = data.mises_totales + " €";
    document.getElementById("res-gains").innerText = data.gains_totaux + " €";
    
    const profitEl = document.getElementById("res-profit");
    profitEl.innerText = data.profit_net + " €";
    profitEl.style.color = data.profit_net >= 0 ? "#10b981" : "#ef4444";

    const roiEl = document.getElementById("res-roi");
    roiEl.innerText = data.roi_pourcent + " %";
    roiEl.style.color = data.roi_pourcent >= 0 ? "#10b981" : "#ef4444";

    document.getElementById("backtest-results").style.display = "grid";

  } catch (err) {
    alert("Erreur lors du calcul du backtest.");
  }
}
