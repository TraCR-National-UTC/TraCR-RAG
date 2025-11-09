const chat = document.getElementById("chat");
const msg = document.getElementById("msg");
const send = document.getElementById("send");
const historyEl = document.getElementById("history");
const newChatBtn = document.getElementById("newChat");
const defaultGreeting = `
Hi, I am <strong>TraCR-AI</strong>, your AI companion to help you with
<strong>Transportation Cybersecurity Legislations</strong>.<br>
How can I assist you today?
`;


let conversations = [[]]; // simple in-memory; one convo with array of {role, content}
let current = 0;
function showDefaultGreeting() {
  // Create a new empty conversation
  const convo = [{ role: "bot", content: defaultGreeting, html: true }];
  conversations.unshift(convo); // add new chat at the top
  current = 0;
  renderConvo();      // render it in the chat window
  refreshHistory();   // update sidebar
}


// Safely allow a small set of tags/attrs (so links + <br> work)
function sanitizeHTML(input) {
  const template = document.createElement("template");
  template.innerHTML = input;

  const ALLOWED_TAGS = new Set(["BR","A","B","I","STRONG","EM","CODE","PRE","UL","OL","LI","P","SPAN"]);
  const ALLOWED_ATTRS = { A: new Set(["href","title","target","rel"]) };

  (function walk(node) {
    [...node.children].forEach(el => {
      if (!ALLOWED_TAGS.has(el.tagName)) {
        // unwrap disallowed tags
        el.replaceWith(...el.childNodes);
      } else {
        // drop disallowed attributes
        [...el.attributes].forEach(attr => {
          const ok = (ALLOWED_ATTRS[el.tagName] || new Set()).has(attr.name.toLowerCase());
          if (!ok) el.removeAttribute(attr.name);
        });
        if (el.tagName === "A") {
          const href = el.getAttribute("href") || "#";
          if (!/^https?:\/\//i.test(href) && !href.startsWith("#") && !href.startsWith("mailto:")) {
            el.setAttribute("href", "#");
          }
          el.setAttribute("target", "_blank");
          el.setAttribute("rel", "noopener noreferrer");
        }
        walk(el);
      }
    });
  })(template.content);

  return template.innerHTML;
}

// Only autoscroll if user is already at the bottom
function shouldAutoScroll() {
  // Allow a small threshold for rounding errors
  return (chat.scrollHeight - chat.scrollTop - chat.clientHeight) < 10;
}

// Append streamed HTML: insert tags immediately, type only the text nodes
async function appendStreamedHTML(bubble, html, speed = 0) {
  const safe = sanitizeHTML(html);
  const parts = safe.split(/(<[^>]+>)/g).filter(Boolean);

  for (const part of parts) {
    if (part.startsWith("<")) {
      bubble.insertAdjacentHTML("beforeend", part); // insert tag instantly
      if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
    } else {
      // type the text content character-by-character
      for (let i = 0; i < part.length; i++) {
        bubble.append(part[i]);
        if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
        await new Promise(r => setTimeout(r, speed));
      }
    }
  }
}

// Add a helper to render a saved HTML message (for history)
function addMessageHTML(role, html) {
  const row = document.createElement("div");
  row.className = `msg ${role}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "me" ? "🙂" : "🤖";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = sanitizeHTML(html);
  row.appendChild(avatar);
  row.appendChild(bubble);
  chat.appendChild(row);
  if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
}

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
  if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
}

function refreshHistory() {
  historyEl.innerHTML = "";

  // Build items newest → oldest
  for (let i = conversations.length - 1; i >= 0; i--) {
    const el = document.createElement("div");
    el.className = "item";
    el.dataset.index = String(i);   // REAL index
    el.textContent = getTitle(i);

    // click selects the chat
    el.onclick = () => switchConvo(i);

    // double-click to rename
    el.ondblclick = (e) => {
      e.stopPropagation();
      renameChat(i);
    };

    historyEl.appendChild(el);
  }

  // Highlight the active chat: find the node with data-index === String(current)
  const nodes = Array.from(historyEl.children);
  const active = nodes.find(n => n.dataset.index === String(current));
  if (active) active.classList.add("active");
}

// Store optional custom titles on the conversations array itself
function getTitle(i) {
  const metaTitle = conversations[i]?.title;
  if (metaTitle && metaTitle.trim()) return metaTitle.trim();

  const firstUserMsg = conversations[i]?.find(m => m.role === "me")?.content || "";
  return firstUserMsg ? firstUserMsg.slice(0, 30) : "New chat";
}

function renameChat(i) {
  const currentTitle = getTitle(i);
  const name = prompt("Rename chat:", currentTitle);
  if (name === null) return; // cancelled
  conversations[i].title = name.trim() || "Untitled chat";
  refreshHistory(); // re-render with new title
}

function switchConvo(i) {
  current = i;        // i is the REAL index in conversations
  renderConvo();
  refreshHistory();   // will highlight the active one
}


function renderConvo() {
  chat.innerHTML = "";
  const convo = conversations[current] || [];
  for (const m of convo) {
    if (m.html) addMessageHTML(m.role, m.content);
    else addMessage(m.role, m.content);
  }
  if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
}

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
  if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
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
  if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
  return bubble;
}

// Append text with a typewriter effect into an existing bubble
function typeText(bubble, text, speed = 0) {
  return new Promise(resolve => {
    let i = 0;
    (function tick() {
      if (i < text.length) {
        bubble.textContent += text.charAt(i++);
        if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
        setTimeout(tick, speed);
      } else {
        resolve();
      }
    })();
  });
}

let botBubble = null;
let combined = "";
let first = true;
let finished = false;   // NEW: normal finish flag
let closed = false;     // NEW: we already closed the ES
let busy = false;  // prevents double-send (click + Enter)
let currentStream = null;

async function sendMessage() {
  if (busy) return;

  const text = msg.value.trim();
  if (!text) return;

  // instrumentation: log send attempts (helps detect duplicate sends)
  try { console.debug && console.debug('sendMessage called', { ts: Date.now(), text }); } catch {}

  busy = true;
  send.disabled = true;

  // IMPORTANT: close any previous stream before starting a new one
  // If a stream is already active and open, don't create another one.
  if (currentStream && currentStream.readyState !== 2) {
    try { console.warn && console.warn('sendMessage: stream already open, ignoring duplicate send'); } catch {}
    busy = false; send.disabled = false;
    return;
  }
  // Close previous closed/errored stream objects
  if (currentStream) {
    try { currentStream.close(); } catch {}
    currentStream = null;
  }

  // capture the conversation index for later use (avoid ReferenceError)
  const convoIndex = current;

  // record the user message in the in-memory convo and render it
  conversations[convoIndex] ??= [];
  conversations[convoIndex].push({ role: "me", content: text });
  addMessage("me", text);
  msg.value = "";

  const thinkingRow = createThinkingBubble();

  const es = new EventSource(`/api/chat/stream/?message=${encodeURIComponent(text)}&sid=${Date.now()}`); // sid avoids caching
  currentStream = es;

  try { console.debug && console.debug('EventSource created', { url: es.url }); } catch {}
  es.onopen = () => { try { console.debug && console.debug('EventSource open', { sid: new URL(es.url, location.href).searchParams.get('sid') }); } catch {} };
  es.onclose = () => { try { console.debug && console.debug('EventSource closed', { sid: new URL(es.url, location.href).searchParams.get('sid') }); } catch {} };

  let seenIds = new Set();        // prevent duplicate chunks on reconnect
  let first = true, finished = false, closed = false;
  let botBubble = null;
  let combinedHTML = "";

  let queue = Promise.resolve();
  const enqueue = (fn) => (queue = queue.then(fn).catch(()=>{}));

  es.onmessage = (e) => {
    // ignore replayed events
    if (e.lastEventId && seenIds.has(e.lastEventId)) return;
    if (e.lastEventId) seenIds.add(e.lastEventId);

    const { delta } = JSON.parse(e.data || "{}");
    if (!delta) return;

    if (first) {
      first = false;
      try { thinkingRow.remove(); } catch {}
      botBubble = createBotBubble();
    }

    const safeDelta = sanitizeHTML(delta);
    combinedHTML += safeDelta;
    enqueue(() => appendStreamedHTML(botBubble, safeDelta, 8));
  };

  es.addEventListener("done", () => {
    // Ensure we always close the EventSource and clear state even if processing fails
    try {
      try { console.debug && console.debug('EventSource done event', { ts: Date.now(), sid: new URL(es.url, location.href).searchParams.get('sid') }); } catch {}
      finished = true;
      queue.then(() => {
        if (botBubble) botBubble.classList.remove("typing");
        conversations[convoIndex].push({ role: "bot", content: combinedHTML, html: true });
      }).catch(()=>{});
    } finally {
      try { if (!closed) { es.close(); closed = true; } } catch {}
      try { if (currentStream === es) currentStream = null; } catch {}
      busy = false; send.disabled = false;
    }
  });

  es.onerror = () => {
    // Ignore errors after normal finish or after we closed it
    if (finished || closed) return;
    try { console.warn && console.warn('EventSource error', { ts: Date.now(), sid: new URL(es.url, location.href).searchParams.get('sid') }); } catch {}
    try { if (thinkingRow && thinkingRow.parentNode) thinkingRow.remove(); } catch {}
    if (first) {
      addMessage("bot", "Error: stream interrupted.");
      conversations[convoIndex].push({ role: "bot", content: "Error: stream interrupted." });
    }
    if (!closed) { es.close(); closed = true; }
    if (currentStream === es) currentStream = null;
    busy = false; send.disabled = false;
  };
}

send.onclick = sendMessage;
msg.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

newChatBtn.onclick = () => {
  conversations.unshift([]);   // add to front
  current = 0;
  renderConvo();
  refreshHistory();
};

refreshHistory();
renderConvo();
