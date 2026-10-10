// El QR usa la dirección pública actual. Publica primero en GitHub Pages.
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('qrcode');
  const status = document.getElementById('qr-status');
  const url = window.location.href.split('#')[0].split('?')[0];
  if (location.protocol === 'file:' || ['localhost','127.0.0.1'].includes(location.hostname)) {
    status.textContent = 'Publica la página en GitHub Pages para obtener un QR que puedan usar otras personas.';
    return;
  }
  if (typeof QRCode === 'undefined') {
    status.textContent = 'No se pudo cargar el generador de QR. Comprueba tu conexión a Internet.';
    return;
  }
  new QRCode(container, {text:url,width:180,height:180,colorDark:'#111111',colorLight:'#ffffff',correctLevel:QRCode.CorrectLevel.H});
});
