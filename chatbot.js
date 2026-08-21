const CHAT_API = "https://az-turf-pro.onrender.com/api/assistant/chat";
const log = document.getElementById("chat-log");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-question");

function addMessage(label, text) {
  const p = document.createElement("p");
  p.innerHTML = `<strong>${label}</strong> ${String(text).replace(/\n/g, "<br>")}`;
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = input.value.trim();
  if (!question) return;
  addMessage("Vous :", question);
  input.value = "";
  try {
    const response = await fetch(CHAT_API, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Erreur assistant");
    addMessage("AZ Turf Pro :", data.reponse || "Aucune réponse.");
  } catch (error) {
    addMessage("Erreur :", error.message);
  }
});
