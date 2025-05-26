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
    if (!piece) return null;
    
    // Handle the new piece format from the server
    const color = piece.color === 'white' ? 'white' : 'black';
    const type = piece.type.toLowerCase();  // Get full piece type name
    const pieceNames = {
        'pawn': 'pawn',
        'knight': 'knight',
        'bishop': 'bishop',
        'rook': 'rook',
        'queen': 'queen',
        'king': 'king'
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
            // Use the new piece format
            const pieceColor = lastMove.piece.color === 'white' ? 'white' : 'black';
            const pieceType = lastMove.piece.type.toLowerCase()[0];
            tempImg.src = `static/images/pieces/${pieceColor}_${getPieceNameFromType(pieceType)}.png`;
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
            const animatingMove = { 
                from: [...lastMove.from], 
                to: [...lastMove.to], 
                piece: {...lastMove.piece}  // Deep copy the piece object
            };
            
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

// Helper function to get piece name from type
function getPieceNameFromType(type) {
    const pieceNames = {
        'pawn': 'pawn',
        'knight': 'knight',
        'bishop': 'bishop',
        'rook': 'rook',
        'queen': 'queen',
        'king': 'king'
    };
    return pieceNames[type.toLowerCase()] || 'pawn';
}

// Update captured pieces display
function updateCapturedPieces(capturedByWhite, capturedByBlack) {
    console.log('Updating captured pieces:', { capturedByWhite, capturedByBlack });
    const whiteCaptures = document.getElementById('white-captures');
    const blackCaptures = document.getElementById('black-captures');
    
    if (!whiteCaptures || !blackCaptures) {
        console.warn('Capture containers not found:', { whiteCaptures, blackCaptures });
        return;
    }

    // Clear existing captures
    whiteCaptures.innerHTML = '';
    blackCaptures.innerHTML = '';

    // Map Unicode symbols to piece types
    const symbolToType = {
        '♙': { type: 'pawn', color: 'white' },
        '♖': { type: 'rook', color: 'white' },
        '♘': { type: 'knight', color: 'white' },
        '♗': { type: 'bishop', color: 'white' },
        '♕': { type: 'queen', color: 'white' },
        '♔': { type: 'king', color: 'white' },
        '♟': { type: 'pawn', color: 'black' },
        '♜': { type: 'rook', color: 'black' },
        '♞': { type: 'knight', color: 'black' },
        '♝': { type: 'bishop', color: 'black' },
        '♛': { type: 'queen', color: 'black' },
        '♚': { type: 'king', color: 'black' }
    };

    // Add captured pieces
    if (Array.isArray(capturedByWhite)) {
        capturedByWhite.forEach(symbol => {
            const pieceInfo = symbolToType[symbol];
            if (pieceInfo) {
                const img = document.createElement('img');
                img.src = `static/images/pieces/${pieceInfo.color}_${pieceInfo.type}.png`;
                img.className = 'captured-piece';
                img.alt = `${pieceInfo.color} ${pieceInfo.type}`;
                whiteCaptures.appendChild(img);
            }
        });
    }

    if (Array.isArray(capturedByBlack)) {
        capturedByBlack.forEach(symbol => {
            const pieceInfo = symbolToType[symbol];
            if (pieceInfo) {
                const img = document.createElement('img');
                img.src = `static/images/pieces/${pieceInfo.color}_${pieceInfo.type}.png`;
                img.className = 'captured-piece';
                img.alt = `${pieceInfo.color} ${pieceInfo.type}`;
                blackCaptures.appendChild(img);
            }
        });
    }
}

// Initialize the board
async function initializeBoard() {
    try {
        const response = await fetch(`/api/board?session_id=${getSessionId()}`);
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        const chessboard = document.getElementById('chessboard');
        if (!chessboard) {
            throw new Error('Chessboard element not found');
        }

        // Clear existing board
        chessboard.innerHTML = '';

        // Create squares with proper coloring
        const humanIsBlack = typeof getBlackBot === 'function' && getBlackBot() === 'You';
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('div');
                // Determine if this square should be light or dark
                const isLightSquare = (row + col) % 2 === 0;
                square.className = `square ${isLightSquare ? 'light' : 'dark'}`;
                
                // Set position data attributes
                const actualRow = humanIsBlack ? 7 - row : row;
                const actualCol = humanIsBlack ? col : col;
                square.dataset.position = `${actualRow},${actualCol}`;
                square.dataset.square = positionToAlgebraic([actualRow, actualCol]);
                
                // Add click handler
                square.addEventListener('click', handleSquareClick);
                
                chessboard.appendChild(square);
            }
        }

        // Update the board with initial position
        await updateBoard();
    } catch (error) {
        console.error('Error initializing board:', error);
        // Show a user-friendly error message
        const board = document.getElementById('chessboard');
        if (board) {
            board.innerHTML = '<div class="error-message">Error loading the game board. Please try refreshing the page.</div>';
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

// The actual board update logic, separated from animation
async function doUpdateBoard(animatingMove = null) {
    const currentSessionId = getSessionId();
    if (!currentSessionId) {
        console.log('Waiting for session ID...');
        return;
    }
    
    try {
        const response = await fetch(`/api/board?session_id=${currentSessionId}`);
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        if (data.error) {
            console.error(data.error);
            return;
        }

        console.log('Board state received:', data);

        // Update captured pieces if available
        if (data.captured_by_white || data.captured_by_black) {
            updateCapturedPieces(data.captured_by_white || [], data.captured_by_black || []);
        }

        const humanIsBlack = typeof getBlackBot === 'function' && getBlackBot() === 'You';
        
        // Update pieces on the board
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const actualRow = humanIsBlack ? 7 - row : row;
                const actualCol = humanIsBlack ? col : col;
                const position = `${actualRow},${actualCol}`;
                const square = document.querySelector(`[data-position="${position}"]`);
                
                if (!square) {
                    console.error(`Square not found for position ${position}`);
                    continue;
                }

                // Clear existing pieces
                square.innerHTML = '';
                
                // Add piece if one exists at this position
                const piece = data.board[actualRow][actualCol];
                if (piece) {
                    // Skip the piece during animation if it's the moving piece
                    const moveToCheck = animatingMove || lastMove;
                    if (
                        moveToCheck &&
                        moveToCheck.from &&
                        moveToCheck.piece &&
                        moveToCheck.from[0] === actualRow &&
                        moveToCheck.from[1] === actualCol &&
                        moveToCheck.piece.type === piece.type &&
                        moveToCheck.piece.color === piece.color
                    ) {
                        continue;
                    }

                    const pieceImageUrl = getPieceImageUrl(piece);
                    if (pieceImageUrl) {
                        const pieceImage = document.createElement('img');
                        pieceImage.src = pieceImageUrl;
                        pieceImage.className = 'piece-image';
                        square.appendChild(pieceImage);
                    }
                }
            }
        }

        // Update status and turn indicator
        const statusMessageElem = document.getElementById('status-message');
        if (statusMessageElem && data.status) {
            statusMessageElem.textContent = data.status;
        }
        
        if (data.turn) {
            updateTurnIndicator(data.turn);
        }
    } catch (error) {
        console.error('Error updating board:', error);
    }
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