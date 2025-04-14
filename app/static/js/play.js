const boardEl = document.getElementById("board");
const pieceBasePath = "/static/images/classic_pieces/";

const pieceImageMap = {
  'P': 'white_pawn.png',
  'R': 'white_rook.png',
  'N': 'white_knight.png',
  'B': 'white_bishop.png',
  'Q': 'white_queen.png',
  'K': 'white_king.png',
  'p': 'black_pawn.png',
  'r': 'black_rook.png',
  'n': 'black_knight.png',
  'b': 'black_bishop.png',
  'q': 'black_queen.png',
  'k': 'black_king.png',
};

// Load board state from backend
async function loadBoard() {
  const response = await fetch("/api/board");
  const data = await response.json();
  renderBoard(data.board);
}

// Render the 8x8 board
function renderBoard(board) {
  boardEl.innerHTML = ""; // Clear previous board
  for (let row = 0; row < 8; row++) {
    for (let col = 0; col < 8; col++) {
      const square = document.createElement("div");
      square.classList.add("square");

      // Add light/dark class
      if ((row + col) % 2 === 0) {
        square.classList.add("light");
      } else {
        square.classList.add("dark");
      }

      const piece = board[row][col];
      if (piece) {
        const img = document.createElement("img");
        const filename = pieceImageMap[piece];
        img.src = pieceBasePath + filename;
        img.alt = piece;
        square.appendChild(img);
      }

      square.dataset.row = row;
      square.dataset.col = col;
      boardEl.appendChild(square);
    }
  }
}

function setBoardTheme(theme) {
  // Remove all known theme classes
  const themes = ['classic', 'blue', 'green', 'gray'];
  themes.forEach(t => boardEl.classList.remove(t));

  // Add the selected theme
  boardEl.classList.add(theme);
}

document.addEventListener("DOMContentLoaded", () => {
  const currentThemeBtn = document.getElementById("currentTheme");
  const themeOptions = document.getElementById("themeOptions");

  currentThemeBtn.addEventListener("click", () => {
    themeOptions.classList.toggle("hidden");
  });

  themeOptions.addEventListener("click", (e) => {
    const option = e.target.closest(".theme-option");
    if (!option) return;

    const theme = option.dataset.theme;

    // Update button text and swatch class
    currentThemeBtn.innerHTML = `<span class="swatch swatch-${theme}"></span> ${theme.charAt(0).toUpperCase() + theme.slice(1)}`;

    themeOptions.classList.add("hidden");

    setBoardTheme(theme);
  });

  document.addEventListener("click", (e) => {
    if (!document.querySelector(".custom-theme-picker").contains(e.target)) {
      themeOptions.classList.add("hidden");
    }
  });
});

// Initial load
loadBoard();
