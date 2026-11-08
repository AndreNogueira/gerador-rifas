# Changelog (resumen en español)

Resumen traducido de `../CHANGELOG.md`: mismas versiones, secciones y puntos, más breves. El texto completo está en portugués.

## 3.24.0 — 2026-11-08

### Mejorado
- **Tutorial con capturas del sitio:** los temas básicos del tutorial muestran ahora el propio sitio, en las 18 lenguas, en lugar de la app de Windows.

## 3.23.0 — 2026-11-08

### Novedades
- **Tutorial y vídeo de cada función:** el tutorial tiene un tema por función (series, lista y hoja de control, marcas de corte, galería, marca propia, QR, sorteo, guardar y compartir, instalar como app, temas), cada uno con un vídeo corto grabado en la propia interfaz, en portugués e inglés.
- **Changelog, Términos, Privacidad y Contacto en 18 idiomas:** el texto aparece en el idioma elegido. El Changelog trae un resumen traducido de cada versión (el completo es el portugués); los textos legales son traducciones sin revisión nativa y, si hay diferencias, prevalece la versión portuguesa.
- **App de Windows 2.4** con lo que el sitio ha ganado desde la 3.10: menú «Extras» con series, prefijos y color por serie, números omitidos, color de los números, logotipo, marcas de corte, galería de plantillas, sorteo verificable y exportación de la lista (CSV) y de la hoja de control; y el aspecto navideño automático en diciembre. El QR de verificación e instalar como app quedan solo en el sitio.

## 3.22.0 — 2026-11-08

### Mejorado
- **Contraste de los 9 temas medido de verdad:** una prueba en un navegador mide el texto contra los píxeles reales del fondo, en claro y oscuro (WCAG AA), y se corrigió lo que no pasaba.
- Los grandes números decorativos de cada paso ya no los leen los lectores de pantalla.

## 3.21.0 — 2026-11-08

### Novedades
- **Sorteo verificable** (página «Sorteo»): sortea números de un intervalo (con números a omitir) de modo que cualquiera pueda repetirlo y obtener el mismo resultado, con una semilla pública. Se hace en el navegador y «Copiar enlace» comparte el mismo sorteo.
- El método está documentado paso a paso, con una implementación de referencia que da los mismos números que el sitio.

## 3.20.0 — 2026-11-08

### Novedades
- **QR en cada boleto:** un código QR de verificación en una esquina de cada boleto (plantillas de un solo boleto), con opciones de esquina y tamaño. Al leerlo se abre una página que confirma que este servicio emitió el código para ese boleto. Va firmado con una clave que solo tiene el servidor; no hay base de datos. No prueba el pago ni un premio.
- Solo aparece cuando el dueño del servicio configura la clave. Los pedidos con QR tienen un tope de 10 000 números.

## 3.19.0 — 2026-11-08

### Novedades
- **Marca propia:** el color de los números (en cualquier plantilla; el color de la serie gana) y el **logotipo** de la asociación en cada boleto (PNG o JPG de hasta 2 MB, plantillas de un solo boleto), con esquina y tamaño (10 a 40 %). El PNG conserva la transparencia.
- El logotipo queda solo en la sesión (se borra con ella y con «Borrar todo») y se ve en la vista previa.

## 3.18.0 — 2026-11-08

### Novedades
- **Galería de plantillas:** elija uno de cuatro diseños (Bosque, Quermesse, Natal y Gala), escriba título, organización, hasta tres premios y fecha, mire la vista previa y pulse «Usar esta plantilla»: plantilla y dígitos quedan listos. Cada diseño es un boleto con talón.
- Los diseños son originales de este proyecto, en la letra libre Vera. La letra solo tiene alfabeto latino: con otras letras sale un aviso.

## 3.17.0 — 2026-11-08

### Novedades
- **Marcas de corte:** una casilla en el panel de la hoja (plantillas de un solo boleto) dibuja trazos cortos en los márgenes, prolongando cada línea de corte. Pide al menos 3 mm de margen.
- El **talón** (el número dos veces en cada boleto) ya funcionaba: ahora está probado y documentado.
- El **sangrado** ya se respeta: si el PDF de Canva tiene una TrimBox menor que la página, el boleto es solo lo que queda dentro.

## 3.16.0 — 2026-11-08

### Novedades
- **Exportar la lista de boletos (CSV):** un archivo para Excel o Calc, un boleto por fila (serie, número y columnas Nombre, Contacto y Pagado vacías), con prefijos, series y números omitidos.
- **Hoja de control de ventas (PDF):** una tabla A4 para imprimir y rellenar a mano (36 boletos por página, con casilla de «pagado»). En los idiomas cuyas letras el PDF no puede escribir, los encabezados salen en inglés.
- Nada se guarda en el servidor: la lista sale solo del formulario.

## 3.15.0 — 2026-11-08

### Novedades
- **Series y prefijos:** un texto antes de los dígitos (A- da A-0001). Con varias series separadas por comas, cada una repite el intervalo y tiene sus propios PDF. El prefijo admite letras, espacio, punto, guion y barra (hasta 6 caracteres, sin dígitos).
- **Omitir números:** 13, 100-110 quita esos números de la secuencia (el resumen, los archivos y la verificación cuentan solo lo que se imprime).
- **Un color para cada serie.**
- Todo esto también va en «Copiar enlace» y en la vista previa.

## 3.14.0 — 2026-11-08

### Novedades
- **Instalar como app (PWA):** instale el sitio en el móvil o el ordenador; la carcasa de la app abre incluso sin red (generar sigue necesitando el servidor). Un service worker sencillo guarda solo la página, los archivos de la app y los textos de la interfaz, y nunca toca sus archivos ni los pedidos de generación.

## 3.13.0 — 2026-11-08

### Novedades
- **Recordar el archivo de dígitos:** quien vuelve al año siguiente no lo repite. Se guarda solo en su navegador (nunca en el servidor) y se reutiliza con una plantilla nueva; elegir otro lo cambia y «Borrar todo» lo elimina.
- **Copiar enlace:** un botón que copia un enlace con los valores del formulario (desde, hasta, modo, máximo por archivo, papel, margen y nombre). Quien lo abre ve los mismos valores; los archivos nunca van en el enlace.

## 3.12.0 — 2026-11-08

### Novedades
- Páginas de **Términos de uso**, **Política de privacidad** y **Contacto**, enlazadas en el pie. Son versiones provisionales, por revisar con apoyo jurídico antes de cobrar.
- **Botón de donación** en el pie: solo aparece cuando el dueño configura el enlace. El correo de contacto y el nombre del responsable también vienen de la configuración del servidor, nunca del código.

## 3.11.0 — 2026-11-08

### Novedades
- **Embudo de uso** en el panel de administración: cuántos eventos hay en cada etapa (sesión, plantilla, dígitos, vista previa, generación, descarga) y qué parte de la etapa anterior llegó a la siguiente. Muestra dónde abandonan las personas. Cuenta eventos, no personas.

## 3.10.0 — 2026-11-08

### Novedades
- Esta página: el **Changelog**, con todo lo que cambia, versión a versión.
- En **diciembre** el tema visual automático es la **Navidad** (para quien nunca eligió uno). Elegir otro tema sigue quedando guardado.

### Mejorado
- Una dependencia menos en el servidor (`python-multipart` ya no se usaba: los archivos llegan en cuerpo crudo).

## 3.9.0 — 2026-11-08

### Novedades
- Diseño pensado para **pantallas grandes** (4K, ultra-wide) y **móviles recientes**: cabecera compacta y botones de 44 px.
- La vista previa muestra una imagen cuando el navegador no puede mostrar PDF dentro de la página (Chrome de Android).
- El panel de administración registra el **tipo de pantalla** (clase, tamaño, familia) sin guardar nada personal.
- El servicio se llama a sí mismo cada 10 minutos para no dormirse.

## 3.8.0 — 2026-11-08

### Novedades
- **Panel de administración** (solo para el dueño, con contraseña) con gráficos y explicaciones del sistema y del uso: solo agregados, nunca datos personales.

## 3.7.0 — 2026-11-08

### Novedades
- **SEO**: título, descripción y texto por página, `robots.txt`, `sitemap.xml` y un 404 de verdad en las páginas que no existen.

## 3.6.0 — 2026-11-08

### Mejorado
- El sitio entrega **un solo archivo de JavaScript**, ofuscado y precomprimido: lo que viaja es bastante menor que antes.

## 3.5.0 — 2026-11-08

### Novedades
- Tema visual **Matrix Gamer**: lluvia de caracteres verdes y brillo de neón.

## 3.4.0 — 2026-11-08

### Mejorado
- Los estilos pasan a **Sass** y salen en **un único CSS**. La estructura de la página es igual en todos los temas: un tema solo cambia colores y formato.

## 3.3.0 — 2026-11-07

### Novedades
- **Temas visuales**: Premiado (el nuevo aspecto por defecto) y siete más (Quermesse, Arcade, Brutalista, Risografia, Janela 98, Gala y Natal), cada uno en claro y oscuro.
- Nuevo icono de la aplicación.
