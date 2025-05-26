import { 
    getSessionId, 
    getWhiteBot, 
    getBlackBot, 
    isGameStarted, 
    statusMessage, 
    resignBtn, 
    newGameBtn, 
    startGameBtn, 
    gameNotStartedOverlay,
    getSelectedSquare,
    setSelectedSquare,
    updateStatus,
    setGameStarted
} from './gameState.js';
import { updateBoard, clearHighlights, highlightSquare, highlightValidMoves, lastMove } from './boardUI.js';
import { addMoveToHistory } from './moveHistory.js';
import { makeBotMove } from './botManager.js';

// Fetch current board state
async function fetchBoardState() {
    const response = await fetch(`/api/board?session_id=${getSessionId()}`);
    return await response.json();
}

// Handle square clicks
async function handleSquareClick(event) {
    if (!isGameStarted()) return;  // Prevent moves before game starts
    
    const square = event.target.closest('.square');
    if (!square) return;

    const position = square.dataset.position.split(',').map(Number);
    const currentState = await fetchBoardState();
    
    // If it's not the human's turn, don't allow moves
    if ((currentState.turn === 'white' && getWhiteBot() !== 'You') || (currentState.turn === 'black' && getBlackBot() !== 'You')) {
        return;
    }

    // Clear previous selections
    clearHighlights();

    if (getSelectedSquare()) {
        const fromPos = getSelectedSquare().dataset.position.split(',').map(Number);
        
        // Check if clicking a different piece of the same color
        const response = await fetch(`/api/valid-moves?session_id=${getSessionId()}&position=${position.join(',')}`);
        const data = await response.json();
        
        if (data.valid_moves && data.valid_moves.length > 0) {
            // If clicking a different piece of the same color, select that piece instead
            setSelectedSquare(square);
            highlightSquare(square);
            highlightValidMoves(data.valid_moves);
            return;
        }
        
        // Check if the destination is a valid move
        const validMovesResponse = await fetch(`/api/valid-moves?session_id=${getSessionId()}&position=${fromPos.join(',')}`);
        const validMovesData = await validMovesResponse.json();
        
        if (!validMovesData.valid_moves || !validMovesData.valid_moves.some(move => 
            move[0] === position[0] && move[1] === position[1])) {
            setSelectedSquare(null);
            return;
        }

        const moveResponse = await fetch('/api/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: getSessionId(),
                from: fromPos,
                to: position
            })
        });

        const result = await moveResponse.json();
        if (result.success) {
            // Set lastMove for animation
            lastMove.from = fromPos;
            lastMove.to = position;
            lastMove.piece = currentState.board[fromPos[0]][fromPos[1]];
            await updateBoard();
            updateStatus(result.status);
            addMoveToHistory(fromPos, position, currentState.turn);
            setSelectedSquare(null);
            
            // If it's now the bot's turn, make the bot move
            const newState = await fetchBoardState();
            if ((newState.turn === 'white' && getWhiteBot() !== 'You') || (newState.turn === 'black' && getBlackBot() !== 'You')) {
                await makeBotMove();
            }
        } else {
            // Display the error message to the user
            updateStatus(result.error || 'Invalid move');
            setSelectedSquare(null);
        }
    } else {
        const response = await fetch(`/api/valid-moves?session_id=${getSessionId()}&position=${position.join(',')}`);
        const data = await response.json();
        if (data.valid_moves && data.valid_moves.length > 0) {
            setSelectedSquare(square);
            highlightSquare(square);
            highlightValidMoves(data.valid_moves);
        }
    }
}

// Initialize event listeners
function initializeEventListeners() {
    // Handle resign button
    if (resignBtn) {
        resignBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to resign?')) {
                statusMessage.textContent = 'Game over - Resigned';
                // TODO: Add resign endpoint to backend
            }
        });
    }

    // Handle new game button
    if (newGameBtn) {
        newGameBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to start a new game?')) {
                window.location.href = '/';
            }
        });
    }

    // Handle start game button click
    if (startGameBtn && gameNotStartedOverlay) {
        startGameBtn.addEventListener('click', async () => {
            startGameBtn.style.display = 'none';
            gameNotStartedOverlay.style.display = 'none';  // Hide the overlay
            setGameStarted(true);
            
            // Make bot move if it's the bot's turn
            const currentState = await fetchBoardState();
            if ((currentState.turn === 'white' && getWhiteBot() !== 'You') || 
                (currentState.turn === 'black' && getBlackBot() !== 'You')) {
                console.log('Making initial bot move for', currentState.turn, 'bot');
                await makeBotMove();
            }
        });
    }

    // Add click event listener to each square
    document.querySelectorAll('.square').forEach(square => {
        square.addEventListener('click', handleSquareClick);
    });
}

export {
    fetchBoardState,
    handleSquareClick,
    initializeEventListeners
}; 