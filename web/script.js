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

  const matchIds = document.getElementById("match_ids").value;
  const team = document.getElementById("team").value;
  const player = document.getElementById("player").value;
  const showIndividualShots = document.getElementById("show-ind-shots").checked;

  let url = `/shotmap?match_ids=${matchIds}&team=${team}&show_individual_shots=${showIndividualShots}`;
  if (player.trim() !== "") {
    url += `&player=${encodeURIComponent(player)}`;
  }

  // 1️⃣ AQUEST GET ÉS EL QUE ACTIVA EL BACKEND
  img.src = url + "&t=" + Date.now();

    // 2️⃣ JSON (fetch)
  
  let url_ass = `/assisted?match_ids=${matchIds}&team=${team}`
  if (player.trim() !== "") {
    url_ass += `&player=${encodeURIComponent(player)}`;
  }
  const res = await fetch(url_ass);
  const data = await res.json();

  // Renderitzar el diccionari d'assistències l qui hem anomenat data
  renderAssistedStats(data);
  
  // 3: barra de progrés per cada partit
  processMatches(matchIds);
});


//Funció que crida a processar els partits d'un en un
async function processMatches(matchIds) {
  const matches = matchIds.split(",").map(m => m.trim());

  for (const matchId of matches) {
    await pollSingleMatch(matchId);
  }
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

//Barra de progrés que va creixent per a cada partit
function pollSingleMatch(matchId) {
  return new Promise((resolve) => {
    progressContainer.classList.remove("inactive");

    const interval = setInterval(async () => {
      const res = await fetch(`/progress/${matchId}`);
      const data = await res.json();

      const pct = data.progress ?? 0;
      progressBar.style.width = pct + "%";
      progressBar.textContent = `Match ${matchId}: ${pct}%`;

      if (pct >= 100) {
        clearInterval(interval);

        setTimeout(() => {
          progressContainer.classList.add("inactive");
          progressBar.style.width = "0%";
          progressBar.textContent = "0%";
          resolve();
        }, 500);
      }
    }, 400);
  });
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
