const CHAT_API = "https://az-turf-pro.onrender.com/api/assistant/chat";

const log = document.getElementById("chat-log");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-question");

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function addMessage(label, text, className = "") {
  if (!log) return;
  const p = document.createElement("p");
  p.className = `chat-message ${className}`.trim();
  p.innerHTML = `<strong>${escapeHtml(label)}</strong> ${escapeHtml(text).replace(/\n/g, "<br>")}`;
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}

function retourPagePrecedente() {
  if (window.history.length > 1) window.history.back();
  else window.location.href = "index.html";
}

function poserQuestion(question) {
  if (!input || !form) return;
  input.value = question;
  form.requestSubmit();
}

function ajouterInterfaceAssistant() {
  const section = document.querySelector(".card");
  if (!section) return;

  if (!document.getElementById("az-chat-back")) {
    const back = document.createElement("button");
    back.id = "az-chat-back";
    back.type = "button";
    back.className = "az-chat-back";
    back.textContent = "← Retour";
    back.addEventListener("click", retourPagePrecedente);
    section.insertBefore(back, section.firstChild);
  }

  if (!document.getElementById("az-chat-actions")) {
    const actions = document.createElement("div");
    actions.id = "az-chat-actions";
    actions.className = "az-chat-actions";

    const questions = [
      ["🧠", "Analyse la course"],
      ["🎟️", "Explique le ticket Premium"],
      ["🎯", "Quelle est la meilleure base ?"],
      ["⚔️", "Compare les deux meilleurs chevaux"],
      ["🔥", "Quel est le meilleur outsider ?"],
      ["⚠️", "Quels favoris sont vulnérables ?"],
      ["🛣️", "Quel est le scénario probable ?"],
      ["🏷️", "Explique les badges"]
    ];

    questions.forEach(([icon, text]) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "az-chat-action";
      button.textContent = `${icon} ${text}`;
      button.addEventListener("click", () => poserQuestion(text));
      actions.appendChild(button);
    });

    form.parentNode.insertBefore(actions, form);
  }
}

ajouterInterfaceAssistant();

if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = input.value.trim();
    if (!question) return;

    addMessage("Vous :", question, "user-message");
    input.value = "";

    const submit = form.querySelector('button[type="submit"]');
    if (submit) submit.disabled = true;

    const loading = document.createElement("p");
    loading.className = "chat-message assistant-message loading";
    loading.innerHTML = "<strong>AZ Turf Pro :</strong> Analyse en cours…";
    log.appendChild(loading);
    log.scrollTop = log.scrollHeight;

    try {
      const response = await fetch(CHAT_API, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question})
      });

      const data = await response.json();
      loading.remove();

      if (!response.ok) {
        throw new Error(data.detail || "Erreur assistant");
      }

      addMessage(
        "AZ Turf Pro :",
        data.reponse || "Aucune réponse disponible.",
        "assistant-message"
      );
    } catch (error) {
      loading.remove();
      addMessage(
        "Erreur :",
        error.message || "Impossible de contacter l'assistant.",
        "error-message"
      );
    } finally {
      if (submit) submit.disabled = false;
      input.focus();
    }
  });
}
