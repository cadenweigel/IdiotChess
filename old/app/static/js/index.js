const modeSelect = document.getElementById("mode");
const vsBotSettings = document.getElementById("vs-bot-settings");
const botVsBotSettings = document.getElementById("bot-vs-bot-settings");

let botMap = {};

async function loadBotOptions() {
  try {
    const res = await fetch("/api/bots");
    const data = await res.json();
    const botList = data.bots || [];

    botMap = Object.fromEntries(botList.map(bot => [bot.id, bot]));

    const whiteSelect = document.getElementById("white-bot");
    const blackSelect = document.getElementById("black-bot");

    whiteSelect.innerHTML = "";
    blackSelect.innerHTML = "";

    botList.forEach(bot => {
      const option = document.createElement("option");
      option.value = bot.id;
      option.textContent = bot.name;

      if (bot.id.startsWith("white_")) whiteSelect.appendChild(option);
      if (bot.id.startsWith("black_")) blackSelect.appendChild(option);
    });

    updateBotDescriptions(); // initial description
    updateVsBotDescription();
    whiteSelect.addEventListener("change", updateBotDescriptions);
    blackSelect.addEventListener("change", updateBotDescriptions);
  } catch (err) {
    console.error("Failed to load bots:", err);
  }
}

function updateVsBotDescription() {
  const selected = document.getElementById("bot-choice").value;
  const id = selected === "white" ? "white_idiot" : "black_idiot";
  const bot = botMap[id] || {};

  document.getElementById("vs-bot-description").textContent = bot.description || "";
  document.getElementById("vs-bot-avatar").src = `/static/images/avatars/${bot.avatar || "default.png"}`;
}


document.addEventListener("DOMContentLoaded", () => {
  loadBotOptions();
  document.getElementById("bot-choice").addEventListener("change", updateVsBotDescription);
});

function updateBotDescriptions() {
  const whiteId = document.getElementById("white-bot").value;
  const blackId = document.getElementById("black-bot").value;

  const white = botMap[whiteId] || {};
  const black = botMap[blackId] || {};

  document.getElementById("white-bot-description").textContent = white.description || "";
  document.getElementById("black-bot-description").textContent = black.description || "";

  document.getElementById("white-bot-avatar").src = `/static/images/avatars/${white.avatar || "default.png"}`;
  document.getElementById("black-bot-avatar").src = `/static/images/avatars/${black.avatar || "default.png"}`;
}


document.addEventListener("DOMContentLoaded", () => {
  loadBotOptions();
});

modeSelect.addEventListener("change", () => {
  const mode = modeSelect.value;
  vsBotSettings.style.display = mode === "vs-bot" ? "block" : "none";
  botVsBotSettings.style.display = mode === "bot-vs-bot" ? "block" : "none";
});

document.getElementById("start-game-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const mode = modeSelect.value;

  let response;
  try {
    if (mode === "vs-bot") {
      const botColor = document.getElementById("bot-choice").value;
      response = await fetch("/api/new-game/bot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bot_color: botColor })
      });
    } else {
      const whiteBot = document.getElementById("white-bot").value;
      const blackBot = document.getElementById("black-bot").value;
      response = await fetch("/api/new-game/bots", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ white_bot: whiteBot, black_bot: blackBot })
      });
    }

    const data = await response.json();
    if (data.session_id) {
      window.location.href = `/play?session_id=${data.session_id}`;
    } else {
      alert("Failed to start game.");
    }
  } catch (err) {
    console.error("Error starting game:", err);
    alert("Could not start game.");
  }
});
