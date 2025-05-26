let botMap = {};
let selectedBotType = null;
let selectedColor = 'random'; // Default to random

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
    document.getElementById("pongo-bot-avatar").src = `/static/images/avatars/${botMap["pongo"].avatar}`;
    document.getElementById("borzoi-bot-avatar").src = `/static/images/avatars/${botMap["borzoi"].avatar}`;
    document.getElementById("barrowofmonkeys-bot-avatar").src = `/static/images/avatars/${botMap["barrowofmonkeys"].avatar}`;
    document.getElementById("gigantopithecus-bot-avatar").src = `/static/images/avatars/${botMap["gigantopithecus"].avatar}`;
    
    // Initially disable the start button
    document.querySelector('button[type="submit"]').disabled = true;
  } catch (err) {
    console.error("Failed to load bots:", err);
  }
}

function updateColorOptions(botCard) {
  const botColor = botCard?.dataset.botColor;
  const colorOptions = document.querySelectorAll('.color-option');
  
  // First, enable all color options
  colorOptions.forEach(option => {
    option.classList.remove('disabled');
    option.classList.remove('selected');
  });

  // If a fixed-color bot is selected, disable and select the opposite color
  if (botColor === 'white') {
    const blackOption = document.querySelector('.color-option[data-color="black"]');
    blackOption.classList.add('selected');
    selectedColor = 'black';
    colorOptions.forEach(option => {
      if (option.dataset.color !== 'black') {
        option.classList.add('disabled');
      }
    });
  } else if (botColor === 'black') {
    const whiteOption = document.querySelector('.color-option[data-color="white"]');
    whiteOption.classList.add('selected');
    selectedColor = 'white';
    colorOptions.forEach(option => {
      if (option.dataset.color !== 'white') {
        option.classList.add('disabled');
      }
    });
  } else {
    // For Pongo, select the previously selected color or default to random
    const previousOption = document.querySelector(`.color-option[data-color="${selectedColor}"]`);
    previousOption.classList.add('selected');
  }
}

function selectBot(botCard) {
  // Remove selection from all cards
  document.querySelectorAll('.bot-card').forEach(card => {
    card.classList.remove('selected');
  });
  
  // Add selection to clicked card
  botCard.classList.add('selected');
  selectedBotType = botCard.dataset.botType;
  
  // Update color options based on selected bot
  updateColorOptions(botCard);
  
  // Enable the start button
  document.querySelector('button[type="submit"]').disabled = false;
}

function selectColor(colorOption) {
  const selectedBot = document.querySelector('.bot-card.selected');
  const botColor = selectedBot?.dataset.botColor;
  
  // If a fixed-color bot is selected, don't allow color change
  if (botColor) return;
  
  // Remove selection from all color options
  document.querySelectorAll('.color-option').forEach(option => {
    option.classList.remove('selected');
  });
  
  // Add selection to clicked option
  colorOption.classList.add('selected');
  selectedColor = colorOption.dataset.color;
}

document.addEventListener("DOMContentLoaded", () => {
  loadBotOptions();
  
  // Add click handlers to bot cards
  document.querySelectorAll('.bot-card').forEach(card => {
    card.addEventListener('click', () => selectBot(card));
  });
  
  // Add click handlers to color options
  document.querySelectorAll('.color-option').forEach(option => {
    option.addEventListener('click', () => {
      if (!option.classList.contains('disabled')) {
        selectColor(option);
      }
    });
  });
  
  // Select random color by default
  document.querySelector('.color-option[data-color="random"]').classList.add('selected');
});

document.getElementById("start-game-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  if (!selectedBotType) {
    alert("Please select a bot to play against");
    return;
  }
  
  try {
    const response = await fetch("/api/new-game/bot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        bot_type: selectedBotType,
        player_color: selectedColor // Send the player's color preference
      })
    });
    
    const data = await response.json();
    if (data.session_id) {
      window.location.href = `/play?session_id=${data.session_id}&bot_color=${data.bot_color}&bot_type=${selectedBotType}`;
    } else {
      alert("Failed to start game.");
    }
  } catch (err) {
    console.error("Error starting game:", err);
    alert("Could not start game.");
  }
});
