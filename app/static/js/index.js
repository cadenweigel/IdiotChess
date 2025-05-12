let botMap = {};
let selectedBotColor = null;

async function loadBotOptions() {
  try {
    const res = await fetch("/api/bots");
    const data = await res.json();
    const botList = data.bots || [];

    // Create a map of bot IDs to their full information
    botMap = Object.fromEntries(botList.map(bot => [bot.id, bot]));
    
    // Set initial bot avatars
    document.getElementById("white-bot-avatar").src = `/static/images/avatars/${botMap["white_idiot"].avatar}`;
    document.getElementById("black-bot-avatar").src = `/static/images/avatars/${botMap["black_idiot"].avatar}`;
    
    // Initially disable the start button
    document.querySelector('button[type="submit"]').disabled = true;
  } catch (err) {
    console.error("Failed to load bots:", err);
  }
}

function selectBot(botCard) {
  // Remove selection from all cards
  document.querySelectorAll('.bot-card').forEach(card => {
    card.classList.remove('selected');
  });
  
  // Add selection to clicked card
  botCard.classList.add('selected');
  selectedBotColor = botCard.dataset.botColor;
  
  // Enable the start button
  document.querySelector('button[type="submit"]').disabled = false;
}

document.addEventListener("DOMContentLoaded", () => {
  loadBotOptions();
  
  // Add click handlers to bot cards
  document.querySelectorAll('.bot-card').forEach(card => {
    card.addEventListener('click', () => selectBot(card));
  });
});

document.getElementById("start-game-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  if (!selectedBotColor) {
    alert("Please select a bot to play against");
    return;
  }
  
  try {
    const response = await fetch("/api/new-game/bot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bot_color: selectedBotColor })
    });
    
    const data = await response.json();
    if (data.session_id) {
      const playUrl = `/play?session_id=${data.session_id}&bot_color=${selectedBotColor}`;
      console.log('Redirecting to:', playUrl); // Debug log
      window.location.href = playUrl;
    } else {
      alert("Failed to start game.");
    }
  } catch (err) {
    console.error("Error starting game:", err);
    alert("Could not start game.");
  }
});
