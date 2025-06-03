import { initializeBoard, updateBoard as updateBoardDisplay, lastMove } from './boardUI.js';
import { clearMoveHistory, initializeMoveHistory, addMoveToHistory } from './moveHistory.js';
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
let gameSpeed = 3; // Default speed (1-5)
let moveDelay = 1000; // Default delay in ms
let isPaused = false;
let gameTimeout = null;

const statusMessage = document.getElementById('status-message');
const movesList = document.getElementById('moves-list');
const startBtn = document.getElementById('start-botvbot-btn');
const whiteBotSelect = document.getElementById('white-bot-select');
const blackBotSelect = document.getElementById('black-bot-select');
const speedSlider = document.getElementById('game-speed');
const speedValue = document.getElementById('speed-value');
const pauseBtn = document.getElementById('pause-btn');
const pauseIcon = pauseBtn.querySelector('.pause-icon');
const playIcon = pauseBtn.querySelector('.play-icon');

// Speed mapping (1-5 to actual delays in ms)
const SPEED_DELAYS = {
    1: 2000,  // Very Slow
    2: 1500,  // Slow
    3: 1000,  // Normal
    4: 500,   // Fast
    5: 250    // Very Fast
};

// Speed labels
const SPEED_LABELS = {
    1: 'Very Slow',
    2: 'Slow',
    3: 'Normal',
    4: 'Fast',
    5: 'Very Fast'
};

// Update speed when slider changes
speedSlider.addEventListener('input', (e) => {
    gameSpeed = parseInt(e.target.value);
    moveDelay = SPEED_DELAYS[gameSpeed];
    speedValue.textContent = SPEED_LABELS[gameSpeed];
});

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
    // Set default: white = white_idiot (Wyatt), black = black_idiot (Moose)
    whiteBotSelect.value = 'white_idiot';
    blackBotSelect.value = 'black_idiot';
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

function updateBotSelectOptions() {
    // Only prevent Wyatt vs Wyatt and Moose vs Moose
    const whiteValue = whiteBotSelect.value;
    const blackValue = blackBotSelect.value;
    // Enable all first
    for (let i = 0; i < whiteBotSelect.options.length; i++) {
        whiteBotSelect.options[i].disabled = false;
        blackBotSelect.options[i].disabled = false;
    }
    // Only disable if both are white_idiot or both are black_idiot
    if (blackValue === 'white_idiot') {
        for (let i = 0; i < whiteBotSelect.options.length; i++) {
            if (whiteBotSelect.options[i].value === 'white_idiot') {
                whiteBotSelect.options[i].disabled = true;
            }
        }
    }
    if (whiteValue === 'white_idiot') {
        for (let i = 0; i < blackBotSelect.options.length; i++) {
            if (blackBotSelect.options[i].value === 'white_idiot') {
                blackBotSelect.options[i].disabled = true;
            }
        }
    }
    if (blackValue === 'black_idiot') {
        for (let i = 0; i < whiteBotSelect.options.length; i++) {
            if (whiteBotSelect.options[i].value === 'black_idiot') {
                whiteBotSelect.options[i].disabled = true;
            }
        }
    }
    if (whiteValue === 'black_idiot') {
        for (let i = 0; i < blackBotSelect.options.length; i++) {
            if (blackBotSelect.options[i].value === 'black_idiot') {
                blackBotSelect.options[i].disabled = true;
            }
        }
    }
    // If both are the same and are white_idiot or black_idiot, auto-change black
    if (whiteValue && blackValue && whiteValue === blackValue && (whiteValue === 'white_idiot' || whiteValue === 'black_idiot')) {
        for (let i = 0; i < blackBotSelect.options.length; i++) {
            if (!blackBotSelect.options[i].disabled) {
                blackBotSelect.selectedIndex = i;
                break;
            }
        }
    }
}

function renderDefaultBoard() {
    const chessboard = document.getElementById('chessboard');
    if (!chessboard) return;
    chessboard.innerHTML = '';
    const game = new window.Chess(); // chess.js global
    const board = game.board(); // 2D array of pieces
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const square = document.createElement('div');
            const isLightSquare = (row + col) % 2 === 0;
            square.className = `square ${isLightSquare ? 'light' : 'dark'}`;
            square.dataset.position = `${row},${col}`;
            // Add piece if present
            const piece = board[row][col];
            if (piece) {
                const color = piece.color === 'w' ? 'white' : 'black';
                const type = piece.type;
                const pieceNames = {
                    'p': 'pawn',
                    'n': 'knight',
                    'b': 'bishop',
                    'r': 'rook',
                    'q': 'queen',
                    'k': 'king'
                };
                const img = document.createElement('img');
                img.src = `static/images/pieces/${color}_${pieceNames[type]}.png`;
                img.className = 'piece-image';
                square.appendChild(img);
            }
            chessboard.appendChild(square);
        }
    }
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
        isPaused = false;
        pauseBtn.disabled = false;
        pauseIcon.style.display = 'inline-block';
        playIcon.style.display = 'none';
        statusMessage.textContent = 'Game ongoing';
        startBtn.style.display = 'none';  // Hide the start button when game starts
        clearMoveHistory();
        initializeBoard(); // Only call this after a game is started
        initializeMoveHistory();
        playBotvBot();
    } else {
        statusMessage.textContent = 'Failed to start game.';
    }
}

async function playBotvBot() {
    if (!gameStarted || isPaused) return;
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
    gameTimeout = setTimeout(playBotvBot, moveDelay); // Store the timeout ID
}

async function makeBotMove() {
    // Get the current state before making the move to know whose turn it is
    const currentState = await fetchBoardState();
    
    // Check if game is already over
    if (currentState.status && (currentState.status.includes('checkmate') || currentState.status.includes('draw') || currentState.status.includes('stalemate'))) {
        showGameOver(currentState.status);
        return;
    }
    
    const moveColor = currentState.turn;  // Store the color before making the move

    const response = await fetch('/api/bot-move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    });
    const data = await response.json();
    
    if (data.success) {
        // Only proceed with move processing if we have valid move data
        if (data.move && data.move.from && data.move.to) {
            // Get the piece that was moved
            const fromSquare = data.move.from;
            const piece = currentState.board[fromSquare[0]][fromSquare[1]];
            
            // Set lastMove for animation
            lastMove.from = data.move.from;
            lastMove.to = data.move.to;
            lastMove.piece = {
                type: piece.type,
                color: piece.color,
                symbol: piece.symbol
            };
            
            // Add move to history
            addMoveToHistory(
                data.move.from,
                data.move.to,
                moveColor  // Use the stored color instead of getting it after the move
            );
        }
        
        // Update board display regardless of whether we had a move
        await updateBoardDisplay();
        
        // Check if game is over after the move
        const newState = await fetchBoardState();
        if (newState.status && (newState.status.includes('checkmate') || newState.status.includes('draw') || newState.status.includes('stalemate'))) {
            showGameOver(newState.status);
            return;
        }
    }
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
    startBtn.style.display = 'block';  // Show the start button again when game is over
    pauseBtn.disabled = true;  // Disable pause button when game is over
    gameStarted = false;  // Reset game state
    setGameStarted(false);
    if (gameTimeout) {
        clearTimeout(gameTimeout);
        gameTimeout = null;
    }
}

// Handle pause/play button
pauseBtn.addEventListener('click', () => {
    if (!gameStarted) return;
    
    isPaused = !isPaused;
    if (isPaused) {
        // Pause the game
        if (gameTimeout) {
            clearTimeout(gameTimeout);
            gameTimeout = null;
        }
        pauseIcon.style.display = 'none';
        playIcon.style.display = 'inline-block';
        statusMessage.textContent = 'Game paused';
    } else {
        // Resume the game
        pauseIcon.style.display = 'inline-block';
        playIcon.style.display = 'none';
        statusMessage.textContent = 'Game ongoing';
        playBotvBot(); // Continue the game
    }
});

startBtn.addEventListener('click', () => {
    if (whiteBotSelect.value && blackBotSelect.value) {
        startBotvBotGame();
    }
});

whiteBotSelect.addEventListener('change', () => {
    updateBotAvatarsAndNames();
    updateBotSelectOptions();
});
blackBotSelect.addEventListener('change', () => {
    updateBotAvatarsAndNames();
    updateBotSelectOptions();
});

document.addEventListener('DOMContentLoaded', async () => {
    initializeDOMElements();
    await loadBotOptions();
    updateBotAvatarsAndNames();
    updateBotSelectOptions();
    renderDefaultBoard(); // Show the board and pieces immediately, no backend call
    pauseBtn.disabled = true; // Initially disable pause button until game starts
}); 