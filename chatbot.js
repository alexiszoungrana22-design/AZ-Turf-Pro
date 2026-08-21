const CHAT_API = "https://az-turf-pro.onrender.com/api/assistant/chat";
const log = document.getElementById("chat-log");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-question");
const quick = document.getElementById("quick-actions");

document.getElementById("chat-back")?.addEventListener("click", () => {
  if (history.length > 1) history.back(); else location.href = "index.html";
});

function addMessage(label, text) {
  const p=document.createElement("p");
  p.innerHTML=`<strong>${label}</strong> ${String(text).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","":"&quot;"}[c])).replace(/\n/g,"<br>")}`;
  log.appendChild(p); log.scrollTop=log.scrollHeight;
}

[
  ["🧠","Analyse la course"],["🎟️","Explique le ticket Premium"],
  ["🎯","Quelle est la meilleure base ?"],["⚔️","Compare les deux meilleurs chevaux"],
  ["🔥","Quel est le meilleur outsider ?"],["⚠️","Quels favoris sont vulnérables ?"],
  ["🛣️","Quel est le scénario probable ?"],["🏷️","Explique les badges"]
].forEach(([icon,q])=>{
  const b=document.createElement("button"); b.type="button"; b.textContent=`${icon} ${q}`;
  b.onclick=()=>{input.value=q;form.requestSubmit();}; quick?.appendChild(b);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question=input.value.trim(); if(!question)return;
  addMessage("Vous :",question); input.value="";
  const send=form.querySelector('button[type="submit"]'); if(send)send.disabled=true;
  addMessage("AZ Turf Pro :","Analyse en cours…");
  try {
    const response=await fetch(CHAT_API,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question})});
    const data=await response.json();
    if(!response.ok)throw new Error(data.detail||"Erreur assistant");
    log.lastElementChild?.remove();
    addMessage("AZ Turf Pro :",data.reponse||"Aucune réponse.");
  } catch(error) {
    log.lastElementChild?.remove(); addMessage("Erreur :",error.message);
  } finally { if(send)send.disabled=false; input.focus(); }
});
