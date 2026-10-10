# Tarjeta digital Dragon Systems

## Publicación automática en GitHub Pages

1. Sube los cambios a la rama `main` del repositorio `KIMN24/dragon-systems-card`, incluyendo `.github/workflows/pages.yml`, `tools/` y `tests/`.
2. En **Settings → Pages → Build and deployment → Source**, selecciona **GitHub Actions**. Este ajuste reemplaza la publicación directa desde una rama.
3. En **Actions**, abre **Publish Dragon Systems**. Se ejecuta al subir cambios a `main` y también mediante **Run workflow**. Los pull requests ejecutan las pruebas y preparación sin publicar.
4. El trabajo `build` prueba el versionado y prepara `_site/`; `deploy` publica el artefacto y comprueba el HTML y todos sus recursos mediante SHA-256, con reintentos para la propagación de Pages.
5. Abre la URL que muestra el entorno `github-pages`. Si se usa la dirección predeterminada, será `https://kimn24.github.io/dragon-systems-card/`.

No se generan commits ni se reescriben archivos fuente durante la preparación. Solo se publican HTML, CSS, JavaScript, VCF, los recursos de `assets/` y un manifiesto de versiones. El código de herramientas, pruebas y configuración no se publica.

## Versionado por contenido

`tools/build.py` usa Python 3.12 y su biblioteca estándar, sin paquetes adicionales. Calcula SHA-256 del contenido publicado y añade los primeros 16 caracteres al nombre: `styles.<hash>.css`, `script.<hash>.js`, `assets/logo.<hash>.png` e `ivan-mejia.<hash>.vcf`.

Las referencias `src`, `href` y `poster` del HTML se actualizan en la copia publicada. También se resuelven `url(...)` y los `@import` de CSS: cambiar una imagen referenciada por CSS cambia el nombre de esa imagen y del CSS. Las rutas permanecen relativas. Las referencias externas (Google Fonts, WhatsApp), `tel:` y `mailto:` conservan su función.

Los archivos binarios, incluido el logotipo original, se copian sin alterar sus bytes. Se mantienen los nombres amigables de descarga mediante el atributo `download`. Los recursos que no cambian conservan su versión. La preparación falla si hay archivos locales inexistentes, rutas absolutas o dependencias circulares de CSS.

Para añadir imágenes o fuentes locales, colócalas en `assets/` y utiliza referencias relativas desde HTML o CSS. Si en el futuro se añaden módulos JavaScript con imports o recursos cargados dinámicamente por JavaScript, habrá que ampliar la preparación para resolver esas referencias; el JavaScript actual no las utiliza.

El versionado evita reutilizar recursos antiguos una vez recibido el HTML actualizado. No fuerza la actualización de una pestaña que ya está abierta ni modifica las cabeceras de caché administradas por GitHub Pages.

## Comprobación local

Con Python 3.12 o posterior instalado, desde la raíz:

```sh
python -m unittest discover -s tests -v
python tools/build.py
python -m http.server 8000 --directory _site
```

Abre `http://localhost:8000/`. `_site/` debe estar vacía o no existir antes de preparar: la herramienta no elimina directorios ni sobreescribe una publicación anterior. Para repetir, utiliza un directorio nuevo con `python tools/build.py --output _site/preview-2` y sirve ese directorio. Las pruebas utilizan carpetas temporales independientes.

Para comprobar una publicación contra un artefacto preparado del mismo commit:

```sh
python tools/verify_deploy.py https://kimn24.github.io/dragon-systems-card/ --output _site
```

## Cómo probar en el navegador

1. Comprueba que el workflow termine en verde, incluido **Check published content**.
2. Abre la página y, en herramientas de desarrollador → **Network**, identifica los nombres con hash del CSS, JavaScript, logo y favicon. Deben responder sin errores 404.
3. Cambia una regla del CSS y sube el cambio a `main`. Después del despliegue, recarga normalmente con la caché del navegador habilitada. El CSS debe tener otro nombre; el JS y el logo deben mantener el suyo si no cambiaron.
4. Comprueba las versiones negra y blanca y la persistencia del switch. Toca el teléfono y el correo: deben copiar el dato y mostrar «Copiado». Prueba WhatsApp, guardar contacto y «Enviar correo», que abre la app de correo configurada. Pulsa la flecha lateral para ver servicios y vuelve a pulsarla para regresar al contacto. También puedes volver con Escape desde el reverso. Verifica en móvil que no haya desplazamiento horizontal.
5. Activa la preferencia del dispositivo de reducir movimiento: el fondo debe permanecer estático.

## Diseño y mantenimiento

- Fondo negro o blanco, acentos rojos, degradados suaves animados y sombras. El movimiento se desactiva con `prefers-reduced-motion`.
- El QR se utiliza fuera de la página; no se genera ni muestra dentro de ella.
- El archivo original del logotipo se conserva; en la versión blanca se presenta en negro mediante CSS.
- Tipografía en `typography.css`: Montserrat ExtraBold 800 para el nombre, Regular 400 para profesión y contacto, Michroma para DRAGON y Montserrat Bold 700 con espaciado ampliado para SYSTEMS. Se cargan desde Google Fonts con fuentes locales de respaldo.
- Los iconos de teléfono y correo son SVG integrados.
- Las acciones de WhatsApp, correo y guardar contacto están centradas fuera de la tarjeta, antes del pie de página. Sus SVG proceden de [Bootstrap Icons](https://github.com/twbs/icons), con licencia MIT incluida en `assets/icons/LICENSE.txt`.
- Las filas de teléfono y correo copian los datos con confirmación accesible. «Enviar correo» usa el manejador de correo configurado en el dispositivo.
- El reverso presenta diagnóstico electrónico, diseño de sistemas embebidos y diseño 3D. La cara oculta queda fuera de la navegación por teclado y de los lectores de pantalla. El giro se desactiva con la preferencia de movimiento reducido.
- Textos y enlaces: `index.html`. Diseño: `styles.css`. Fuentes: `typography.css`. Selector: `script.js`. Contacto: `ivan-mejia.vcf`. El HTML no contiene estilos CSS; `styles.css` importa el módulo de tipografía.
- NFC queda pendiente para otra etapa.
