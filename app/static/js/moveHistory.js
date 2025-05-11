import { movesList } from './gameState.js';

// Track move count internally
let moveCount = 1; // Start at 1

// Function to scroll move history to bottom
function scrollMoveHistoryToBottom() {
    // Use setTimeout to ensure DOM updates are complete
    setTimeout(() => {
        movesList.scrollTop = movesList.scrollHeight;
    }, 50);
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
    movesList.innerHTML = '';
    moveCount = 1;
}

export {
    addMoveToHistory,
    clearMoveHistory,
    scrollMoveHistoryToBottom
}; 