// Conserva la versión elegida cuando el navegador permite guardar preferencias.
const themeSwitch = document.querySelector('.theme-switch');
const themeColor = document.querySelector('meta[name="theme-color"]');

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  themeColor.content = theme === 'light' ? '#ffffff' : '#101010';
  themeSwitch.setAttribute('aria-checked', String(theme === 'dark'));
}

try {
  const savedTheme = localStorage.getItem('dragon-systems-theme');
  if (savedTheme === 'light' || savedTheme === 'dark') applyTheme(savedTheme);
} catch {
  // El selector también funciona si el almacenamiento está bloqueado.
}

themeSwitch.addEventListener('click', () => {
  const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(theme);
  try {
    localStorage.setItem('dragon-systems-theme', theme);
  } catch {
    // La selección permanece activa durante esta visita.
  }
});
themeSwitch.hidden = false;

const flipCard = document.querySelector('.flip-card');
const frontFace = document.querySelector('.card-front');
const backFace = document.querySelector('.card-back');
const servicesTitle = document.getElementById('services-title');
const cardArrow = document.querySelector('.card-arrow');
let showingServices = false;
backFace.hidden = false;
backFace.inert = true;
backFace.setAttribute('aria-hidden', 'true');
cardArrow.hidden = false;

function flipTo(showBack) {
  const incoming = showBack ? backFace : frontFace;
  const outgoing = showBack ? frontFace : backFace;
  incoming.inert = false;
  incoming.removeAttribute('aria-hidden');
  flipCard.classList.toggle('is-flipped', showBack);
  showingServices = showBack;
  const label = showBack ? 'Volver al contacto' : 'Ver servicios';
  cardArrow.setAttribute('aria-label', label);
  cardArrow.title = label;
  cardArrow.setAttribute('aria-controls', showBack ? 'contact-face' : 'services-face');
  (showBack ? servicesTitle : cardArrow).focus({ preventScroll: true });
  outgoing.inert = true;
  outgoing.setAttribute('aria-hidden', 'true');
}

cardArrow.addEventListener('click', () => flipTo(!showingServices));
flipCard.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && showingServices) flipTo(false);
});

const copyStatus = document.querySelector('.copy-status');
let copyResetTimer;

async function copyText(value) {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(value);
    return;
  }
  // Respaldo para navegadores que no ofrecen la API del portapapeles.
  const input = document.createElement('textarea');
  input.value = value;
  input.setAttribute('readonly', '');
  input.style.position = 'fixed';
  input.style.opacity = '0';
  document.body.append(input);
  try {
    input.select();
    input.setSelectionRange(0, value.length);
    if (!document.execCommand('copy')) throw new Error('Clipboard unavailable');
  } finally {
    input.remove();
  }
}

document.querySelectorAll('[data-copy]').forEach((button) => {
  let busy = false;
  button.addEventListener('click', async () => {
    if (busy) return;
    busy = true;
    const hint = button.querySelector('small');
    clearTimeout(copyResetTimer);
    document.querySelectorAll('[data-copy] small').forEach((item) => {
      item.textContent = 'Toca para copiar';
    });
    copyStatus.textContent = '';
    try {
      await copyText(button.dataset.copy);
      hint.textContent = 'Copiado';
      copyStatus.textContent = button.dataset.copyLabel + ' copiado';
    } catch {
      hint.textContent = 'No se pudo copiar';
      copyStatus.textContent = 'No se pudo copiar. Selecciona el dato y cópialo manualmente.';
    } finally {
      busy = false;
      button.focus({ preventScroll: true });
      copyResetTimer = setTimeout(() => {
        hint.textContent = 'Toca para copiar';
        copyStatus.textContent = '';
      }, 3500);
    }
  });
});
