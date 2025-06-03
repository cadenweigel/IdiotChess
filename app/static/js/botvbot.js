import { initializeBoard, updateBoard as updateBoardDisplay } from './boardUI.js';
import { clearMoveHistory, initializeMoveHistory } from './moveHistory.js';
import { fetchBoardState } from './eventHandlers.js';
import { 
    initializeDOMElements, 
    updateTurnIndicator, 
    setSessionId, 
    setGameStarted,
    setBotColors,
    setWhiteBot,
    setBlackBot
} from './gameState.js';

let sessionId = null;
let whiteBot = null;
let blackBot = null;
let gameStarted = false;

const statusMessage = document.getElementById('status-message');
const movesList = document.getElementById('moves-list');
const startBtn = document.getElementById('start-botvbot-btn');
const whiteBotSelect = document.getElementById('white-bot-select');
const blackBotSelect = document.getElementById('black-bot-select');

async function loadBotOptions() {
    const res = await fetch('/api/bots');
    const data = await res.json();
    const bots = data.bots || [];
    whiteBotSelect.innerHTML = '';
    blackBotSelect.innerHTML = '';
    bots.forEach(bot => {
        const optionW = document.createElement('option');
        optionW.value = bot.id;
        optionW.textContent = bot.display_name || bot.name;
        optionW.dataset.avatar = bot.avatar;
        whiteBotSelect.appendChild(optionW);
        const optionB = document.createElement('option');
        optionB.value = bot.id;
        optionB.textContent = bot.display_name || bot.name;
        optionB.dataset.avatar = bot.avatar;
        blackBotSelect.appendChild(optionB);
    });
}

function updateBotAvatarsAndNames() {
    const whiteAvatar = document.getElementById('white-avatar');
    const blackAvatar = document.getElementById('black-avatar');
    const whiteName = document.getElementById('white-name');
    const blackName = document.getElementById('black-name');
    const selectedWhite = whiteBotSelect.options[whiteBotSelect.selectedIndex];
    const selectedBlack = blackBotSelect.options[blackBotSelect.selectedIndex];
    whiteAvatar.src = `/static/images/avatars/${selectedWhite.dataset.avatar}`;
    blackAvatar.src = `/static/images/avatars/${selectedBlack.dataset.avatar}`;
    whiteName.textContent = selectedWhite.textContent;
    blackName.textContent = selectedBlack.textContent;
}

async function startBotvBotGame() {
    whiteBot = whiteBotSelect.value;
    blackBot = blackBotSelect.value;
    updateBotAvatarsAndNames();
    const response = await fetch('/api/new-game/bots', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ white_bot: whiteBot, black_bot: blackBot })
    });
    const data = await response.json();
    if (data.session_id) {
        sessionId = data.session_id;
        setSessionId(sessionId);
        setBotColors(whiteBot, blackBot);
        setWhiteBot(whiteBot);
        setBlackBot(blackBot);
        setGameStarted(true);
        gameStarted = true;
        statusMessage.textContent = 'Game ongoing';
        clearMoveHistory();
        initializeBoard();
        initializeMoveHistory();
        playBotvBot();
    } else {
        statusMessage.textContent = 'Failed to start game.';
    }
}

async function playBotvBot() {
    if (!gameStarted) return;
    let state = await fetchBoardState();
    if (state.status && (state.status.includes('checkmate') || state.status.includes('draw') || state.status.includes('stalemate'))) {
        showGameOver(state.status);
        return;
    }
    // Make bot move
    await makeBotMove();
    // Update board and move history
    await updateBoardDisplay();
    // Continue if not game over
    setTimeout(playBotvBot, 600); // Add a delay for visibility
}

async function makeBotMove() {
    const response = await fetch('/api/bot-move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    });
    await response.json(); // Ignore details, board will update
}

function showGameOver(message) {
    const gameOverOverlay = document.getElementById('game-over-overlay');
    const gameOverMessage = document.getElementById('game-over-message');
    const gameOverDetails = document.getElementById('game-over-details');
    if (message.includes('checkmate')) {
        const winner = message.includes('White') ? 'White' : 'Black';
        gameOverMessage.textContent = 'Checkmate!';
        gameOverDetails.textContent = `${winner} wins!`;
    } else if (message.includes('stalemate')) {
        gameOverMessage.textContent = 'Stalemate!';
        gameOverDetails.textContent = 'The game is a draw.';
    } else if (message.includes('draw')) {
        gameOverMessage.textContent = 'Game Drawn';
        gameOverDetails.textContent = message;
    }
    gameOverOverlay.style.display = 'flex';
    statusMessage.textContent = message;
}

startBtn.addEventListener('click', () => {
    if (whiteBotSelect.value && blackBotSelect.value) {
        startBotvBotGame();
    }
});

whiteBotSelect.addEventListener('change', updateBotAvatarsAndNames);
blackBotSelect.addEventListener('change', updateBotAvatarsAndNames);

document.addEventListener('DOMContentLoaded', async () => {
    initializeDOMElements();
    await loadBotOptions();
    updateBotAvatarsAndNames();
}); 