// Conserva la versión elegida cuando el navegador permite guardar preferencias.
const themeButtons = document.querySelectorAll('[data-theme-choice]');
const themeColor = document.querySelector('meta[name="theme-color"]');

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  themeColor.content = theme === 'light' ? '#ffffff' : '#101010';
  themeButtons.forEach((button) => {
    button.setAttribute('aria-pressed', String(button.dataset.themeChoice === theme));
  });
}

try {
  const savedTheme = localStorage.getItem('dragon-systems-theme');
  if (savedTheme === 'light' || savedTheme === 'dark') applyTheme(savedTheme);
} catch {
  // El selector también funciona si el almacenamiento está bloqueado.
}

themeButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const theme = button.dataset.themeChoice;
    applyTheme(theme);
    try {
      localStorage.setItem('dragon-systems-theme', theme);
    } catch {
      // La selección permanece activa durante esta visita.
    }
  });
});
document.querySelector('.theme-picker').hidden = false;
