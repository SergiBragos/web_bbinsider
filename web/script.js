const form = document.getElementById("shotmap-form");
const img = document.getElementById("shotmap-img");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const matchIds = document.getElementById("match_ids").value;
  const team = document.getElementById("team").value;
  const player = document.getElementById("player").value;

  if (!matchIds.trim()) {
    alert("Introdueix almenys un Match ID");
    return;
  }

  let url = `http://127.0.0.1:8000/shotmap?match_ids=${matchIds}&team=${team}`;

  if (player.trim() !== "") {
    url += `&player=${encodeURIComponent(player)}`;
  }

  // Evitar cache
  img.src = url + "&t=" + new Date().getTime();
});
