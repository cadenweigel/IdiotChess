// Game state management
let selectedSquare = null;
let validMoves = [];
let sessionId = null;
let whiteBot = null;
let blackBot = null;
let gameStarted = false;
let moveCount = 0;
let currentPlayerColor = null;  // Add this for drag and drop validation

// DOM Elements
let board = null;
let statusMessage = null;
let movesList = null;
let resignBtn = null;
let newGameBtn = null;
let startGameBtn = null;
let gameNotStartedOverlay = null;

// Initialize DOM elements
function initializeDOMElements() {
    board = document.getElementById('chessboard');
    statusMessage = document.getElementById('status-message');
    movesList = document.getElementById('moves-list');
    resignBtn = document.getElementById('resign-btn');
    newGameBtn = document.getElementById('new-game-btn');
    startGameBtn = document.getElementById('start-game-btn');
    gameNotStartedOverlay = document.getElementById('game-not-started-overlay');

    // Log any missing elements for debugging
    if (!board) console.debug('Chessboard element not found');
    if (!statusMessage) console.debug('Status message element not found');
    if (!movesList) console.debug('Moves list element not found');
    if (!resignBtn) console.debug('Resign button not found');
    if (!newGameBtn) console.debug('New game button not found');
    if (!startGameBtn) console.debug('Start game button not found');
    if (!gameNotStartedOverlay) console.debug('Game not started overlay not found');
}

// Update game status message
export function updateStatus(message) {
    if (statusMessage) {
        // Display "Game ongoing" when status is "active"
        statusMessage.textContent = message === "active" ? "Game ongoing" : message;
    }
}

// Update turn indicator
export function updateTurnIndicator(turn) {
    const whitePlayer = document.querySelector('.white-player');
    const blackPlayer = document.querySelector('.black-player');
    
    // Remove active class from both players
    whitePlayer.classList.remove('active');
    blackPlayer.classList.remove('active');
    
    // Add active class to current player
    if (turn === 'white') {
        whitePlayer.classList.add('active');
    } else {
        blackPlayer.classList.add('active');
    }
}

// Set session ID
export function setSessionId(id) {
    sessionId = id;
}

// Get session ID
export function getSessionId() {
    return sessionId;
}

// Set game started state
export function setGameStarted(started) {
    gameStarted = started;
}

// Get game started state
export function isGameStarted() {
    return gameStarted;
}

// Set bot colors
export function setBotColors(white, black) {
    whiteBot = white;
    blackBot = black;
}

// Get bot colors
export function getWhiteBot() {
    return whiteBot;
}

export function getBlackBot() {
    return blackBot;
}

// Set bot colors
export function setWhiteBot(bot) {
    whiteBot = bot;
}

export function setBlackBot(bot) {
    blackBot = bot;
}

// Getter functions
export function getSelectedSquare() {
    return selectedSquare;
}

// Setter functions
export function setSelectedSquare(square) {
    selectedSquare = square;
}

// Set current player color
export function setCurrentPlayerColor(color) {
    currentPlayerColor = color;
}

// Get current player color
export function getCurrentPlayerColor() {
    return currentPlayerColor;
}

// Export variables
export {
    selectedSquare,
    validMoves,
    moveCount,
    board,
    statusMessage,
    movesList,
    resignBtn,
    newGameBtn,
    startGameBtn,
    gameNotStartedOverlay,
    initializeDOMElements
}; 