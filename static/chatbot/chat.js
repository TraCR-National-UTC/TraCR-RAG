const chat = document.getElementById("chat");
const msg = document.getElementById("msg");
const send = document.getElementById("send");
const historyEl = document.getElementById("history");
const newChatBtn = document.getElementById("newChat");
const themeToggle = document.getElementById("themeToggle");

// Theme handling
let currentTheme = localStorage.getItem("theme") || "dark";

// Set initial theme
document.documentElement.setAttribute("data-theme", currentTheme);

// Toggle theme
themeToggle.addEventListener("click", () => {
  currentTheme = currentTheme === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", currentTheme);
  localStorage.setItem("theme", currentTheme);
});

const defaultGreeting = `
## 👋 Hi, I’m **TraCR-Legal-AI**

I’m your AI companion to help you with _Transportation Cybersecurity Legislations_.

---

### 🔍 Here’s what I can do:
- Provide details on cybersecurity laws by states  
- Compare legislations across states and identify potential loopholes  
- Suggest new policies to address inconsistencies between state regulations
---
How can I assist you today?
`;



// const upBtn = mkBtn("up", "Like");
// const downBtn = mkBtn("down", "Dislike");


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

  // Allow a richer set of HTML tags for markdown
  const ALLOWED_TAGS = new Set([
    "BR", "A", "B", "I", "STRONG", "EM", "CODE", "PRE", 
    "UL", "OL", "LI", "P", "SPAN", "H1", "H2", "H3", "H4", "H5", "H6",
    "BLOCKQUOTE", "HR", "TABLE", "THEAD", "TBODY", "TR", "TH", "TD",
    "DIV", "DEL", "INS"
  ]);
  const ALLOWED_ATTRS = { 
    A: new Set(["href", "title", "target", "rel"]),
    CODE: new Set(["class"]),  // For syntax highlighting classes
    PRE: new Set(["class"]),
    DIV: new Set(["class"])
  };

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

// Add a helper to render a saved message (markdown supported for bot)
function addMessageHTML(role, content, returnBubble = false) {
  const row = document.createElement("div");
  row.className = `msg ${role}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "me" ? "🙂" : "🤖";
  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (role === "bot" && window.marked) {
    bubble.innerHTML = sanitizeHTML(window.marked.parse(content));
    if (window.hljs) {
      bubble.querySelectorAll("pre code:not(.hljs)").forEach(el => hljs.highlightElement(el));
    }
    enhanceCodeBlocks(bubble);
  } else {
    bubble.innerHTML = sanitizeHTML(content);
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  chat.appendChild(row);
  if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
  return returnBubble ? bubble : undefined;
}

// function addMessageHTML(role, content) {
//   const row = document.createElement("div");
//   row.className = `msg ${role}`;
//   const avatar = document.createElement("div");
//   avatar.className = "avatar";
//   avatar.textContent = role === "me" ? "🙂" : "🤖";
//   const bubble = document.createElement("div");
//   bubble.className = "bubble";
//   if (role === "bot" && window.marked) {
//     // Parse markdown to HTML, then sanitize
//     bubble.innerHTML = sanitizeHTML(window.marked.parse(content));
//     if (window.hljs) {
//       bubble.querySelectorAll("pre code:not(.hljs)").forEach(el => hljs.highlightElement(el));
//     }
//     enhanceCodeBlocks(bubble);

//   } else {
//     bubble.innerHTML = sanitizeHTML(content);
//   }
//   row.appendChild(avatar);
//   row.appendChild(bubble);
//   chat.appendChild(row);
//   if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
// }

function addMessage(role, text, returnBubble = false) {
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
  return returnBubble ? bubble : undefined;
}

// function addMessage(role, text) {
//   const row = document.createElement("div");
//   row.className = `msg ${role}`;
//   const avatar = document.createElement("div");
//   avatar.className = "avatar";
//   avatar.textContent = role === "me" ? "🙂" : "🤖";
//   const bubble = document.createElement("div");
//   bubble.className = "bubble";
//   bubble.textContent = text;
//   row.appendChild(avatar);
//   row.appendChild(bubble);
//   chat.appendChild(row);
//   if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
// }

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
  convo.forEach((m, i) => {
    let bubble;
    if (m.html) bubble = addMessageHTML(m.role, m.content, true);
    else        bubble = addMessage(m.role, m.content, true);

    if (m.role === "bot") {
      attachFeedback(bubble, current, i);
      attachCopyFullMessage(bubble);
    }
  });
  if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
}


// function renderConvo() {
//   chat.innerHTML = "";
//   const convo = conversations[current] || [];
//   for (const m of convo) {
//     if (m.html) addMessageHTML(m.role, m.content);
//     else addMessage(m.role, m.content);
//   }
//   if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
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

// Add a "Copy full message" button at the top-right of bot bubbles
function attachCopyFullMessage(bubble) {
  if (!bubble || bubble.querySelector(".bubble-copy-btn")) return;

  const btn = document.createElement("button");
  btn.className = "bubble-copy-btn";
  btn.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor"
    viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
    </svg>
  `;
  btn.title = "Copy entire message";

  btn.addEventListener("click", async () => {
    try {
      // Get the full text (strip HTML tags but keep readable text)
      const range = document.createRange();
      range.selectNodeContents(bubble);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      const text = sel.toString().trim();
      sel.removeAllRanges();

      await navigator.clipboard.writeText(text);
      btn.classList.add("copied");
      btn.title = "Copied!";
      setTimeout(() => {
        btn.classList.remove("copied");
        btn.title = "Copy entire message";
      }, 1500);
    } catch (err) {
      console.error("Copy failed:", err);
    }
  });

  // Ensure bubble is relatively positioned
  bubble.style.position = "relative";
  bubble.appendChild(btn);
}


// Attach like/dislike controls to a bubble and sync with conversations[]
function attachFeedback(bubble, convoIndex, msgIndex) {
  if (!bubble || bubble.dataset.hasFeedback) return;
  bubble.dataset.hasFeedback = "1";

  const footer = document.createElement("div");
  footer.className = "bubble-footer";

  const mkBtn = (cls, title, svg) => {
    const btn = document.createElement("button");
    btn.className = cls;
    btn.type = "button";
    btn.title = title;
    btn.innerHTML = svg;
    return btn;
  };

  const upSvg = `
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor"
  viewBox="0 0 24 24"><path d="M14 9V5a3 3 0 0 0-3-3l-1 7H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h7l5-10a2 2 0 0 0-2-2h-1z"/></svg>`;

  const downSvg = `
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor"
  viewBox="0 0 24 24"><path d="M10 15v4a3 3 0 0 0 3 3l1-7h5a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-7L7 14a2 2 0 0 0 2 2h1z"/></svg>`;

  const copySvg = `
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor"
  viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;

  const upBtn = mkBtn("icon-btn up", "Like", upSvg);
  const downBtn = mkBtn("icon-btn down", "Dislike", downSvg);
  const copyBtn = mkBtn("copy-btn", "Copy message", copySvg);

  const msg = (conversations[convoIndex] || [])[msgIndex] || {};
  if (msg.feedback === "up") upBtn.classList.add("active", "up");
  if (msg.feedback === "down") downBtn.classList.add("active", "down");

  const setFeedback = (val) => {
    const arr = conversations[convoIndex] || (conversations[convoIndex] = []);
    arr[msgIndex] = arr[msgIndex] || { role: "bot", content: "" };
    if (arr[msgIndex].feedback === val) {
      arr[msgIndex].feedback = null;
      upBtn.classList.remove("active","up");
      downBtn.classList.remove("active","down");
    } else {
      arr[msgIndex].feedback = val;
      upBtn.classList.toggle("active", val === "up");
      upBtn.classList.toggle("up", val === "up");
      downBtn.classList.toggle("active", val === "down");
      downBtn.classList.toggle("down", val === "down");
    }
  };

  upBtn.onclick = () => setFeedback("up");
  downBtn.onclick = () => setFeedback("down");

  // copy full bubble text
  copyBtn.onclick = async () => {
    try {
      const text = bubble.innerText.trim();
      await navigator.clipboard.writeText(text);
      copyBtn.classList.add("copied");
      setTimeout(() => copyBtn.classList.remove("copied"), 1200);
    } catch {
      console.error("Copy failed");
    }
  };

  footer.appendChild(copyBtn);
  footer.appendChild(upBtn);
  footer.appendChild(downBtn);
  bubble.appendChild(footer);
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
  let combinedMd = "";   // ← accumulate MARKDOWN, not HTML

  es.onmessage = (e) => {
    const { delta } = JSON.parse(e.data || "{}");
    if (!delta) return;

    if (first) {
      first = false;
      try { thinkingRow.remove(); } catch {}
      botBubble = createBotBubble();     // has the .typing cursor
    }

    combinedMd += delta;

    if (window.marked) {
      // Convert MD → HTML every chunk, then sanitize
      const html = sanitizeHTML(window.marked.parse(combinedMd));
      botBubble.innerHTML = html;
      // highlight newly rendered code
      if (window.hljs) {
        botBubble.querySelectorAll("pre code:not(.hljs)").forEach(el => hljs.highlightElement(el));
      }
      // add Copy button + wrapper like ChatGPT
      enhanceCodeBlocks(botBubble);

    } else {
      // Fallback if marked isn't available: just type plain text
      // (or remove this else if you always have marked)
      botBubble.textContent += delta;
    }

    if (shouldAutoScroll()) chat.scrollTop = chat.scrollHeight;
  };

  es.addEventListener("done", () => {
    finished = true;
    queue.then(() => {
      if (botBubble) botBubble.classList.remove("typing");

      const finalHtml = botBubble ? botBubble.innerHTML : "";   // <- use rendered HTML
      conversations[convoIndex].push({ role: "bot", content: finalHtml, html: true });

      const msgIndex = conversations[convoIndex].length - 1;
      const lastBubble = document.querySelector("#chat .msg.bot:last-child .bubble");
      if (lastBubble) {
        attachFeedback(lastBubble, convoIndex, msgIndex);
        attachCopyFullMessage(lastBubble);
      }
    }).finally(() => {
      if (!closed) { es.close(); closed = true; }
      busy = false; send.disabled = false;
    });
  });


  // es.addEventListener("done", () => {
  //   finished = true;
  //   queue.then(() => {
  //     if (botBubble) botBubble.classList.remove("typing");

  //     // save final message (HTML or text based on your setup)
  //     conversations[convoIndex].push({ role: "bot", content: combinedHTML, html: true });

  //     // attach like/dislike to the just-added bubble
  //     const msgIndex = conversations[convoIndex].length - 1;
  //     const lastBubble = document.querySelector("#chat .msg.bot:last-child .bubble");
  //     if (lastBubble) attachFeedback(lastBubble, convoIndex, msgIndex);
  //   }).finally(() => {
  //     if (!closed) { es.close(); closed = true; }
  //     busy = false; send.disabled = false;
  //   });
  // });


  // es.addEventListener("done", () => {
  //   finished = true;
  //   queue.then(() => {
  //     if (botBubble) botBubble.classList.remove("typing");
  //     const finalHtml = botBubble.innerHTML;       // save rendered HTML
  //     conversations[convoIndex].push({ role: "bot", content: finalHtml, html: true });
  //   }).finally(() => {
  //     if (!closed) { es.close(); closed = true; }
  //     if (currentStream === es) currentStream = null;
  //     busy = false; send.disabled = false;
  //   });
  // });


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

// Wrap each <pre><code>...</code></pre> in a .codeblock and add a Copy button
function enhanceCodeBlocks(container) {
  const blocks = container.querySelectorAll("pre > code");
  blocks.forEach(code => {
    const pre = code.parentElement;
    if (pre.closest(".codeblock")) return; // skip if already wrapped

    const wrapper = document.createElement("div");
    wrapper.className = "codeblock";

    const header = document.createElement("div");
    header.className = "codeblock-header";

    // language label
    const lang = (code.className.match(/language-(\w+)/) || [])[1] || "text";
    const label = document.createElement("span");
    label.className = "lang-label";
    label.textContent = lang;

    // copy button
    const btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg><span>Copy code</span>';

    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(code.innerText);
        btn.classList.add("copied");
        btn.querySelector("span").textContent = "Copied!";
        setTimeout(() => {
          btn.classList.remove("copied");
          btn.querySelector("span").textContent = "Copy code";
        }, 1500);
      } catch {
        btn.querySelector("span").textContent = "Failed";
        setTimeout(() => btn.querySelector("span").textContent = "Copy code", 1500);
      }
    });

    header.appendChild(label);
    header.appendChild(btn);

    // assemble
    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(header);
    wrapper.appendChild(pre);
  });
}


// function enhanceCodeBlocks(container) {
//   const blocks = container.querySelectorAll("pre > code");
//   blocks.forEach(code => {
//     const pre = code.parentElement;
//     if (pre.closest(".codeblock")) return; // already enhanced

//     const wrapper = document.createElement("div");
//     wrapper.className = "codeblock";

//     pre.parentNode.insertBefore(wrapper, pre);
//     wrapper.appendChild(pre);

//     const btn = document.createElement("button");
//     btn.className = "copy-btn";
//     btn.type = "button";
//     btn.textContent = "Copy";
//     btn.addEventListener("click", async () => {
//       try {
//         await navigator.clipboard.writeText(code.innerText);
//         btn.classList.add("copied");
//         btn.textContent = "Copied!";
//         setTimeout(() => { btn.classList.remove("copied"); btn.textContent = "Copy"; }, 1200);
//       } catch {
//         btn.textContent = "Failed";
//         setTimeout(() => { btn.textContent = "Copy"; }, 1200);
//       }
//     });

//     wrapper.appendChild(btn);
//   });
// }


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

// Show initial greeting when page loads
showDefaultGreeting();

// Also show greeting when clicking "New Chat"
newChatBtn.onclick = () => {
  showDefaultGreeting();
};
