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

let lastMove = {};

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

    // If there is a move to animate, do the animation first, then update the board
    if (lastMove && lastMove.from && lastMove.to && lastMove.piece) {
        const boardElem = document.getElementById('chessboard');
        const boardRect = boardElem.getBoundingClientRect();
        const fromSquare = document.querySelector(`[data-position='${lastMove.from[0]},${lastMove.from[1]}']`);
        const toSquare = document.querySelector(`[data-position='${lastMove.to[0]},${lastMove.to[1]}']`);
        if (fromSquare && toSquare) {
            // Create a temporary image for the animation
            const tempImg = document.createElement('img');
            tempImg.src = getPieceImageUrl({ color: lastMove.piece[0] === lastMove.piece[0].toUpperCase() ? 'w' : 'b', type: lastMove.piece.toLowerCase() });
            tempImg.className = 'piece-image moving';
            tempImg.style.position = 'absolute';
            tempImg.style.width = '70px';
            tempImg.style.height = '70px';
            tempImg.style.pointerEvents = 'none';
            tempImg.style.zIndex = '2000';
            // Set start position
            const fromRect = fromSquare.getBoundingClientRect();
            const toRect = toSquare.getBoundingClientRect();
            tempImg.style.left = `${fromRect.left - boardRect.left}px`;
            tempImg.style.top = `${fromRect.top - boardRect.top}px`;
            boardElem.appendChild(tempImg);
            // Hide the piece in the from-square immediately
            const fromPieceImg = fromSquare.querySelector('img.piece-image');
            if (fromPieceImg) {
                fromPieceImg.style.visibility = 'hidden';
            }
            // Make a copy of lastMove for the update after animation
            const animatingMove = { from: [...lastMove.from], to: [...lastMove.to], piece: lastMove.piece };
            // Animate to destination
            requestAnimationFrame(() => {
                tempImg.style.left = `${toRect.left - boardRect.left}px`;
                tempImg.style.top = `${toRect.top - boardRect.top}px`;
                setTimeout(async () => {
                    boardElem.removeChild(tempImg);
                    lastMove = {};
                    // Now update the board for the new state, passing animatingMove
                    await doUpdateBoard(animatingMove);
                }, 300);
            });
            return; // Don't update the board yet, wait for animation
        } else {
            // If squares not found, just update the board
            lastMove = {};
        }
    }
    await doUpdateBoard();
}

// The actual board update logic, separated from animation
async function doUpdateBoard(animatingMove = null) {
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
    for (let visualRank = 0; visualRank < 8; visualRank++) {
        for (let visualFile = 0; visualFile < 8; visualFile++) {
            const rank = ranks[visualRank];
            const file = files[visualFile];
            const position = `${rank},${file}`;
            const square = document.querySelector(`[data-position="${position}"]`);
            if (!square) {
                const newSquare = document.createElement('div');
                newSquare.className = `square ${(visualRank + visualFile) % 2 === 0 ? 'white' : 'black'}`;
                newSquare.dataset.row = rank;
                newSquare.dataset.col = file;
                newSquare.dataset.position = position;
                newSquare.dataset.square = positionToAlgebraic([rank, file]);
                newSquare.addEventListener('click', handleSquareClick);
                chessboard.appendChild(newSquare);
            }
            square.innerHTML = '';
            const piece = data.board[rank][file];
            if (piece) {
                // Hide the piece in the from-square during animation
                const moveToCheck = animatingMove || lastMove;
                if (
                    moveToCheck &&
                    moveToCheck.from &&
                    moveToCheck.piece &&
                    moveToCheck.from[0] === rank &&
                    moveToCheck.from[1] === file &&
                    moveToCheck.piece === piece
                ) {
                    // Don't render the piece in the from-square during animation
                } else {
                    const pieceImage = document.createElement('img');
                    pieceImage.src = getPieceImageUrl({ color: piece[0] === piece[0].toUpperCase() ? 'w' : 'b', type: piece.toLowerCase() });
                    pieceImage.className = 'piece-image';
                    square.appendChild(pieceImage);
                }
            }
        }
    }
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
    clearHighlights,
    lastMove
}; 