# Tarjeta digital Dragon Systems

## Publicar en GitHub Pages
1. Inicia sesión en GitHub y crea un repositorio público llamado `dragon-systems-card`.
2. Selecciona **Add file → Upload files** y sube **el contenido** de esta carpeta (`index.html`, `styles.css`, `script.js`, `ivan-mejia.vcf` y la carpeta `assets` con `logo.png`). El archivo `index.html` debe quedar en la raíz del repositorio.
3. En el repositorio abre **Settings → Pages**.
4. En **Build and deployment**, elige **Deploy from a branch**. Selecciona la rama `main` y carpeta `/(root)`, y pulsa **Save**.
5. Espera a que GitHub muestre la URL. Normalmente será `https://TU-USUARIO.github.io/dragon-systems-card/`.
6. Abre esa URL desde el celular y comprueba llamar, correo, WhatsApp y descarga del contacto.
7. Comprueba las versiones de fondo negro y blanco con el selector. El navegador recuerda la elección cuando permite almacenamiento local.

## Diseño
- El QR se utilizará fuera de la página para acceder a la tarjeta; no se muestra ni se genera dentro de ella.
- Se conserva el archivo original del logotipo. En la versión blanca se presenta en negro mediante CSS, como en la tarjeta de referencia.
- Montserrat aproxima la tipografía de las imágenes; la fuente original no está identificada. Se carga desde Google Fonts con fuentes locales de respaldo.
- Los iconos de teléfono y correo son SVG integrados, sin bibliotecas externas.

## Cambios
- Para cambiar textos, enlaces o botones: edita `index.html`.
- Para cambiar colores, fuentes o distribución: edita `styles.css`.
- Para cambiar datos del contacto descargable: edita `ivan-mejia.vcf`.
- Para cambiar el logotipo: reemplaza `assets/logo.png`.

## Nota
GitHub Pages publica el contenido del repositorio. No incluyas contraseñas ni información privada. NFC queda pendiente para una etapa posterior.
