import { loadBoard } from './board.js';
import { setupThemePicker } from './theme.js';

document.addEventListener("DOMContentLoaded", async () => {
  setupThemePicker();
  await loadBoard();
});