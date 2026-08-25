const CHAT_STREAM_API = "https://az-turf-pro.onrender.com/api/assistant/chat/stream";
const HISTORY_KEY = "AZ_TURF_CHAT_HISTORY_V1";
const MAX_HISTORY = 30;

const log = document.getElementById("chat-log");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-question");
const quick = document.getElementById("quick-actions");
const clearBtn = document.getElementById("chat-clear");

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Markdown volontairement limité et sécurisé : aucun HTML fourni par le serveur
// n'est exécuté dans le navigateur.
function renderMarkdown(value) {
  let html = escapeHtml(value);
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/(^|[\s])\*([^*]+)\*(?=[\s.,!?]|$)/g, "$1<em>$2</em>");
  html = html.replace(/^### (.+)$/gm, "<h4>$1</h4>");
  html = html.replace(/^## (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^# (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^- (.+)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>\n?)+/g, block => `<ul>${block}</ul>`);
  html = html.replace(/\n/g, "<br>");
  return html;
}

function readHistory() {
  try {
    const value = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    return Array.isArray(value) ? value.slice(-MAX_HISTORY) : [];
  } catch (_) {
    return [];
  }
}

let history = readHistory();

function saveHistory() {
  history = history.slice(-MAX_HISTORY);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

function addBubble(role, text, save = true) {
  if (!log) return null;
  const wrapper = document.createElement("div");
  wrapper.className = role === "user" ? "chat-bubble user-bubble" : "chat-bubble assistant-bubble";
  wrapper.innerHTML = renderMarkdown(text);
  log.appendChild(wrapper);
  log.scrollTop = log.scrollHeight;
  if (save) {
    history.push({ role, content: String(text) });
    saveHistory();
  }
  return wrapper;
}

function restoreHistory() {
  if (!log) return;
  log.innerHTML = "";
  history.forEach(item => addBubble(item.role, item.content, false));
}

function addQuickChip(icon, question) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "chat-chip";
  b.textContent = `${icon} ${question}`;
  b.addEventListener("click", () => {
    input.value = question;
    form.requestSubmit();
  });
  quick?.appendChild(b);
}

[
  ["🧠", "Analyse la course"],
  ["🤖", "Construis ton propre Quinté, indépendamment d'AZ Turf Pro"],
  ["🛡️", "Fais un ticket IA prudent"],
  ["🔥", "Fais un ticket IA spéculatif avec de vrais outsiders"],
  ["💰", "Cherche les chevaux à valeur par rapport aux cotes"],
  ["⚔️", "Compare le ticket IA au ticket AZ Turf Pro"],
  ["🎯", "Quelle est la meilleure base et pourquoi ?"],
  ["⚠️", "Quels favoris sont vulnérables et pourquoi ?"],
  ["🛣️", "Donne-moi deux scénarios de course"],
  ["🏷️", "Explique les badges"]
].forEach(([icon, q]) => addQuickChip(icon, q));

// Retour conservé.
document.getElementById("chat-back")?.addEventListener("click", () => {
  if (window.history.length > 1) window.history.back();
  else window.location.href = "index.html";
});

clearBtn?.addEventListener("click", () => {
  history = [];
  localStorage.removeItem(HISTORY_KEY);
  if (log) log.innerHTML = "";
});

function getAssistantAuthHeaders() {
  // Point de vérité unique : voir auth.js (window.AZAuth).
  const headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
    ...window.AZAuth.authHeaders()
  };

  return {
    headers,
    isAdmin: window.AZAuth.isAdmin(),
    hasPremiumToken: Boolean(window.AZAuth.getPremiumToken())
  };
}

async function streamAnswer(question) {
  const auth = getAssistantAuthHeaders();
  // Ne bloque plus localement un administrateur dont la session n'a
  // pas encore été restaurée : le serveur est la source d'autorité.
  const response = await fetch(CHAT_STREAM_API, {
    method: "POST",
    headers: auth.headers,
    body: JSON.stringify({ question, historique: history.slice(-12) })
  });

  if (!response.ok) {
    let message = "Impossible de contacter l'assistant.";
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch (_) {}
    throw new Error(message);
  }

  if (!response.body) throw new Error("Le streaming n'est pas disponible sur ce navigateur.");

  const assistantBubble = addBubble("assistant", "", false);
  let answer = "";
  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const event of events) {
      const line = event.split("\n").find(item => item.startsWith("data: "));
      if (!line) continue;
      let data;
      try { data = JSON.parse(line.slice(6)); } catch (_) { continue; }

      if (data.type === "token") {
        answer += data.text || "";
        assistantBubble.innerHTML = renderMarkdown(answer);
        log.scrollTop = log.scrollHeight;
      } else if (data.type === "error") {
        throw new Error(data.message || "Erreur assistant.");
      }
    }
  }

  history.push({ role: "assistant", content: answer });
  saveHistory();
}

form?.addEventListener("submit", async event => {
  event.preventDefault();
  const question = input?.value.trim();
  if (!question) return;

  addBubble("user", question);
  input.value = "";

  const send = form.querySelector('button[type="submit"]');
  if (send) send.disabled = true;
  if (input) input.disabled = true;

  try {
    await streamAnswer(question);
  } catch (error) {
    addBubble("assistant", `⚠️ ${error.message || "Erreur assistant."}`);
  } finally {
    if (send) send.disabled = false;
    if (input) {
      input.disabled = false;
      input.focus();
    }
  }
});

restoreHistory();
