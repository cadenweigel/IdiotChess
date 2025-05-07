// theme.js
const boardEl = document.getElementById("board");

export function setupThemePicker() {
  const currentThemeBtn = document.getElementById("currentTheme");
  const themeOptions = document.getElementById("themeOptions");

  currentThemeBtn.addEventListener("click", () => {
    themeOptions.classList.toggle("hidden");
  });

  themeOptions.addEventListener("click", (e) => {
    const option = e.target.closest(".theme-option");
    if (!option) return;

    const theme = option.dataset.theme;
    currentThemeBtn.innerHTML = `<span class="swatch swatch-${theme}"></span> ${theme.charAt(0).toUpperCase() + theme.slice(1)}`;
    themeOptions.classList.add("hidden");

    setBoardTheme(theme);
  });

  document.addEventListener("click", (e) => {
    if (!document.querySelector(".custom-theme-picker").contains(e.target)) {
      themeOptions.classList.add("hidden");
    }
  });
}

function setBoardTheme(theme) {
  const themes = ['classic', 'blue', 'green', 'gray'];
  themes.forEach(t => boardEl.classList.remove(t));
  boardEl.classList.add(theme);
}
