const $ = (s) => document.querySelector(s);
const state = { q: "", level: new Set(), theme: new Set(), place: new Set(), language: new Set(), ec: new Set(), sort: "name", rec: null };
const facets = { level: "#f-level", theme: "#f-theme", place: "#f-place", language: "#f-language", ec: "#f-ec" };
let MODULES = [];

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const values = (m, key) => (key === "theme" ? m.themes : [m[key]]).filter((v) => v !== "" && v != null).map(String);

function renderFilters() {
  for (const [key, sel] of Object.entries(facets)) {
    const all = [...new Set(MODULES.flatMap((m) => values(m, key)))];
    all.sort(key === "ec" ? (a, b) => parseFloat(a) - parseFloat(b) : (a, b) => a.localeCompare(b));
    $(sel).innerHTML = all
      .map((v) => `<label><input type="checkbox" data-key="${key}" value="${esc(v)}"> ${esc(v)}</label>`)
      .join("");
  }
}

function filtered() {
  if (state.rec) return state.rec.map((r) => MODULES.find((m) => m.id === r.module_id)).filter(Boolean);
  const q = state.q.toLowerCase();
  const list = MODULES.filter((m) =>
    (!q || `${m.name} ${m.summary} ${m.themes.join(" ")} ${m.program}`.toLowerCase().includes(q)) &&
    Object.keys(facets).every((k) => !state[k].size || values(m, k).some((v) => state[k].has(v)))
  );
  const by = { name: (a, b) => a.name.localeCompare(b.name), ec: (a, b) => parseFloat(a.ec) - parseFloat(b.ec) };
  return list.sort(by[state.sort]);
}

function render() {
  const list = filtered();
  const reasons = new Map((state.rec || []).map((r) => [r.module_id, r.reason]));
  $("#count").textContent = state.rec
    ? `${list.length} aanbevolen minor${list.length === 1 ? "" : "s"}`
    : `${list.length} minor${list.length === 1 ? "" : "s"} gevonden`;
  $("#grid").innerHTML = list.map((m) => `
    <button class="card${reasons.has(m.id) ? " rec" : ""}" data-id="${m.id}">
      <div class="tags"><span class="tag ec">${esc(m.ec)} EC</span><span class="tag">${esc(m.level)}</span><span class="tag">${esc(m.place)}</span></div>
      <h3>${esc(m.name)}</h3>
      ${reasons.has(m.id)
        ? `<p class="why"><strong>Waarom aanbevolen:</strong> ${esc(reasons.get(m.id))}</p>`
        : `<p>${esc(m.summary.slice(0, 170))}…</p>`}
      <div class="tags"><span class="tag">${esc(m.form)}</span><span class="tag">${esc(m.language)}</span></div>
    </button>`).join("") || "<p>Geen minors gevonden.</p>";
}

function openDetail(id) {
  const m = MODULES.find((x) => x.id === id);
  if (!m) return;
  const why = (state.rec || []).find((r) => r.module_id === id)?.reason;
  $("#detail-body").innerHTML = `
    <h2>${esc(m.name)}</h2>
    ${why ? `<p class="why"><strong>Waarom aanbevolen:</strong> ${esc(why)}</p>` : ""}
    <div class="tags"><span class="tag ec">${esc(m.ec)} EC</span><span class="tag">${esc(m.level)}</span><span class="tag">${esc(m.place)}</span><span class="tag">${esc(m.form)}</span><span class="tag">${esc(m.language)}</span></div>
    <p>${esc(m.summary)}</p>
    ${m.themes.length ? `<p><strong>Thema's:</strong> ${esc(m.themes.join(", "))}</p>` : ""}
    ${m.entry ? `<p><strong>Ingangseisen:</strong> ${esc(m.entry)}</p>` : ""}
    <p><strong>Periodes:</strong></p><ul>${m.periods.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>`;
  $("#detail").showModal();
}

document.addEventListener("change", (e) => {
  const key = e.target.dataset && e.target.dataset.key;
  if (key) {
    state.rec = null;
    e.target.checked ? state[key].add(e.target.value) : state[key].delete(e.target.value);
    render();
  }
});
$("#search-form").addEventListener("submit", (e) => { e.preventDefault(); state.rec = null; state.q = $("#search").value; render(); });
$("#search").addEventListener("input", (e) => { state.rec = null; state.q = e.target.value; render(); });
$("#sort").addEventListener("change", (e) => { state.sort = e.target.value; render(); });
$("#reset").addEventListener("click", () => {
  Object.keys(facets).forEach((k) => state[k].clear());
  state.q = ""; state.rec = null; $("#search").value = "";
  document.querySelectorAll(".filters input").forEach((i) => (i.checked = false));
  render();
});
$("#grid").addEventListener("click", (e) => {
  const card = e.target.closest(".card");
  if (card) openDetail(Number(card.dataset.id));
});
$("#detail-close").addEventListener("click", () => $("#detail").close());

// Optioneel een andere backend: ?api=http://localhost:9000
const BACKEND_URL = new URLSearchParams(location.search).get("api") || "http://localhost:8001";
// Open de pagina met ?stt=1 om alleen spraak-naar-tekst te testen (zonder AI-model).
const STT_ONLY = new URLSearchParams(location.search).has("stt");
const history = [];

function syncCheckboxes() {
  document.querySelectorAll(".filters input").forEach((i) => {
    i.checked = state[i.dataset.key].has(i.value);
  });
}

// Voert de actie uit die de backend teruggeeft.
function applyAction({ action, params = {} }) {
  if (action !== "recommend" && action !== "ask" && action !== "none") state.rec = null;
  if (action === "search") { state.q = params.query || ""; $("#search").value = state.q; }
  else if (action === "filter") {
    for (const k of Object.keys(facets)) {
      if (params[k] !== undefined) state[k] = new Set([String(params[k])]);
    }
    syncCheckboxes();
  } else if (action === "sort") { state.sort = params.sort_by || "name"; $("#sort").value = state.sort; }
  else if (action === "recommend") state.rec = params.recommendations || [];
  else if (action === "reset") { $("#reset").click(); return; }
  render();
  if (action === "open_module") openDetail(params.module_id);
}
const addMsg = (text, who) => {
  const d = document.createElement("div");
  d.className = `msg ${who}`; d.textContent = text;
  $("#chat-msgs").append(d); $("#chat-msgs").scrollTop = 1e9;
};
async function botReply(text) {
  try {
    const res = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, history: history.slice(-10) }),
    });
    if (!res.ok) throw new Error(res.status);
    const data = await res.json();
    applyAction(data);
    history.push({ role: "user", content: text }, { role: "assistant", content: data.reply });
    return data.reply;
  } catch {
    return "Ik kan de backend niet bereiken.";
  }
}
$("#chat-toggle").addEventListener("click", () => { $("#chat").hidden = !$("#chat").hidden; });

// Spraak: opnemen in de browser, uploaden naar /voice (faster-whisper + Claude).
let recorder = null;
$("#chat-mic").addEventListener("click", async () => {
  const mic = $("#chat-mic");
  if (recorder) { recorder.stop(); return; }
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); }
  catch { addMsg("Geen toegang tot de microfoon.", "bot"); return; }
  const chunks = [];
  recorder = new MediaRecorder(stream);
  recorder.ondataavailable = (e) => chunks.push(e.data);
  recorder.onstop = async () => {
    stream.getTracks().forEach((t) => t.stop());
    recorder = null;
    mic.classList.remove("rec");
    const form = new FormData();
    form.append("audio", new Blob(chunks, { type: chunks[0]?.type || "audio/webm" }), "opname.webm");
    if (!STT_ONLY) form.append("history", JSON.stringify(history.slice(-10)));
    const wait = document.createElement("div");
    wait.className = "msg bot"; wait.textContent = "Bezig met verstaan…";
    $("#chat-msgs").append(wait);
    try {
      const res = await fetch(`${BACKEND_URL}${STT_ONLY ? "/transcribe" : "/voice"}`, { method: "POST", body: form });
      if (!res.ok) throw new Error(res.status);
      const data = await res.json();
      wait.remove();
      if (STT_ONLY) { addMsg(data.transcript ? `🎤 ${data.transcript}` : "Niets verstaan.", "user"); return; }
      if (data.transcript) {
        addMsg(data.transcript, "user");
        applyAction(data);
        history.push({ role: "user", content: data.transcript }, { role: "assistant", content: data.reply });
      }
      addMsg(data.reply, "bot");
    } catch {
      wait.textContent = "Spraak verwerken mislukt.";
    }
  };
  recorder.start();
  mic.classList.add("rec");
});
$("#chat-close").addEventListener("click", () => { $("#chat").hidden = true; });
$("#chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const t = $("#chat-input").value.trim();
  if (!t) return;
  $("#chat-input").value = "";
  addMsg(t, "user");
  addMsg(await botReply(t), "bot");
});

(async function init() {
  try {
    const res = await fetch(`${BACKEND_URL}/modules`);
    if (!res.ok) throw new Error(res.status);
    MODULES = await res.json();
  } catch {
    $("#count").textContent = "Kan de minors niet laden. Draait de backend op poort 8001?";
    return;
  }
  renderFilters();
  render();
})();
