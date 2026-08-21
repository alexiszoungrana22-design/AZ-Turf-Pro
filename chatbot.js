const CHAT_API = "https://az-turf-pro.onrender.com/api/assistant/chat";
const log = document.getElementById("chat-log");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-question");
const quick = document.getElementById("quick-actions");

// Retour : conserve le comportement attendu sur mobile et desktop.
document.getElementById("chat-back")?.addEventListener("click", () => {
  if (window.history.length > 1) window.history.back();
  else window.location.href = "index.html";
});

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
  p.className = className;
  p.innerHTML = `<strong>${escapeHtml(label)}</strong> ${escapeHtml(text).replace(/\n/g, "<br>")}`;
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}

function ask(question) {
  if (!input || !form) return;
  input.value = question;
  form.requestSubmit();
}

[
  ["🧠", "Analyse la course"],
  ["🎟️", "Explique le ticket Premium"],
  ["🎯", "Quelle est la meilleure base ?"],
  ["⚔️", "Compare les deux meilleurs chevaux"],
  ["🔥", "Quel est le meilleur outsider ?"],
  ["⚠️", "Quels favoris sont vulnérables ?"],
  ["🛣️", "Quel est le scénario probable ?"],
  ["🏷️", "Explique les badges"]
].forEach(([icon, q]) => {
  const b = document.createElement("button");
  b.type = "button";
  b.textContent = `${icon} ${q}`;
  b.addEventListener("click", () => ask(q));
  quick?.appendChild(b);
});

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = input?.value.trim();
  if (!question) return;

  addMessage("Vous :", question, "user-message");
  input.value = "";

  const send = form.querySelector('button[type="submit"]');
  if (send) send.disabled = true;

  const loading = document.createElement("p");
  loading.className = "assistant-message loading";
  loading.innerHTML = "<strong>AZ Turf Pro :</strong> Analyse en cours…";
  log?.appendChild(loading);

  try {
    const response = await fetch(CHAT_API, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question})
    });
    const data = await response.json();
    loading.remove();
    if (!response.ok) throw new Error(data.detail || "Erreur assistant");
    addMessage("AZ Turf Pro :", data.reponse || "Aucune réponse.", "assistant-message");
  } catch (error) {
    loading.remove();
    addMessage("Erreur :", error.message || "Impossible de contacter l'assistant.", "error-message");
  } finally {
    if (send) send.disabled = false;
    input?.focus();
  }
});
