const chat = document.getElementById("chat");
const msg = document.getElementById("msg");
const send = document.getElementById("send");
const historyEl = document.getElementById("history");
const newChatBtn = document.getElementById("newChat");

let conversations = [[]]; // simple in-memory; one convo with array of {role, content}
let current = 0;

function addMessage(role, text) {
  const row = document.createElement("div");
  row.className = `msg ${role}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "me" ? "🙂" : "🤖";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  row.appendChild(avatar);
  row.appendChild(bubble);
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
}

function refreshHistory() {
  historyEl.innerHTML = "";
  conversations.forEach((c, i) => {
    const title = c.find(m => m.role === "me")?.content.slice(0, 30) || "New chat";
    const el = document.createElement("div");
    el.className = "item";
    el.textContent = title;
    el.onclick = () => switchConvo(i);
    historyEl.appendChild(el);
  });
}

function switchConvo(i) {
  current = i;
  renderConvo();
}

function renderConvo() {
  chat.innerHTML = "";
  for (const m of conversations[current]) addMessage(m.role, m.content);
}

// async function sendMessage() {
//   const text = msg.value.trim();
//   if (!text) return;
//   conversations[current].push({ role: "me", content: text });
//   addMessage("me", text);
//   msg.value = "";

//   // call backend
//   try {
//     const res = await fetch("/api/chat/", {
//       method: "POST",
//       headers: {"Content-Type":"application/json"},
//       body: JSON.stringify({ message: text })
//     });
//     const data = await res.json();
//     const answer = data.answer || data.error || "(no answer)";
//     conversations[current].push({ role: "bot", content: answer });
//     addMessage("bot", answer);
//   } catch (e) {
//     const err = `Error: ${e.message}`;
//     conversations[current].push({ role: "bot", content: err });
//     addMessage("bot", err);
//   }
// }

// async function sendMessage() {
//   const text = msg.value.trim();
//   if (!text) return;

//   // Show the user's message instantly
//   conversations[current].push({ role: "me", content: text });
//   addMessage("me", text);
//   msg.value = "";

//   try {
//     const res = await fetch("/api/chat/", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ message: text })
//     });

//     const data = await res.json();
//     const answer = data.answer || data.error || "(no answer)";

//     // Create an empty message bubble for the bot
//     const botRow = document.createElement("div");
//     botRow.className = "row bot";
//     const bubble = document.createElement("div");
//     bubble.className = "bubble";
//     botRow.appendChild(bubble);
//     chat.appendChild(botRow);
//     chat.scrollTop = chat.scrollHeight;

//     // Animate text typing effect
//     let i = 0;
//     const speed = 5; // milliseconds per character (adjust for faster/slower typing)

//     bubble.classList.add("typing");

//     function typeWriter() {
//         if (i < answer.length) {
//             bubble.textContent += answer.charAt(i);
//             i++;
//             chat.scrollTop = chat.scrollHeight;
//             setTimeout(typeWriter, speed);
//         } else {
//             bubble.classList.remove("typing"); // stop cursor blink
//             conversations[current].push({ role: "bot", content: answer });
//         }
//     }

//     typeWriter();

//   } catch (e) {
//     addMessage("bot", "Error: " + e.message);
//   }
// }

function createThinkingBubble() {
  const row = document.createElement("div");
  row.className = "msg bot";
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = "🤖";
  const bubble = document.createElement("div");
  bubble.className = "bubble thinking";
  bubble.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span>`;
  row.appendChild(avatar);
  row.appendChild(bubble);
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
  return row; // return the whole row so we can remove it later
}

function createBotBubble() {
  const row = document.createElement("div");
  row.className = "msg bot";
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = "🤖";
  const bubble = document.createElement("div");
  bubble.className = "bubble typing"; // optional blinking cursor class
  row.appendChild(avatar);
  row.appendChild(bubble);
  chat.appendChild(row);
  chat.scrollTop = chat.scrollHeight;
  return bubble;
}

// Append text with a typewriter effect into an existing bubble
function typeText(bubble, text, speed = 12) {
  return new Promise(resolve => {
    let i = 0;
    (function tick() {
      if (i < text.length) {
        bubble.textContent += text.charAt(i++);
        chat.scrollTop = chat.scrollHeight;
        setTimeout(tick, speed);
      } else {
        resolve();
      }
    })();
  });
}

async function sendMessage() {
  const text = msg.value.trim();
  if (!text) return;

  // show user (right)
  addMessage("me", text);
  msg.value = "";

  // show thinking immediately
  const thinkingRow = createThinkingBubble();

  // open SSE stream with the message
  const url = `/api/chat/stream/?message=${encodeURIComponent(text)}`;
  const es = new EventSource(url);

  let botBubble = null;
  let combined = "";
  let first = true;

  es.onmessage = async (e) => {
    const { delta } = JSON.parse(e.data || "{}");
    if (!delta) return;

    if (first) {
      first = false;
      thinkingRow.remove();
      botBubble = createBotBubble();
    }
    combined += delta;
    await typeText(botBubble, delta, 8); // type each incoming chunk
  };

  es.addEventListener("done", () => {
    if (botBubble) botBubble.classList.remove("typing");
    // (optional) store 'combined' somewhere if you keep history
    es.close();
  });

  es.onerror = () => {
    try { es.close(); } catch {}
    if (thinkingRow && thinkingRow.parentNode) thinkingRow.remove();
    addMessage("bot", "Error: stream interrupted.");
  };
}



// async function sendMessage() {
//   const text = msg.value.trim();
//   if (!text) return;

//   // 1) Show the user's message immediately (right-aligned by your CSS)
//   conversations[current].push({ role: "me", content: text });
//   addMessage("me", text);
//   msg.value = "";

//   try {
//     // 2) Ask your backend
//     const res = await fetch("/api/chat/", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ message: text })
//     });
//     const data = await res.json();
//     const answer = data.answer || data.error || "(no answer)";

//     // 3) Create a BOT row matching your existing structure: <div class="msg bot"><div class="avatar">🤖</div><div class="bubble"></div></div>
//     const row = document.createElement("div");
//     row.className = "msg bot";

//     const avatar = document.createElement("div");
//     avatar.className = "avatar";
//     avatar.textContent = "🤖";

//     const bubble = document.createElement("div");
//     bubble.className = "bubble typing"; // 'typing' gives the blinking cursor you already have

//     row.appendChild(avatar);
//     row.appendChild(bubble);
//     chat.appendChild(row);
//     chat.scrollTop = chat.scrollHeight;

//     // 4) Type it out, one character at a time
//     let i = 0;
//     const speed = 5; // ms per character (tweak: 10 = faster, 40 = slower)

//     (function type() {
//       if (i < answer.length) {
//         bubble.textContent += answer.charAt(i++);
//         chat.scrollTop = chat.scrollHeight;
//         setTimeout(type, speed);
//       } else {
//         bubble.classList.remove("typing"); // stop the blinking cursor
//         conversations[current].push({ role: "bot", content: answer }); // save final message
//       }
//     })();

//   } catch (e) {
//     addMessage("bot", "Error: " + e.message);
//   }
// }



send.onclick = sendMessage;
msg.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }});
newChatBtn.onclick = () => { conversations.push([]); current = conversations.length - 1; renderConvo(); refreshHistory(); };

refreshHistory();
renderConvo();
