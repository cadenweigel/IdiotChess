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
            tempImg.src = getPieceImageUrl(lastMove.piece);
            tempImg.className = 'piece-image moving';
            tempImg.style.position = 'absolute';
            tempImg.style.width = '70px';
            tempImg.style.height = '70px';
            tempImg.style.pointerEvents = 'none';
            tempImg.style.zIndex = '2000';
            tempImg.style.transition = 'none'; // Disable transition initially
            
            // Calculate positions based on square size and position
            const squareSize = boardElem.clientWidth / 8;  // Board is always square
            const humanIsBlack = typeof getBlackBot === 'function' && getBlackBot() === 'You';
            
            // Only flip the row coordinate for board orientation, keep column as is
            const fromRow = humanIsBlack ? 7 - lastMove.from[0] : lastMove.from[0];
            const fromCol = lastMove.from[1];  // Don't flip column
            const toRow = humanIsBlack ? 7 - lastMove.to[0] : lastMove.to[0];
            const toCol = lastMove.to[1];  // Don't flip column
            
            // Calculate center positions for the piece
            const pieceOffset = (squareSize - 70) / 2; // Center the 70px piece in the square
            
            // Set start position using square coordinates, centered in the square
            tempImg.style.left = `${fromCol * squareSize + pieceOffset}px`;
            tempImg.style.top = `${fromRow * squareSize + pieceOffset}px`;
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
            
            // Force a reflow to ensure the initial position is applied
            tempImg.offsetHeight;
            
            // Now enable the transition and animate to destination
            requestAnimationFrame(() => {
                tempImg.style.transition = 'all 0.3s ease-out';
                tempImg.style.left = `${toCol * squareSize + pieceOffset}px`;
                tempImg.style.top = `${toRow * squareSize + pieceOffset}px`;
                
                setTimeout(async () => {
                    // Update the board first while the animated piece is still visible
                    await doUpdateBoard(animatingMove);
                    // Then fade out the animated piece
                    tempImg.style.transition = 'opacity 0.1s';
                    tempImg.style.opacity = '0';
                    // Remove the animated piece after the fade completes
                    setTimeout(() => {
                        boardElem.removeChild(tempImg);
                        lastMove = {};
                    }, 100);  // Match the transition duration
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
    const whiteName = document.getElementById('white-name');
    const blackName = document.getElementById('black-name');
    
    if (!whiteCaptures || !blackCaptures || !whiteName || !blackName) {
        console.warn('Capture containers or player names not found:', { whiteCaptures, blackCaptures, whiteName, blackName });
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

    // Piece values for material calculation
    const pieceValues = {
        'pawn': 1,
        'knight': 3,
        'bishop': 3,
        'rook': 5,
        'queen': 9,
        'king': 0 // King is not counted
    };

    // Calculate material value of captured pieces
    function calcMaterial(capturedArr) {
        let total = 0;
        for (const symbol of capturedArr) {
            const info = symbolToType[symbol];
            if (info && pieceValues[info.type] !== undefined) {
                total += pieceValues[info.type];
            }
        }
        return total;
    }
    const whiteMaterial = calcMaterial(capturedByWhite); // White's captures (black pieces)
    const blackMaterial = calcMaterial(capturedByBlack); // Black's captures (white pieces)
    const diff = whiteMaterial - blackMaterial;

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

    // Show point advantage next to the leading player's name
    // Remove any previous advantage indicators
    whiteName.querySelector('.point-advantage')?.remove();
    blackName.querySelector('.point-advantage')?.remove();

    if (diff > 0) {
        // White is ahead
        const adv = document.createElement('span');
        adv.className = 'point-advantage';
        adv.textContent = ` +${diff}`;
        whiteName.appendChild(adv);
    } else if (diff < 0) {
        // Black is ahead
        const adv = document.createElement('span');
        adv.className = 'point-advantage';
        adv.textContent = ` +${-diff}`;
        blackName.appendChild(adv);
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

        // Update status and turn indicator using the proper functions
        if (data.status) {
            updateStatus(data.status);
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