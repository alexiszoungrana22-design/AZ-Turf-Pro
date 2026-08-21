const CHAT_API = "https://az-turf-pro.onrender.com/api/assistant/chat";
const log = document.getElementById("chat-log");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-question");
const quick = document.getElementById("quick-actions");

function getUserName() {
  const keys = ["AZ_TURF_PRENOM", "AZ_TURF_USER_NAME", "AZ_TURF_NOM_PRENOM", "AZ_TURF_NOM"];
  for (const key of keys) {
    const value = sessionStorage.getItem(key) || localStorage.getItem(key);
    if (value && value.trim()) return value.trim().split(/\s+/)[0];
  }
  return "";
}
function getAdminKey() {
  return sessionStorage.getItem("AZ_TURF_ADMIN_API_KEY") || localStorage.getItem("AZ_TURF_ADMIN_API_KEY") || "";
}
function getPremiumToken() {
  return sessionStorage.getItem("AZ_TURF_PREMIUM_TOKEN") || localStorage.getItem("AZ_TURF_PREMIUM_TOKEN") || "";
}
function escapeHtml(value) {
  return String(value ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
function addMessage(label, text, className = "") {
  if (!log) return;
  const p = document.createElement("p");
  p.className = className;
  p.innerHTML = `<strong>${escapeHtml(label)}</strong> ${escapeHtml(text).replace(/\n/g, "<br>")}`;
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}
document.getElementById("chat-back")?.addEventListener("click", () => {
  if (window.history.length > 1) window.history.back(); else window.location.href = "index.html";
});
const conversation = [];
function buildHeaders() {
  const headers = { "Content-Type": "application/json" };
  const adminKey = getAdminKey();
  const premiumToken = getPremiumToken();
  if (adminKey) headers["X-Admin-Key"] = adminKey;
  else if (premiumToken) headers["Authorization"] = `Bearer ${premiumToken}`;
  return headers;
}
async function sendQuestion(question) {
  const q = String(question || "").trim();
  if (!q) return;
  addMessage("Vous :", q, "user-message");
  conversation.push({ role: "user", content: q });
  const loading = document.createElement("p");
  loading.className = "assistant-message loading";
  loading.innerHTML = "<strong>🤖 Assistant Chatbot :</strong> Analyse en cours…";
  log?.appendChild(loading);
  const send = form?.querySelector('button[type="submit"]');
  if (send) send.disabled = true;
  try {
    const response = await fetch(CHAT_API, {
      method: "POST",
      headers: buildHeaders(),
      body: JSON.stringify({ question: q, conversation: conversation.slice(-12), contexte: { source: "chatbot" } })
    });
    const raw = await response.text();
    let data = {};
    try { data = JSON.parse(raw); } catch (_) {}
    loading.remove();
    if (!response.ok) throw new Error(data.detail || raw || `Erreur assistant (${response.status})`);
    const answer = data.reponse || data.response || data.message || "Aucune réponse.";
    conversation.push({ role: "assistant", content: String(answer) });
    addMessage("🤖 Assistant Chatbot :", answer, "assistant-message");
  } catch (error) {
    loading.remove();
    addMessage("⚠️ Assistant :", error.message || "Impossible de contacter l'assistant.", "error-message");
  } finally {
    if (send) send.disabled = false;
    input?.focus();
  }
}
function ask(question) {
  const q = String(question || "").trim();
  if (!q) return;
  if (input) input.value = q;
  sendQuestion(q);
  if (input) input.value = "";
}
if (log && !log.dataset.greetingShown) {
  const name = getUserName();
  const greeting = name ? `Bonjour ${name} 👋\nJe suis l'Assistant Chatbot AZ Turf Pro.\nComment puis-je vous aider aujourd'hui ?` : `Bonjour 👋\nJe suis l'Assistant Chatbot AZ Turf Pro.\nComment puis-je vous aider aujourd'hui ?`;
  addMessage("🤖 Assistant Chatbot :", greeting, "assistant-message greeting");
  log.dataset.greetingShown = "1";
}
[["🧠", "Analyse la course"], ["🎟️", "Explique le ticket Premium"], ["🎯", "Quelle est la meilleure base ?"], ["⚔️", "Compare les deux meilleurs chevaux"], ["🔥", "Quel est le meilleur outsider ?"], ["⚠️", "Quels favoris sont vulnérables ?"], ["🛣️", "Donne-moi deux scénarios de course"], ["🏷️", "Explique les badges"]].forEach(([icon, q]) => {
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
  input.value = "";
  await sendQuestion(question);
});
