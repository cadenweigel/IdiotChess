const boardEl = document.getElementById("board");
const pieceBasePath = "/static/images/classic_pieces/";

const pieceImageMap = {
  'P': 'white_pawn.png', 'R': 'white_rook.png', 'N': 'white_knight.png',
  'B': 'white_bishop.png', 'Q': 'white_queen.png', 'K': 'white_king.png',
  'p': 'black_pawn.png', 'r': 'black_rook.png', 'n': 'black_knight.png',
  'b': 'black_bishop.png', 'q': 'black_queen.png', 'k': 'black_king.png',
};

let dragState = {
  dragging: false,
  from: null,
  pieceEl: null,
  ghost: null,
};

let dragStartX = 0;
let dragStartY = 0;

export async function loadBoard(sessionId) {
  const res = await fetch(`/api/board?session_id=${sessionId}`);
  const data = await res.json();

  if (data.error) {
    alert(data.error);
    return;
  }

  renderBoard(data.board, sessionId);
  updateStatus(data.status);
}

function renderBoard(board, sessionId) {
  boardEl.innerHTML = "";

  for (let row = 0; row < 8; row++) {
    for (let col = 0; col < 8; col++) {
      const square = document.createElement("div");
      square.classList.add("square", (row + col) % 2 === 0 ? "light" : "dark");
      square.dataset.row = row;
      square.dataset.col = col;
      square.dataset.pos = `${row},${col}`;

      const piece = board[row][col];
      if (piece) {
        const img = document.createElement("img");
        img.src = pieceBasePath + pieceImageMap[piece];
        img.alt = piece;
        img.classList.add("draggable-piece");
        square.appendChild(img);
      }

      boardEl.appendChild(square);
    }
  }
}

document.addEventListener("mousedown", (e) => {
  const target = e.target.closest("img");
  if (!target || !target.classList.contains("draggable-piece")) return;

  e.preventDefault(); // prevent native image drag

  const square = target.parentElement;
  const row = parseInt(square.dataset.row);
  const col = parseInt(square.dataset.col);

  dragStartX = e.pageX;
  dragStartY = e.pageY;

  dragState.from = [row, col];
  dragState.pieceEl = target;
});

document.addEventListener("mousemove", (e) => {
  if (!dragState.pieceEl || dragState.dragging) return;

  const dist = Math.hypot(e.pageX - dragStartX, e.pageY - dragStartY);
  if (dist > 5) {
    dragState.dragging = true;

    const ghost = dragState.pieceEl.cloneNode();
    ghost.classList.add("drag-ghost");
    ghost.style.position = "absolute";
    ghost.style.pointerEvents = "none";
    ghost.style.width = `${dragState.pieceEl.offsetWidth}px`;
    ghost.style.height = `${dragState.pieceEl.offsetHeight}px`;
    document.body.appendChild(ghost);
    dragState.ghost = ghost;
  }

  if (dragState.ghost) {
    dragState.ghost.style.left = `${e.pageX - 25}px`;
    dragState.ghost.style.top = `${e.pageY - 25}px`;
  }
});

document.addEventListener("mouseup", async (e) => {
  console.log("🖱 mouseup event fired");
  if (!dragState.dragging) {
    console.log("❌ Not dragging — abort");
    return;
  }

  dragState.dragging = false;

  const rect = boardEl.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  const squareSize = boardEl.offsetWidth / 8;
  const col = Math.floor(x / squareSize);
  const row = Math.floor(y / squareSize);

  console.log(`📍 Drop position row,col = ${row},${col}`);

  const from = dragState.from;
  const to = [row, col];

  if (dragState.ghost) {
    dragState.ghost.remove();
    dragState.ghost = null;
  }

  if (!from || col < 0 || col > 7 || row < 0 || row > 7) {
    console.log("❌ Invalid target square");
    return;
  }

  console.log(`🚚 Attempting move from ${from} to ${to}`);

  const res = await fetch("/api/move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, from, to }),
  });

  const data = await res.json();
  console.log("📬 Move response:", data);

  if (data.success) {
    await loadBoard(sessionId);
    if (data.turn.includes("bot")) {
      setTimeout(() => triggerBotMove(sessionId), 500);
    }
  } else {
    alert(data.error);
  }

  dragState.from = null;
  dragState.pieceEl = null;
});

function triggerBotMove(sessionId) {
  fetch("/api/bot-move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      animateBotMove(data.from, data.to);
      setTimeout(() => loadBoard(sessionId), 400);
    }
  });
}

function animateBotMove(from, to) {
  const fromSquare = document.querySelector(`[data-pos="${from[0]},${from[1]}"]`);
  const toSquare = document.querySelector(`[data-pos="${to[0]},${to[1]}"]`);

  if (!fromSquare || !toSquare) return;

  const pieceImg = fromSquare.querySelector("img");
  if (!pieceImg) return;

  const clone = pieceImg.cloneNode();
  const boardRect = boardEl.getBoundingClientRect();
  const fromRect = fromSquare.getBoundingClientRect();
  const toRect = toSquare.getBoundingClientRect();

  clone.style.position = "absolute";
  clone.style.pointerEvents = "none";
  clone.style.zIndex = "1000";
  clone.style.left = `${fromRect.left - boardRect.left}px`;
  clone.style.top = `${fromRect.top - boardRect.top}px`;
  clone.style.width = `${fromRect.width}px`;
  clone.style.height = `${fromRect.height}px`;
  clone.style.transition = "all 0.3s ease-in-out";

  boardEl.appendChild(clone);

  requestAnimationFrame(() => {
    clone.style.left = `${toRect.left - boardRect.left}px`;
    clone.style.top = `${toRect.top - boardRect.top}px`;
  });

  setTimeout(() => {
    clone.remove();
  }, 350);
}

function updateStatus(status) {
  const messageEl = document.getElementById("message");
  messageEl.textContent = status;
}
