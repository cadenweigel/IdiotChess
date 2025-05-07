import { loadBoard } from './board.js';
import { setupThemePicker } from './theme.js';

const urlParams = new URLSearchParams(window.location.search);
const sessionId = urlParams.get("session_id");

if (!sessionId) {
  alert("Missing session ID");
  throw new Error("Missing session ID");
}

async function maybeAutoMove() {
  const res = await fetch("/api/bot-move", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId })
  });

  const data = await res.json();

  if (data.success) {
    await loadBoard(sessionId);
    setTimeout(maybeAutoMove, 500); // delay between bot moves
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  setupThemePicker();
  await loadBoard(sessionId);
});