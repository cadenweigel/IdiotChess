import { ensureSession } from './session.js';

const boardEl = document.getElementById("board");
const pieceBasePath = "/static/images/classic_pieces/";

const pieceImageMap = {
  'P': 'white_pawn.png', 'R': 'white_rook.png', 'N': 'white_knight.png',
  'B': 'white_bishop.png', 'Q': 'white_queen.png', 'K': 'white_king.png',
  'p': 'black_pawn.png', 'r': 'black_rook.png', 'n': 'black_knight.png',
  'b': 'black_bishop.png', 'q': 'black_queen.png', 'k': 'black_king.png',
};

export async function loadBoard() {
  const sessionId = await ensureSession();
  const response = await fetch(`/api/board?session_id=${sessionId}`);
  const data = await response.json();
  renderBoard(data.board);
}

function renderBoard(board) {
  boardEl.innerHTML = "";
  for (let row = 0; row < 8; row++) {
    for (let col = 0; col < 8; col++) {
      const square = document.createElement("div");
      square.classList.add("square", (row + col) % 2 === 0 ? "light" : "dark");

      const piece = board[row][col];
      if (piece) {
        const img = document.createElement("img");
        img.src = pieceBasePath + pieceImageMap[piece];
        img.alt = piece;
        square.appendChild(img);
      }

      square.dataset.row = row;
      square.dataset.col = col;
      boardEl.appendChild(square);
    }
  }
}
