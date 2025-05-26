import { initializeBoard, updateBoard as updateBoardDisplay } from './boardUI.js';
import { loadBotAvatars } from './botManager.js';
import { clearMoveHistory, initializeMoveHistory } from './moveHistory.js';
import { fetchBoardState, initializeEventListeners } from './eventHandlers.js';
import { 
    initializeDOMElements, 
    updateTurnIndicator, 
    setSessionId, 
    setGameStarted,
    setBotColors,
    getSessionId,
    getWhiteBot,
    getBlackBot,
    setWhiteBot,
    setBlackBot,
    setCurrentPlayerColor
} from './gameState.js';

// Game state
let selectedSquare = null;
let validMoves = [];
let sessionId = null;
let whiteBot = null;
let blackBot = null;
let gameStarted = false;
let moveCount = 1;  // Start at 1

// DOM Elements
const board = document.getElementById('chessboard');
const statusMessage = document.getElementById('status-message');
const movesList = document.getElementById('moves-list');
const resignBtn = document.getElementById('resign-btn');
const newGameBtn = document.getElementById('new-game-btn');
const startGameBtn = document.getElementById('start-game-btn');
const gameNotStartedOverlay = document.getElementById('game-not-started-overlay');

// Function to scroll move history to bottom
function scrollMoveHistoryToBottom() {
    // Use setTimeout to ensure DOM updates are complete
    setTimeout(() => {
        movesList.scrollTop = movesList.scrollHeight;
    }, 50);
}

// Set up MutationObserver to handle move history scrolling
const moveHistoryObserver = new MutationObserver(() => {
    movesList.scrollTop = movesList.scrollHeight;
});

// Start observing the moves list for changes
moveHistoryObserver.observe(movesList, { 
    childList: true,
    subtree: true,
    characterData: true
});

// Update game status message
function updateStatus(message) {
    if (statusMessage) {
        statusMessage.textContent = message;
    }

    // Check for game over conditions
    if (message.includes('checkmate') || message.includes('stalemate') || message.includes('draw')) {
        showGameOver(message);
    }
}

// Show game over overlay
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
}

// Convert algebraic notation to backend position
function algebraicToPosition(square) {
    const file = square.charCodeAt(0) - 97; // 'a' -> 0, 'b' -> 1, etc.
    const rank = 8 - parseInt(square[1]); // '1' -> 7, '2' -> 6, etc.
    return [rank, file];
}

// Convert backend position to algebraic notation
function positionToAlgebraic(position) {
    const [rank, file] = position;
    const fileChar = String.fromCharCode(97 + file);
    const rankNum = 8 - rank;
    return `${fileChar}${rankNum}`;
}

// Get piece image for a piece
function getPieceImage(piece) {
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
    return `<img src="static/images/pieces/${color}_${pieceNames[type]}.png" alt="${color} ${type}" class="piece-image">`;
}

// Handle square clicks
async function handleSquareClick(event) {
    if (!gameStarted) return;  // Prevent moves before game starts
    
    const square = event.target.closest('.square');
    if (!square) return;

    const position = square.dataset.position.split(',').map(Number);
    const currentState = await fetchBoardState();
    
    // If it's not the human's turn, don't allow moves
    if ((currentState.turn === 'white' && whiteBot !== 'You') || (currentState.turn === 'black' && blackBot !== 'You')) {
        return;
    }

    // Clear previous selections
    clearHighlights();

    if (selectedSquare) {
        const fromPos = selectedSquare.dataset.position.split(',').map(Number);
        const response = await fetch('/api/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                from: fromPos,
                to: position
            })
        });

        const result = await response.json();
        if (result.success) {
            await updateBoardDisplay();
            updateStatus(result.status);
            addMoveToHistory(fromPos, position, currentState.turn);
            selectedSquare = null;
            
            // If it's now the bot's turn, make the bot move
            const newState = await fetchBoardState();
            if ((newState.turn === 'white' && whiteBot !== 'You') || (newState.turn === 'black' && blackBot !== 'You')) {
                await makeBotMove();
            }
        }
    } else {
        const response = await fetch(`/api/valid-moves?session_id=${sessionId}&position=${position.join(',')}`);
        const data = await response.json();
        if (data.valid_moves && data.valid_moves.length > 0) {
            selectedSquare = square;
            highlightSquare(square);
            highlightValidMoves(data.valid_moves);
        }
    }
}

// Make bot move
async function makeBotMove() {
    try {
        // First check if it's actually a bot's turn
        const currentState = await fetchBoardState();
        const isBotTurn = (currentState.turn === 'white' && getWhiteBot() !== 'You') || 
                         (currentState.turn === 'black' && getBlackBot() !== 'You');
        
        if (!isBotTurn) {
            console.log('Not bot turn, skipping bot move');
            return;
        }

        const currentSessionId = getSessionId();
        if (!currentSessionId) {
            console.error('No session ID available for bot move');
            return;
        }

        console.log('Making bot move for session:', currentSessionId, 'turn:', currentState.turn);
        console.log('Bot configuration:', { whiteBot: getWhiteBot(), blackBot: getBlackBot() });

        const response = await fetch('/api/bot-move', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ 
                session_id: currentSessionId,
                bot_color: currentState.turn
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Bot move failed:', response.status, errorData);
            updateStatus('Error making bot move. Please try again.');
            return;
        }

        const data = await response.json();
        console.log('Bot move response:', data);

        if (data.success) {
            await updateBoardDisplay();
            updateStatus(data.status);
            
            // Only add to move history if we have valid move data
            if (data.move && data.move.from && data.move.to) {
                addMoveToHistory(
                    data.move.from,
                    data.move.to,
                    currentState.turn
                );
            }
            
            // Check if it's still a bot's turn after the move
            const newState = await fetchBoardState();
            const isStillBotTurn = (newState.turn === 'white' && getWhiteBot() !== 'You') || 
                                 (newState.turn === 'black' && getBlackBot() !== 'You');
            
            if (isStillBotTurn) {
                await makeBotMove();
            }
        } else {
            console.error('Bot move failed:', data.error);
            updateStatus('Error: ' + (data.error || 'Failed to make bot move'));
        }
    } catch (error) {
        console.error('Error making bot move:', error);
        updateStatus('Error making bot move. Please try again.');
        
        // Try to recover by updating the board state
        try {
            await updateBoardDisplay();
        } catch (e) {
            console.error('Failed to recover board state:', e);
        }
    }
}

// Highlight a square
function highlightSquare(square) {
    square.classList.add('selected');
}

// Highlight valid moves
function highlightValidMoves(moves) {
    moves.forEach(move => {
        const [row, col] = move;
        const square = document.querySelector(`[data-position="${row},${col}"]`);
        if (square) {
            square.classList.add('valid-move');
        }
    });
}

// Clear all highlights
function clearHighlights() {
    document.querySelectorAll('.square').forEach(square => {
        square.classList.remove('selected', 'valid-move');
    });
}

// Add move to history
function addMoveToHistory(from, to, color) {
    const fromSquare = document.querySelector(`[data-position="${from.join(',')}"]`).dataset.square;
    const toSquare = document.querySelector(`[data-position="${to.join(',')}"]`).dataset.square;
    const moveText = `${fromSquare}${toSquare}`;

    // Find or create the move container for this move number
    let moveContainer = document.querySelector(`.move-container[data-move="${moveCount}"]`);
    if (!moveContainer) {
        moveContainer = document.createElement('div');
        moveContainer.className = 'move-container';
        moveContainer.dataset.move = moveCount;

        // Move number
        const moveNumber = document.createElement('span');
        moveNumber.className = 'move-number';
        moveNumber.textContent = `${moveCount}.`;
        moveContainer.appendChild(moveNumber);

        // White move
        const whiteMove = document.createElement('span');
        whiteMove.className = 'move-text white-move';
        moveContainer.appendChild(whiteMove);

        // Black move
        const blackMove = document.createElement('span');
        blackMove.className = 'move-text black-move';
        moveContainer.appendChild(blackMove);

        movesList.appendChild(moveContainer);
    }

    // Update the correct move
    const moveElement = moveContainer.querySelector(`.${color}-move`);
    if (moveElement) {
        moveElement.textContent = moveText;
    }

    // Only increment moveCount after black's move
    if (color === 'black') {
        moveCount++;
    }

    // Scroll to the bottom
    movesList.scrollTop = movesList.scrollHeight;
}

// Handle resign button
resignBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to resign?')) {
        statusMessage.textContent = 'Game over - Resigned';
        // TODO: Add resign endpoint to backend
    }
});

// Handle new game button
newGameBtn.addEventListener('click', async () => {
    // Reset the game state
    selectedSquare = null;
    clearHighlights();
    
    // Redirect to the home page
    window.location.href = '/';
});

// Handle start game button click
startGameBtn.addEventListener('click', async () => {
    startGameBtn.style.display = 'none';
    gameNotStartedOverlay.style.display = 'none';  // Hide the overlay
    gameStarted = true;
    
    // Make bot move if it's the bot's turn
    const currentState = await fetchBoardState();
    if ((currentState.turn === 'white' && whiteBot !== 'You') || 
        (currentState.turn === 'black' && blackBot !== 'You')) {
        console.log('Making initial bot move for', currentState.turn, 'bot');
        await makeBotMove();
    }
});

function positionHumanPlayerAtBottom() {
    const whitePlayerDiv = document.querySelector('.white-player');
    const blackPlayerDiv = document.querySelector('.black-player');
    if (!whitePlayerDiv || !blackPlayerDiv) return;
    if (getWhiteBot() === 'You') {
        whitePlayerDiv.style.order = 2;
        blackPlayerDiv.style.order = 1;
    } else {
        whitePlayerDiv.style.order = 1;
        blackPlayerDiv.style.order = 2;
    }
}

function moveHumanPlayerInfoToBottom() {
    const whitePlayerDiv = document.querySelector('.white-player');
    const blackPlayerDiv = document.querySelector('.black-player');
    if (!whitePlayerDiv || !blackPlayerDiv) return;
    const parent = whitePlayerDiv.parentElement;
    if (!parent) return;
    if (getWhiteBot() === 'You') {
        parent.appendChild(whitePlayerDiv);
    } else {
        parent.appendChild(blackPlayerDiv);
    }
}

// Initialize game
async function initializeGame() {
    // Get session ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    const botColor = urlParams.get('bot_color');
    const botType = urlParams.get('bot_type');

    if (!sessionId) {
        console.error('No session ID provided');
        return;
    }

    // Initialize game state
    setSessionId(sessionId);
    
    // Set up bot colors based on the URL parameters
    if (botColor && botType) {
        // If bot is white, human is black, and vice versa
        if (botColor === 'white') {
            setWhiteBot(botType);
            setBlackBot('You');
        } else {
            setWhiteBot('You');
            setBlackBot(botType);
        }
        setBotColors(botColor === 'white' ? botType : 'You', botColor === 'black' ? botType : 'You');
    }
    
    // Initialize move history from server
    await initializeMoveHistory(sessionId);
    
    // Set up the game board
    await initializeBoard();
    
    // Initialize other game components
    initializeDOMElements();
    initializeEventListeners();
    loadBotAvatars();
    
    // Position the human player at the bottom
    positionHumanPlayerAtBottom();
}

// Initialize the game when the page loads
window.addEventListener('load', initializeGame);