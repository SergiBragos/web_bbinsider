//script.js

const form = document.getElementById("shotmap-form");
const img = document.getElementById("shotmap-img");
const progressContainer = document.getElementById("progress-container");
const progressBar = document.getElementById("progress-bar");
const assistedDiv = document.getElementById("assisted-stats");
// Estat global dels partits seleccionats
const selectedMatches = new Set();

//Execució quan s'activa el botó de submit
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  //console.log("Botó clicat")
  const matchIds = document.getElementById("match_ids").value;
  const team = document.getElementById("team").value;
  const player = document.getElementById("player").value;
  const showIndividualShots = document.getElementById("show-ind-shots").checked;

  let url = `/shotmap?match_ids=${matchIds}&team=${team}&show_individual_shots=${showIndividualShots}`;
  if (player.trim() !== "") {
    url += `&player=${encodeURIComponent(player)}`;
  }

  // 1️⃣ Activa backend
  img.src = url + "&t=" + Date.now();

  // 2️⃣ ACTIVA IMMEDIATAMENT LA BARRA
  startBatchProgress(matchIds);

  // Crea l'url per renderitzar la taula" Assisted"
  let url_ass = `/assisted?match_ids=${matchIds}&team=${team}`;
  if (player.trim() !== "") {
    url_ass += `&player=${encodeURIComponent(player)}`;
  }

  // 3️⃣ Fetch assisted (pot anar en paral·lel)
  const res = await fetch(url_ass);
  const data = await res.json();
  renderAssistedStats(data);

});



//Funció que fa refrescar la barra de progrés cada cop que es demana l'anàlisi d'un nou partit.
function startBatchProgress(matchIds) {
  console.log("Analitzant partits");
  
  progressContainer.classList.remove("inactive");
  progressBar.style.width = "0%";
  progressContainer.textContent = "Starting analysis...";

  pollBatchProgress(matchIds);
}



//Aquí s'analitzen els partits
async function pollBatchProgress(matchIds) {
  const matches = matchIds.split(",").map(m => m.trim());
  const total = matches.length;
  const start = Date.now();

  const interval = setInterval(async () => {
    // ⛔ tall de seguretat: 1 minut
    if (Date.now() - start > 60000) {
      clearInterval(interval);
      progressBar.textContent = "Timeout while processing matches";
      return;
    }

    const res = await fetch(`/progress_batch?match_ids=${matchIds}`);
    const data = await res.json();

    const done = data.done ?? 0;
    const pct = Math.floor(done / total * 100);

    progressBar.style.width = pct + "%";
    progressContainer.textContent = `Processed ${done} / ${total} matches`;

    if (done >= total) {
      clearInterval(interval);
      //progressContainer.classList.add("inactive");
    }
  }, 2000);
}



// Funció que renderitza el diccionari d'assistències
function renderAssistedStats(assisted) {

  assistedDiv.innerHTML = `
    <table class="assisted-table">
      <thead>
        <tr>
          <th>Shot Type</th>
          <th>Scored</th>
          <th>Attempts</th>
          <th>%</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Assisted 2P</td>
          <td>${assisted.a2[0]}</td>
          <td>${assisted.a2[1]}</td>
          <td>${(assisted.a2[0] / Math.max(1, assisted.a2[1]) * 100).toFixed(1)}%</td>
        </tr>
        <tr>
          <td>Unassisted 2P</td>
          <td>${assisted.u2[0]}</td>
          <td>${assisted.u2[1]}</td>
          <td>${(assisted.u2[0] / Math.max(1, assisted.u2[1]) * 100).toFixed(1)}%</td>
        </tr>
        <tr>
          <td>Assisted 3P</td>
          <td>${assisted.a3[0]}</td>
          <td>${assisted.a3[1]}</td>
          <td>${(assisted.a3[0] / Math.max(1, assisted.a3[1]) * 100).toFixed(1)}%</td>
        </tr>
        <tr>
          <td>Unassisted 3P</td>
          <td>${assisted.u3[0]}</td>
          <td>${assisted.u3[1]}</td>
          <td>${(assisted.u3[0] / Math.max(1, assisted.u3[1]) * 100).toFixed(1)}%</td>
        </tr>
      </tbody>
    </table>
  `;
}


//Funció que carrega el calendari d'un equip
async function loadSchedule() {
  const teamid = document.getElementById("teamid").value;
  const season = document.getElementById("season").value;
  const matchesContainer = document.getElementById("matches");

  matchesContainer.innerHTML = "Loading...";

  const res = await fetch(`/api/schedule?teamid=${teamid}&season=${season}`);
  const data = await res.json();

  matchesContainer.innerHTML = "";

  data.forEach(m => {
    const btn = document.createElement("button");
    const typeClass = m.type.replaceAll(".", "-");
    btn.className = `match-btn ${typeClass}`; //per pintar els botons segons el tipus de partit
    btn.dataset.matchId = m.match_id;

    const date = new Date(m.date).toLocaleDateString();
    btn.textContent = `${date} · ${typeClass} · ${m.match_id}`;

    btn.onclick = () => loadMatch(m.match_id, m.type, date, btn);

    matchesContainer.appendChild(btn);
  });
}


function loadMatch(matchId, type, date, button) {
  if (selectedMatches.has(matchId)) {
    selectedMatches.delete(matchId);
    button.classList.remove("selected");
  } else {
    selectedMatches.add(matchId);
    button.classList.add("selected");
  }

  renderSelectedMatches(type, date);
}


function renderSelectedMatches(type, date) {
  const container = document.getElementById("selected-matches");
  container.innerHTML = "";

  selectedMatches.forEach(matchId => {
    const card = document.createElement("div");
    card.className = "match-card";

    const span = document.createElement("span");
    span.textContent = matchId;

    const removeBtn = document.createElement("button");
    removeBtn.textContent = "✕";
    removeBtn.className = "remove-btn";

    removeBtn.onclick = () => {
      // eliminar del Set
      selectedMatches.delete(matchId);
      updateMatchIds();
      renderSelectedMatches();
    }

    card.appendChild(span);
    card.appendChild(removeBtn);
    container.appendChild(card);
  });

  updateMatchIds();
}

function updateMatchIds() {
  document.getElementById("match_ids").value =
    Array.from(selectedMatches).join(",");
}


//FUNCIONS DE L'ENTRENAMENT
const trainings = [
  "None","JS for 12","JS for 34","JS for 23","JS for team",
  "JR for 2","JR for 12","JR for 23","JR for team",
  "OD for 1","OD for 12","OD for 123",
  "HA for 1","HA for 12","HA for 123",
  "DR for 12","DR for 34","DR for team",
  "PA for 1","PA for 12","PA for team",
  "IS for 5","IS for 45","IS for 345",
  "ID for 5","ID for 45","ID for 345",
  "RB for 45","RB for team",
  "SB for 5","SB for 45","SB for 345"
];
const trainingBtn = document.getElementById("training-btn");
const planDiv = document.getElementById("plan");

trainingBtn.addEventListener("click", runTraining);

for (let i = 0; i < 28; i++) {
  const row = document.createElement("div");
  row.className = "training-element"
  const label = document.createElement("span");
  label.textContent = `Week ${i + 1}: `;

  const sel = document.createElement("select");
  trainings.forEach(t => {
    const o = document.createElement("option");
    o.value = t;
    o.textContent = t;
    sel.appendChild(o);
  });

  const copyBtn = document.createElement("button");
  copyBtn.textContent = "Copy";
  copyBtn.type = "button";
  copyBtn.onclick = () => {
    copiedTraining = sel.value;
  };

  const pasteBtn = document.createElement("button");
  pasteBtn.textContent = "Paste";
  pasteBtn.type = "button";
  pasteBtn.onclick = () => {
    if (copiedTraining) sel.value = copiedTraining;
  };

  row.append(label, sel, copyBtn, pasteBtn);
  planDiv.appendChild(row);
}

async function runTraining() {
    const playerId = document.getElementById("player_id").value;
    const coach = document.getElementById("coach").value;
    const currentWeek = document.getElementById("current_week").value;

    const trainingPlan = [...planDiv.querySelectorAll("select")]
        .map(s => s.value)
        .join("|"); // separador segur

    const url =
        `/training?player_id=${playerId}` +
        `&coach_level=${coach}` +
        `&current_week=${currentWeek}` +
        `&plan=${encodeURIComponent(trainingPlan)}`;

    const res = await fetch(url);
    const data = await res.json();

    renderTrainingResult(data)
}

function renderTrainingResult(data) {
    const output = document.getElementById("output");
    output.innerHTML = ""; // neteja prèvia

    // 🔹 Títol jugador
    const title = document.createElement("h3");
    title.textContent = `${data.name} ${data.surname} (Edat: ${data.age_at_end})`;
    output.appendChild(title);

    // 🔹 Taula
    const table = document.createElement("table");
    table.className = "skills-table";

    const thead = document.createElement("thead");
    thead.innerHTML = `
        <tr>
            <th>Skill</th>
            <th>Valor</th>
            <th>Diferència</th>
        </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");

    for (const [skill, value] of Object.entries(data.skills_by_week)) {
      const tr = document.createElement("tr");

      const tdSkill = document.createElement("td");
      tdSkill.textContent = skill;

      const tdValue = document.createElement("td");
      tdValue.textContent = value.toFixed(2);
      tdValue.style.color = getSkillColor(value);
      tdValue.style.fontWeight = "bold";

      const tdDifference = document.createElement("td");
      tdDifference.textContent = (value - data.initial_skills[skill]).toFixed(2)

      tr.appendChild(tdSkill);
      tr.appendChild(tdValue);
      tr.appendChild(tdDifference);
      tbody.appendChild(tr);
    }

    table.appendChild(tbody);
    output.appendChild(table);
}

//Funció que pinta el text d'una habilitat segons el color de BB
const SKILL_LEVELS = 
  {1: "#000000",
  2: "#121263",
  3: "#221385",
  4: "#30139F",
  5: "#700BA2",
  6: "#910B9D",
  7: "#AD0B88",
  8: "#B70B5A",
  9: "#9C0B32",
  10: "#A70B00",
  11: "#BD2600",
  12: "#CB3100",
  13: "#D93C00",
  14: "#DB6E04",
  15: "#E5A64B",
  16: "#AC860A",
  17: "#8E9800",
  18: "#498E00",
  19: "#0EAE28",
  20: "#0EB366"
};
function getSkillColor(value) {
    const level = Math.max(1, Math.min(20, Math.floor(value)));
    return SKILL_LEVELS[level];
}