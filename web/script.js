const form = document.getElementById("shotmap-form");
const img = document.getElementById("shotmap-img");
const progressContainer = document.getElementById("progress-container");
const progressBar = document.getElementById("progress-bar");


//Execució quan s'activa el botó de submit
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const matchIds = document.getElementById("match_ids").value;
  const team = document.getElementById("team").value;
  const player = document.getElementById("player").value;

  let url = `/shotmap?match_ids=${matchIds}&team=${team}`;
  if (player.trim() !== "") {
    url += `&player=${encodeURIComponent(player)}`;
  }

  // 🔥 1️⃣ AQUEST GET ÉS EL QUE ACTIVA EL BACKEND
  img.src = url + "&t=" + Date.now();

  // 🔁 2️⃣ ARA SÍ: barra de progrés per cada partit
  processMatches(matchIds);
});



//Funció que crida a processar els partits d'un en un
async function processMatches(matchIds) {
  const matches = matchIds.split(",").map(m => m.trim());

  for (const matchId of matches) {
    await pollSingleMatch(matchId);
  }
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
