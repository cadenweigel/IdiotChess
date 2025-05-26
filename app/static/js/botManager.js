import { 
    getSessionId, 
    getWhiteBot, 
    getBlackBot, 
    updateStatus 
} from './gameState.js';
import { updateBoard, lastMove } from './boardUI.js';
import { addMoveToHistory } from './moveHistory.js';
import { fetchBoardState } from './eventHandlers.js';

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
            // Get the piece that was moved
            const fromSquare = data.move.from;
            const piece = currentState.board[fromSquare[0]][fromSquare[1]];
            
            // Update lastMove properties instead of reassigning
            lastMove.from = data.move.from;
            lastMove.to = data.move.to;
            lastMove.piece = {
                type: piece.type,
                color: piece.color,
                symbol: piece.symbol
            };
            
            await updateBoard();
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
        console.error('Bot move failed:', error);
        updateStatus('Error making bot move. Please try again.');
        
        // Try to recover by updating the board state
        try {
            await updateBoard();
        } catch (e) {
            console.error('Failed to recover board state:', e);
        }
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