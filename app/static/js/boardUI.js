import { 
    board, 
    updateStatus, 
    updateTurnIndicator, 
    getSessionId, 
    statusMessage,
    getBlackBot,
    getWhiteBot
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

// Get piece image URL for a piece
function getPieceImageUrl(piece) {
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
    return `static/images/pieces/${color}_${pieceNames[type]}.png`;
}

// Update the board display (click-to-move only)
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

    // Human is white if getWhiteBot() === 'You', black if getBlackBot() === 'You'
    const humanIsWhite = typeof getWhiteBot === 'function' && getWhiteBot() === 'You';
    const humanIsBlack = typeof getBlackBot === 'function' && getBlackBot() === 'You';
    let ranks, files;
    if (humanIsBlack) {
        ranks = [7, 6, 5, 4, 3, 2, 1, 0];
        files = [0, 1, 2, 3, 4, 5, 6, 7];
    } else {
        ranks = [0, 1, 2, 3, 4, 5, 6, 7];
        files = [7, 6, 5, 4, 3, 2, 1, 0];
    }
    const chessboard = document.getElementById('chessboard');
    chessboard.innerHTML = '';
    
    for (let visualRank = 0; visualRank < 8; visualRank++) {
        for (let visualFile = 0; visualFile < 8; visualFile++) {
            const rank = ranks[visualRank];
            const file = files[visualFile];
            const square = document.createElement('div');
            square.className = `square ${(visualRank + visualFile) % 2 === 0 ? 'white' : 'black'}`;
            square.dataset.row = rank;
            square.dataset.col = file;
            square.dataset.position = `${rank},${file}`;
            square.dataset.square = positionToAlgebraic([rank, file]);
            square.addEventListener('click', handleSquareClick);

            const piece = data.board[rank][file];
            if (piece) {
                const pieceImage = document.createElement('img');
                pieceImage.src = getPieceImageUrl({ color: piece[0] === piece[0].toUpperCase() ? 'w' : 'b', type: piece.toLowerCase() });
                pieceImage.className = 'piece-image';
                square.appendChild(pieceImage);
            }
            
            chessboard.appendChild(square);
        }
    }

    // Update game status and turn indicator
    statusMessage.textContent = data.status;
    updateTurnIndicator(data.turn);
}

// Initialize the board
function initializeBoard() {
    board.innerHTML = '';
    const humanIsBlack = typeof getBlackBot === 'function' && getBlackBot() === 'You';
    let ranks, files;
    if (humanIsBlack) {
        ranks = [7, 6, 5, 4, 3, 2, 1, 0];
        files = [0, 1, 2, 3, 4, 5, 6, 7];
    } else {
        ranks = [0, 1, 2, 3, 4, 5, 6, 7];
        files = [7, 6, 5, 4, 3, 2, 1, 0];
    }
    for (let visualRank = 0; visualRank < 8; visualRank++) {
        for (let visualFile = 0; visualFile < 8; visualFile++) {
            const rank = ranks[visualRank];
            const file = files[visualFile];
            const square = document.createElement('div');
            const isWhiteSquare = (visualRank + visualFile) % 2 === 0;
            square.className = `square ${isWhiteSquare ? 'white' : 'black'}`;
            const algebraic = `${String.fromCharCode(97 + file)}${rank + 1}`;
            square.dataset.square = algebraic;
            square.dataset.position = `${rank},${file}`;
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
    getPieceImageUrl,
    updateBoard,
    initializeBoard,
    highlightSquare,
    highlightValidMoves,
    clearHighlights
}; 