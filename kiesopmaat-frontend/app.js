const $ = (s) => document.querySelector(s);
const state = { q: "", level: new Set(), theme: new Set(), period: new Set(), ec: new Set(), sort: "name" };
const facets = { level: "#f-level", theme: "#f-theme", period: "#f-period", ec: "#f-ec" };

function renderFilters() {
  for (const [key, sel] of Object.entries(facets)) {
    const values = [...new Set(MODULES.map((m) => String(m[key])))].sort();
    $(sel).innerHTML = values
      .map((v) => `<label><input type="checkbox" data-key="${key}" value="${v}"> ${v}</label>`)
      .join("");
  }
}

function filtered() {
  const q = state.q.toLowerCase();
  const list = MODULES.filter((m) =>
    (!q || `${m.name} ${m.description} ${m.theme}`.toLowerCase().includes(q)) &&
    Object.keys(facets).every((k) => !state[k].size || state[k].has(String(m[k])))
  );
  const by = { name: (a, b) => a.name.localeCompare(b.name), ec: (a, b) => a.ec - b.ec, period: (a, b) => a.period.localeCompare(b.period) };
  return list.sort(by[state.sort]);
}

function render() {
  const list = filtered();
  $("#count").textContent = `${list.length} module${list.length === 1 ? "" : "s"} gevonden`;
  $("#grid").innerHTML = list.map((m) => `
    <button class="card" data-id="${m.id}">
      <div class="tags"><span class="tag ec">${m.ec} EC</span><span class="tag">${m.level}</span></div>
      <h3>${m.name}</h3>
      <p>${m.description}</p>
      <div class="tags"><span class="tag">${m.theme}</span><span class="tag">${m.period}</span></div>
    </button>`).join("") || "<p>Geen modules gevonden.</p>";
}

function openDetail(id) {
  const m = MODULES.find((x) => x.id === id);
  $("#detail-body").innerHTML = `
    <h2>${m.name}</h2>
    <div class="tags"><span class="tag ec">${m.ec} EC</span><span class="tag">${m.level}</span><span class="tag">${m.theme}</span><span class="tag">${m.period}</span></div>
    <p>${m.description}</p>
    <button class="btn">Inschrijven</button>`;
  $("#detail").showModal();
}

document.addEventListener("change", (e) => {
  const key = e.target.dataset && e.target.dataset.key;
  if (key) {
    e.target.checked ? state[key].add(e.target.value) : state[key].delete(e.target.value);
    render();
  }
});
$("#search-form").addEventListener("submit", (e) => { e.preventDefault(); state.q = $("#search").value; render(); });
$("#search").addEventListener("input", (e) => { state.q = e.target.value; render(); });
$("#sort").addEventListener("change", (e) => { state.sort = e.target.value; render(); });
$("#reset").addEventListener("click", () => {
  Object.keys(facets).forEach((k) => state[k].clear());
  state.q = ""; $("#search").value = "";
  document.querySelectorAll(".filters input").forEach((i) => (i.checked = false));
  render();
});
$("#grid").addEventListener("click", (e) => {
  const card = e.target.closest(".card");
  if (card) openDetail(Number(card.dataset.id));
});
$("#detail-close").addEventListener("click", () => $("#detail").close());

// Chat UI (nog zonder backend): vervang `botReply` door je AI-call.
const addMsg = (text, who) => {
  const d = document.createElement("div");
  d.className = `msg ${who}`; d.textContent = text;
  $("#chat-msgs").append(d); $("#chat-msgs").scrollTop = 1e9;
};
async function botReply(text) {
  return "Chatbot is nog niet gekoppeld aan een backend.";
}
$("#chat-toggle").addEventListener("click", () => { $("#chat").hidden = !$("#chat").hidden; });
$("#chat-close").addEventListener("click", () => { $("#chat").hidden = true; });
$("#chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const t = $("#chat-input").value.trim();
  if (!t) return;
  $("#chat-input").value = "";
  addMsg(t, "user");
  addMsg(await botReply(t), "bot");
});

renderFilters();
render();
