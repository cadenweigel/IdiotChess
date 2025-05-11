import { 
    board, 
    updateStatus, 
    updateTurnIndicator, 
    getSessionId, 
    statusMessage,
    getBlackBot
} from './gameState.js';
import { handleSquareClick } from './eventHandlers.js';

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

// Update the board display
async function updateBoard() {
    const currentSessionId = getSessionId();
    if (!currentSessionId) {
        console.log('Waiting for session ID...');
        return;
    }

    const response = await fetch(`/api/board?session_id=${currentSessionId}`);
    const data = await response.json();
    
    if (data.error) {
        console.error(data.error);
        return;
    }

    const isBlackPlayer = getBlackBot() === 'You';
    
    // Update board state
    for (let rank = 0; rank < 8; rank++) {
        for (let file = 0; file < 8; file++) {
            // Convert backend position to frontend position
            const frontendRank = isBlackPlayer ? rank : 7 - rank;
            const frontendFile = isBlackPlayer ? 7 - file : file;
            const square = document.querySelector(`[data-position="${rank},${file}"]`);
            const piece = data.board[rank][file];
            square.innerHTML = piece ? getPieceImage({ color: piece[0] === piece[0].toUpperCase() ? 'w' : 'b', type: piece.toLowerCase() }) : '';
        }
    }

    // Update game status and turn indicator
    statusMessage.textContent = data.status;
    updateTurnIndicator(data.turn);
}

// Initialize the board
function initializeBoard() {
    board.innerHTML = '';
    const isBlackPlayer = getBlackBot() === 'You';
    
    // If playing as black, we'll create the board in reverse order
    const ranks = isBlackPlayer ? [0, 1, 2, 3, 4, 5, 6, 7] : [7, 6, 5, 4, 3, 2, 1, 0];
    const files = isBlackPlayer ? [7, 6, 5, 4, 3, 2, 1, 0] : [0, 1, 2, 3, 4, 5, 6, 7];
    
    for (let visualRank = 0; visualRank < 8; visualRank++) {
        for (let visualFile = 0; visualFile < 8; visualFile++) {
            const rank = ranks[visualRank];
            const file = files[visualFile];
            const square = document.createElement('div');
            // Standard chessboard coloring: (visualRank + visualFile) % 2 === 0 is white
            const isWhiteSquare = (visualRank + visualFile) % 2 === 0;
            square.className = `square ${isWhiteSquare ? 'white' : 'black'}`;
            const algebraic = `${String.fromCharCode(97 + file)}${rank + 1}`;
            square.dataset.square = algebraic;
            // Store backend position format (row, col) where row is 0-7 from top to bottom
            square.dataset.position = `${7-rank},${file}`;
            square.addEventListener('click', handleSquareClick);
            board.appendChild(square);
        }
    }
    
    // Wait for session ID to be set before updating board
    const checkSessionId = setInterval(() => {
        const currentSessionId = getSessionId();
        if (currentSessionId) {
            clearInterval(checkSessionId);
            updateBoard();
        }
    }, 100);
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

export {
    algebraicToPosition,
    positionToAlgebraic,
    getPieceImage,
    updateBoard,
    initializeBoard,
    highlightSquare,
    highlightValidMoves,
    clearHighlights
}; 