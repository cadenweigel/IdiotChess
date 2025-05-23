import { 
    getSessionId, 
    getWhiteBot, 
    getBlackBot, 
    updateStatus 
} from './gameState.js';
import { updateBoard, lastMove } from './boardUI.js';
import { addMoveToHistory } from './moveHistory.js';
import { fetchBoardState } from './eventHandlers.js';

// Make a bot move
async function makeBotMove() {
    const sessionId = getSessionId();
    if (!sessionId) {
        console.error('No session ID available for bot move');
        return;
    }

    try {
        // Get current board state to determine whose turn it is
        const response = await fetch(`/api/board?session_id=${sessionId}`);
        const data = await response.json();
        
        // Determine which bot should move based on current turn and bot configuration
        const currentTurn = data.turn;
        const whiteBot = getWhiteBot();
        const blackBot = getBlackBot();
        const isWhiteBot = whiteBot !== 'You';
        const isBlackBot = blackBot !== 'You';
        
        console.log('Current turn:', currentTurn);
        console.log('Bot configuration:', { whiteBot, blackBot });
        
        // Only make a bot move if it's the bot's turn
        if ((currentTurn === 'white' && !isWhiteBot) || (currentTurn === 'black' && !isBlackBot)) {
            console.log('Not bot turn, skipping bot move');
            return;
        }
        
        console.log('Making bot move for color:', currentTurn);
        
        // Make the bot move request
        const moveResponse = await fetch('/api/bot-move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                bot_color: currentTurn
            })
        });

        if (!moveResponse.ok) {
            const errorData = await moveResponse.json();
            throw new Error(`Bot move failed: ${moveResponse.status} ${JSON.stringify(errorData)}`);
        }

        const moveData = await moveResponse.json();
        if (moveData.success) {
            // Set lastMove for animation if move data is available
            if (moveData.move && moveData.move.from && moveData.move.to && moveData.move.piece) {
                lastMove.from = moveData.move.from;
                lastMove.to = moveData.move.to;
                lastMove.piece = moveData.move.piece;
            }
            // Update the board with the new state
            await updateBoard();
            updateStatus(moveData.status);
            
            // Add the move to history if we have valid move data
            if (moveData.move && moveData.move.from && moveData.move.to) {
                addMoveToHistory(
                    moveData.move.from,
                    moveData.move.to,
                    currentTurn
                );
            }
        }
    } catch (error) {
        console.error('Bot move failed:', error);
        updateStatus('Error making bot move');
    }
}

// Load bot avatars
function loadBotAvatars() {
    const whiteAvatar = document.getElementById('white-avatar');
    const blackAvatar = document.getElementById('black-avatar');
    const whiteName = document.getElementById('white-name');
    const blackName = document.getElementById('black-name');

    if (!whiteAvatar || !blackAvatar || !whiteName || !blackName) {
        console.error('Required DOM elements not found');
        return;
    }

    // Always get the latest bot/player names from gameState
    const whiteBotName = getWhiteBot() || 'You';
    const blackBotName = getBlackBot() || 'You';

    // Handle avatar loading
    if (whiteBotName === 'You') {
        whiteAvatar.src = '/static/images/avatars/default_player.png';
    } else if (whiteBotName === 'Pongo') {
        whiteAvatar.src = '/static/images/avatars/pongo.png';
    } else {
        whiteAvatar.src = `/static/images/avatars/${whiteBotName.toLowerCase()}.png`;
    }
    whiteName.textContent = whiteBotName;

    if (blackBotName === 'You') {
        blackAvatar.src = '/static/images/avatars/default_player.png';
    } else if (blackBotName === 'Pongo') {
        blackAvatar.src = '/static/images/avatars/pongo.png';
    } else {
        blackAvatar.src = `/static/images/avatars/${blackBotName.toLowerCase()}.png`;
    }
    blackName.textContent = blackBotName;
}

export {
    makeBotMove,
    loadBotAvatars
}; 