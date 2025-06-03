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

// Bot type to display name mapping
const BOT_DISPLAY_NAMES = {
    'white_idiot': 'Wyatt',
    'black_idiot': 'Moose',
    'pongo': 'Pongo',
    'borzoi': 'Borzoi',
    'barrowofmonkeys': 'Barrow of Monkeys',
    'gigantopithecus': 'Gigantopithecus'
};

// Bot type to avatar filename mapping
const BOT_AVATAR_FILES = {
    'white_idiot': 'wyatt',
    'black_idiot': 'moose',
    'pongo': 'pongo',
    'borzoi': 'borzoi',
    'barrowofmonkeys': 'barrowofmonkeys',
    'gigantopithecus': 'gigantopithecus'
};

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

    // Get the latest game state
    fetch(`/api/board?session_id=${getSessionId()}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error fetching game state:', data.error);
                return;
            }

            const whiteBotType = getWhiteBot();
            const blackBotType = getBlackBot();

            // Use player names from game state
            const whitePlayerName = data.white_player_name;
            const blackPlayerName = data.black_player_name;

            // Handle avatar loading
            if (whiteBotType === 'You') {
                whiteAvatar.src = '/static/images/avatars/default_player.png';
                whiteName.textContent = whitePlayerName === 'default' ? 'You' : whitePlayerName;
            } else {
                const whiteAvatarFile = BOT_AVATAR_FILES[whiteBotType] || whiteBotType.toLowerCase().replace(/\s+/g, '');
                whiteAvatar.src = `/static/images/avatars/${whiteAvatarFile}.png`;
                whiteName.textContent = BOT_DISPLAY_NAMES[whiteBotType] || whiteBotType;
            }

            if (blackBotType === 'You') {
                blackAvatar.src = '/static/images/avatars/default_player.png';
                blackName.textContent = blackPlayerName === 'default' ? 'You' : blackPlayerName;
            } else {
                const blackAvatarFile = BOT_AVATAR_FILES[blackBotType] || blackBotType.toLowerCase().replace(/\s+/g, '');
                blackAvatar.src = `/static/images/avatars/${blackAvatarFile}.png`;
                blackName.textContent = BOT_DISPLAY_NAMES[blackBotType] || blackBotType;
            }
        })
        .catch(error => {
            console.error('Error loading bot avatars:', error);
        });
}

export {
    makeBotMove,
    loadBotAvatars
}; 