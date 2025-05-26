import { movesList } from './gameState.js';
import { getBlackBot } from './gameState.js';

// Track move count internally
let moveCount = 1; // Start at 1

// Function to get moves list element
function getMovesListElement() {
    return document.getElementById('moves-list') || movesList;
}

// Function to scroll move history to bottom
function scrollMoveHistoryToBottom() {
    const movesList = getMovesListElement();
    if (!movesList) return;
    
    // Use setTimeout to ensure DOM updates are complete
    setTimeout(() => {
        movesList.scrollTop = movesList.scrollHeight;
    }, 50);
}

// Initialize move history from server data
async function initializeMoveHistory(sessionId) {
    try {
        const response = await fetch(`/api/board?session_id=${sessionId}`);
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.move_history) {
            // Clear existing move history
            clearMoveHistory();
            
            // Add each move from the history
            data.move_history.forEach(move => {
                addMoveToHistory(move.from, move.to, move.color);
            });
        }
    } catch (error) {
        console.error('Error initializing move history:', error);
        // Don't throw the error - allow the game to continue without move history
        // We can try to recover it later
    }
}

function flipCoordsIfHumanBlack([row, col]) {
    if (getBlackBot && getBlackBot() === 'You') {
        return [7 - row, 7 - col];
    }
    return [row, col];
}

function positionToAlgebraic(position) {
    const [rank, file] = position;
    const fileChar = String.fromCharCode(97 + file);
    const rankNum = 8 - rank;
    return `${fileChar}${rankNum}`;
}

// Add move to history
function addMoveToHistory(from, to, color) {
    const movesList = getMovesListElement();
    if (!movesList) {
        console.error('Moves list element not found');
        return;
    }

    const fromFlipped = flipCoordsIfHumanBlack(from);
    const toFlipped = flipCoordsIfHumanBlack(to);
    const fromElem = document.querySelector(`[data-position="${fromFlipped.join(',')}"]`);
    const toElem = document.querySelector(`[data-position="${toFlipped.join(',')}"]`);
    let fromSquare = '??';
    let toSquare = '??';
    if (fromElem && fromElem.dataset.square) {
        fromSquare = fromElem.dataset.square;
    } else {
        fromSquare = positionToAlgebraic(fromFlipped);
        console.warn('Move history: from square not found for', from, fromElem);
    }
    if (toElem && toElem.dataset.square) {
        toSquare = toElem.dataset.square;
    } else {
        toSquare = positionToAlgebraic(toFlipped);
        console.warn('Move history: to square not found for', to, toElem);
    }
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

        // White move (always create)
        const whiteMove = document.createElement('span');
        whiteMove.className = 'move-text white-move';
        moveContainer.appendChild(whiteMove);

        // Only create black move if this is a black move
        if (color === 'black') {
            const blackMove = document.createElement('span');
            blackMove.className = 'move-text black-move';
            moveContainer.appendChild(blackMove);
        }

        movesList.appendChild(moveContainer);
    } else {
        // If this is a black move and the black-move element doesn't exist yet, create it
        if (color === 'black' && !moveContainer.querySelector('.black-move')) {
            const blackMove = document.createElement('span');
            blackMove.className = 'move-text black-move';
            moveContainer.appendChild(blackMove);
        }
    }

    // Update the correct move
    const moveElement = moveContainer.querySelector(`.${color}-move`);
    if (moveElement) {
        moveElement.textContent = moveText;
        // Scroll after updating the move text
        scrollMoveHistoryToBottom();
    }

    // Only increment moveCount after black's move
    if (color === 'black') {
        moveCount++;
    }
}

// Clear move history
function clearMoveHistory() {
    const movesList = getMovesListElement();
    if (!movesList) {
        console.error('Moves list element not found');
        return;
    }
    movesList.innerHTML = '';
    moveCount = 1;
}

export {
    addMoveToHistory,
    clearMoveHistory,
    scrollMoveHistoryToBottom,
    initializeMoveHistory
}; 