# Changelog (resumen en español)

Resumen traducido de `../CHANGELOG.md`: mismas versiones, secciones y puntos, más breves. El texto completo está en portugués.

## 3.97.0 — 2026-11-27

### Mejorado
- **Guías «Cómo hacer una rifa para el colegio» y «…para los bomberos» reescritas**: dejan de compartir la estructura y las frases de las demás guías por público. La del colegio habla ahora de quién decide (la asociación de padres o el consejo escolar), del calendario escolar (reunión de padres, fin de trimestre), y advierte, en el propio texto y no solo en un consejo, de no escribir nunca el nombre de un alumno ni otros datos personales en el boleto. La de los bomberos habla de la propia dirección o mando del cuerpo, de un motivo concreto (un vehículo, mangueras, equipo de protección), de la venta de puerta en puerta de uniforme y del código QR de verificación para mantener la confianza de quienes compran año tras año.

## 3.96.0 — 2026-11-27

### Mejorado
- **Las guías del club y de la fiesta de barrio tienen ahora contenido propio**: `/rifas-para-clubes` y `/rifas-para-festas` dejan de repetir casi el mismo texto de las demás guías por público; ahora hablan de la realidad de cada una: la junta y los colores del club, los patrocinadores; la comisión de vecinos (o solo un grupo de vecinos, sin asociación formal) y quién se responsabiliza del dinero hasta el sorteo.

## 3.95.0 — 2026-11-27

### Corregido
- **Título de la página inicial tras cargar**: solo mostraba «Gerador de Rifas» en vez del título completo que el servidor ya envía a quien no ejecuta JavaScript; React ahora repone el título correcto.
- **Salto visual en la cabecera**: medir qué cabe junto al nombre de la app podía, por un instante, hacer que la cabecera pasara a dos líneas y empujara el resto de la página hacia abajo; se encontró la causa real (no eran los anuncios) y se corrigió.

### Mejorado
- **La página inicial no pierde la explicación ni los guías al montarse**: «Cómo funciona», el tutorial, el vídeo, «Acerca de» y los guías «Cómo hacer» también viven ahora en el cuerpo de la página, no solo en el menú «Ayuda».
- **Los idiomas cargan en paralelo**: pedir los textos de la interfaz ya no espera a la lista de idiomas solo para decidir el idioma de la página, lo que adelanta la 1.ª pintura con contenido en móviles y conexiones lentas.
- **Guía «Cómo hacer una rifa para la parroquia» con voz más propia**: decidir con el consejo parroquial, el sorteo verificable como respuesta a la confianza de quien compra, y ya no nombra una autoridad local concreta (varía según la región).

## 3.94.0 — 2026-11-26

### Corregido
- **Letra pequeña en la galería de diseños, en el móvil**: dentro del panel «¿Sin plantilla? Elija uno de la galería», la lista «Cuántos premios», el formato de la fecha y el campo «texto antes de la fecha» aparecían a 14 px, como los tres campos ya corregidos en la versión anterior. Ahora tienen al menos 16 px.
- **El paso 2 solo dice «(obligatorio)» cuando realmente falta**: al elegir un diseño de la galería (que ya trae los dígitos listos), el título del paso 2 deja de decir «(obligatorio)» mientras el campo esté relleno.

### Mejorado
- **La descripción de la página de inicio ya no exige Canva**: la descripción que aparece en los buscadores solo hablaba de la plantilla de Canva; ahora también dice que se puede elegir un diseño ya hecho de la galería, sin necesitarlo.

## 3.93.0 — 2026-11-26

### Corregido
- **Letra pequeña en tres campos en el móvil**: los campos del máximo por archivo, el color de los números y el nombre de los archivos mostraban el texto por debajo de 16 px, lo que hace que iOS Safari amplíe automáticamente al enfocar. Ahora tienen el mismo tamaño que los campos vecinos.

### Mejorado
- **«Acerca de» dice quién hace el Generador de Rifas**: cuando el responsable del servicio se identifica (la misma configuración de los Términos y la Privacidad), la página «Acerca de» dice ahora quién lo creó y lo mantiene, y que la app para Windows llegó primero.

## 3.92.0 — 2026-11-26

### Corregido
- **Texto del paso 4 («Destino») en el sitio**: el tutorial y la página de inicio decían «elija la carpeta donde guardar los PDF», cierto solo en la app de Windows — en el sitio, los archivos se descargan automáticamente por el navegador. El texto del sitio ya no habla de ninguna carpeta.

## 3.91.0 — 2026-11-26

### Mejorado
- **La galería de diseños gana el mismo peso visual que subir la plantilla**: en la página de inicio, elegir un diseño ya hecho (sin necesitar Canva) deja de ser un enlace secundario escondido debajo de la subida del PDF — ahora tiene una caja con el mismo protagonismo.
- **Más enlaces entre páginas**: las guías del sorteo y del preçario pasan a enlazar con su propia herramienta (`/sorteio`, `/precario`) en lugar del generador de rifas, y la página de inicio también enlaza ahora con el índice de guías «Cómo hacerlo» (`/como-fazer`).

## 3.90.0 — 2026-11-26

### Corregido
- **La página en portugués ya no cambia de idioma sola**: visitar una dirección sin prefijo (`/`, `/tutorial`, …) sin que el navegador diga que el idioma es portugués — el caso de muchos rastreadores de buscadores y de algunos navegadores — hacía que el sitio reescribiera solo la URL y todo el contenido a inglés. Sin prefijo significa siempre portugués, como estaba previsto; los 21 idiomas con prefijo siguen funcionando igual. El `robots.txt` también deja de bloquear del todo `/api/linguas`, `/api/textos`, `/api/guia(s)` y la documentación de la API pública (`/api/v1/docs`), para que los buscadores puedan renderizar e indexar bien el sitio.

### Mejorado
- **Selector de idioma más rápido**: los nombres nativos de los idiomas en el selector (como «Tiếng Việt» o «Čeština») ahora usan la letra del sistema en vez de la de la marca, así la página ya no tiene que bajar glifos extra solo para mostrarlos — eso retrasaba el texto principal y a veces lo movía.

## 3.89.0 — 2026-11-26

### Mejorado
- **Tres bibliotecas de imágenes de contorno más en el preçario: Tabler Icons, Lucide y Material Symbols** (sin exigir crédito): más de 100 artículos ganaron alternativas de estas bibliotecas, elegidas una a una para representar de verdad el artículo (a diferencia de las anteriores, no hay forma automática de encontrarlas). A diferencia de las imágenes en color, estas se pintan del color del texto del momento — del sitio, de la app Windows o del papel elegido en el PDF — para no quedar nunca invisibles en un tema oscuro o un papel oscuro.

## 3.88.0 — 2026-11-21

### Mejorado
- **Dos bibliotecas más de imágenes en el preçario: Twemoji y OpenMoji**: se suman al Noto Emoji y al Fluent Emoji 3D, sin quitar ninguna imagen que ya hubiera — el selector ahora agrupa las imágenes por biblioteca, con el nombre de cada una. El Twemoji (CC BY 4.0) y el OpenMoji (CC BY-SA 4.0) piden crédito a los autores, que aparece en la Política de privacidad y, solo cuando se usa de verdad una de esas imágenes, en el pie del PDF y de las etiquetas de recogida generados.

## 3.87.0 — 2026-11-21

### Mejorado
- **Más imágenes a elegir en el preçario, del Fluent Emoji 3D de Microsoft (licencia MIT, sin exigir crédito)**: los 93 artículos del catálogo ganaron, además de las imágenes Noto Emoji de siempre, una alternativa en estilo 3D allí donde exista para ese código, sin quitar ninguna de las que ya había.

## 3.86.0 — 2026-11-21

### Mejorado
- **Espacio entre las rifas y marcas de corte entre cada una**: al activar las marcas de corte, el hueco que antes solo agrandaba el margen pasa a ser espacio entre cada rifa, y las marcas (antes solo en los márgenes de la hoja) aparecen ahora también entre cada rifa.

## 3.85.0 — 2026-11-21

### Corregido
- **Página 404 de verdad**: un enlace erróneo mostraba el generador escondido bajo el estado 404. Ahora aparece una página real de «Página no encontrada», traducida, con el enlace para volver.
- **Icono de reserva (favicon.ico)**: para herramientas antiguas que solo miran esa ruta.

## 3.84.0 — 2026-11-21

### Novedades
- **Diseño «Cumpleaños» en la galería y en el preçario**: globos, banderines y confeti en rosa, turquesa y amarillo — el 25.º diseño que se suma a los ya existentes, para que la fiesta de cumpleaños tenga su propio estilo en las rifas, el preçario y los vales.

## 3.83.0 — 2026-11-21

### Mejorado
- **Más imágenes a elegir por artículo del preçario**: cada artículo del catálogo puede tener ahora hasta 8 imágenes (antes 5) — los 93 ganaron al menos una alternativa nueva, elegida a juego (el agua ganó una ola, el café un mate, la tarta confeti…).

## 3.82.0 — 2026-11-20

### Corregido
- **Márgenes desiguales al llenar la hoja con menos rifas de las que cabían**: pedir menos rifas por hoja que el máximo las dejaba pegadas arriba a la izquierda, con todo el hueco abajo a la derecha — la guillotina recta ya no las separaba bien. Ahora quedan siempre centradas, con el mismo margen en los cuatro lados.

## 3.81.0 — 2026-11-20

### Novedades
- **Etiquetas de recogida**: ¿se paga en un sitio y se recoge en otro? En la página de la lista de precios, cada artículo se convierte en una etiqueta con la imagen, el nombre, el precio (si quiere) y la zona donde se recoge (la barra, la cocina…), con las copias que elija, 24 por hoja A4 con guías de corte y un color por zona. Un combo da una etiqueta por artículo, cada una en la zona de su sección (sitio y app de Windows; con tutorial y vídeos).

## 3.80.0 — 2026-11-20

### Novedades
- **Combos entre secciones en la lista de precios**: una de 2 a 4 artículos del catálogo, incluso de secciones distintas (por ejemplo, un bocadillo y una bebida), en un solo precio. El combo aparece en una sección nueva, «Menús y combos», con las imágenes de los artículos una junto a otra, y puede tener un nombre propio (sitio y app de Windows).

## 3.79.0 — 2026-11-20

### Novedades
- **Colores y logotipo en la lista de precios**: puede cambiar el color principal, el de acento y el del papel del diseño (los precios se ajustan solos para leerse siempre) y poner el logotipo de su asociación (PNG o JPG) en la cabecera, a la izquierda o a la derecha, o en el pie (sitio y app de Windows). Los colores y el sitio quedan en el archivo de la lista y en el enlace compartido; el logotipo solo sirve para dibujar la vista previa y el PDF y nunca se guarda.

## 3.78.0 — 2026-11-20

### Novedades
- **Hasta 5 imágenes a elegir por artículo**: en la lista de precios, pulse la imagen de un artículo del catálogo y elija la que más le guste entre hasta 5 (el agua puede ser una gota, un grifo, hielo, un vaso…). La elección se ve en el PDF y se guarda en el archivo de la lista y en el enlace compartido (sitio y app de Windows).

## 3.77.0 — 2026-11-20

### Mejorado
- **Listas y filas de la lista de precios más ordenadas**: todas las listas desplegables del sitio tienen ahora el aspecto de los demás campos, con una flecha que sigue el tema (claro y oscuro). En la lista de precios, la × para quitar un artículo y el botón de la foto ocupan mucho menos espacio, los precios ya no saltan a una segunda línea y, en el móvil, el nombre queda arriba y los campos debajo.

## 3.76.0 — 2026-11-20

### Novedades
- **Fotos propias en la lista de precios**: en cada artículo puede pulsar «Foto» y poner una imagen suya (PNG o JPG) en lugar del icono (hasta 20 por lista; sitio y app de Windows). La foto se reduce en su ordenador y solo sirve para dibujar la vista previa y el PDF: no se guarda en el servidor, ni en el archivo de la lista, ni en el enlace compartido.

## 3.75.0 — 2026-11-20

### Novedades
- **Compartir la lista de precios por enlace** (en el sitio, cuando el servicio tiene base de datos): «Compartir por enlace» en la página de la lista crea un enlace que cualquiera puede abrir para ver y continuar su lista (textos, artículos, precios y diseño). Se guarda 90 días desde el último acceso, sin nada sobre quién la comparte; la Política de privacidad se actualizó.

## 3.74.0 — 2026-11-20

### Novedades
- **Dos tamaños en la lista de precios**: active «Dos tamaños (dos precios por artículo)» (sitio y app de Windows) para escribir dos precios en cada artículo (por ejemplo, pequeño y grande, o el artículo y el menú). Las dos columnas salen alineadas, con los nombres que elija encima («Pequeño» y «Grande» por defecto), y se guardan en el archivo de la lista.

## 3.73.0 — 2026-11-20

### Novedades
- **Tarjetas de mesa**: en el formato de la lista de precios elija «Tarjetas de mesa (4 por hoja A4)» (sitio y app de Windows) y la lista sale en tarjetas A6, cuatro en una hoja A4 con guías de corte, listas para imprimir y cortar para las mesas (hasta 12 artículos).

## 3.72.0 — 2026-11-20

### Novedades
- **Lista de precios en «pizarra»**: un diseño nuevo en la lista «Ocasión y tema» (y en la app de Windows): fondo verde oscuro de pizarra escolar, marco de madera y texto a tiza (blanco y amarillo), ideal para el puesto, la terraza o el aula.

## 3.71.0 — 2026-11-20

### Novedades
- **Vales de fichas numerados** (en la lista de precios, con una moneda inventada; y «Extras → Lista de precios… → Vales numerados…» en la app de Windows): elija cuántas fichas vale cada vale, el título y una nota, vea el vale con el diseño de la lista y créelos. Continúa en el generador de rifas, que numera los vales con series, QR de verificación y hojas listas para imprimir.

## 3.70.0 — 2026-11-20

### Novedades
- **Generador de listas de precios para fiestas** (`/precario`, y «Extras → Lista de precios…» en la app de Windows): elija la ocasión (se sugiere la de la época) y los artículos de un catálogo con imágenes, escriba los precios en la moneda de su país o en una inventada (fichas…) y descargue el PDF (o una imagen) listo para imprimir, en A5, A4 o A3 y con los 24 diseños de la galería. También hay una guía nueva: «Cómo hacer la lista de precios de una fiesta».

## 3.69.0 — 2026-11-19

### Novedades
- **Portugués de Brasil** (`/pt-br`): el sitio, las guías y las páginas legales existen también en portugués de Brasil, con su vocabulario, una Política de privacidad adaptada a la LGPD brasileña y el idioma elegido solo cuando el navegador está en pt-BR. El portugués de Portugal sigue igual, sin prefijo en la dirección.

## 3.68.0 — 2026-11-19

### Novedades
- **Tres guías nuevas, por tema** (no por público): cómo numerar los boletos de una rifa, cómo hacer un sorteo verificable (enlaza con la página «Sorteo») y cuántos boletos hacer y a qué precio. Están en «Todas las guías» (`/como-fazer`), en 22 idiomas.

## 3.67.0 — 2026-11-19

### Novedades
- **Índice de guías «Cómo hacer»** (`/como-fazer`): una página con todas las guías y un resumen de cada una; cada guía termina con enlaces a las demás. También en el menú «Ayuda» («Todas las guías»).
- Las guías y el índice indican a Google su ruta (Inicio › Cómo hacer › guía) para mostrarla en los resultados.

## 3.66.0 — 2026-11-19

### Novedades
- **Invitación a dejar un comentario:** después de descargar las rifas, aparece (una sola vez por dispositivo) un aviso discreto que invita a dejar un comentario, anónimo si lo desea. Puede descartarlo con «Ahora no».

## 3.65.0 — 2026-11-19

### Mejorado
- **Un sitio más ligero y más seguro:** quien solo genera rifas descarga un 24 % menos de código (el panel de administración, el editor de plantillas y el sorteo solo se cargan al abrir la página). El sitio también envía ahora cabeceras de seguridad y responde a verificadores de enlaces y a vistas previas al compartir.

## 3.64.0 — 2026-11-19

### Novedades
- **Copia de seguridad semanal de los datos del panel de administración:** cada lunes el servicio guarda, en el almacenamiento del mismo proveedor de la base de datos, una copia del historial, los objetivos, el registro de acciones, los comentarios y los textos de SEO (últimas 8 semanas), con un script para restaurarla.

## 3.63.0 — 2026-11-19

### Novedades
- **Rendimiento real del sitio en las estadísticas:** el panel de administración muestra, por día, cuánto tarda en aparecer la página, cuánto se mueve el contenido y cuánto tarda en responder a un clic, medido en los navegadores de los visitantes (móvil y ordenador). Solo tres números anónimos por visita; se actualizó la Política de privacidad.

## 3.62.0 — 2026-11-19

### Novedades
- **Origen de las visitas en las estadísticas:** el panel de administración muestra ahora de dónde vienen las visitas, en categorías generales (búsqueda, redes sociales, correo, otros sitios o directas) y por campaña (utm_source), para medir una difusión. Nunca se guarda la dirección de la página de origen ni la IP; se actualizó la Política de privacidad.

## 3.61.0 — 2026-11-19

### Novedades
- **Registro de acciones en el panel de administración:** se guarda durante 400 días quién hizo qué y cuándo en el panel (entradas, comentarios borrados u ocultos, claves de la API, textos de SEO, objetivos), sin datos de visitantes ni contraseñas.

## 3.60.0 — 2026-11-19

### Novedades
- **Objetivos diarios en el panel de administración:** el responsable fija una meta por día (sesiones, generaciones, números generados, descargas…) y ve si el último día la cumplió, la media de los últimos 7 días y en cuántos se alcanzó; el informe diario por correo lleva la misma sección.

## 3.59.0 — 2026-11-19

### Novedades
- **Comentarios con estado en el panel de administración:** el responsable puede marcar cada comentario como leído, favorito u oculto (un comentario oculto deja de aparecer en la página pública, pero no se pierde), filtrar por estado y ver cuántos quedan por leer.

## 3.58.0 — 2026-11-19

### Novedades
- **Cuotas del alojamiento gratuito en el panel de administración:** muestra cuántas de las 750 horas mensuales de Render ha gastado el servicio (con la proyección hasta fin de mes) y cuánto espacio ocupa la base de datos en el plan gratuito de Neon, con aviso en el informe diario por correo antes de que se agoten.

## 3.57.0 — 2026-11-19

### Novedades
- **Marcas de versión en los gráficos del panel de administración:** cada gráfico diario señala el día en que llegó una versión nueva de la app (y el informe diario dice cuál), para relacionar una subida de errores o del tiempo de respuesta con la actualización que la causó.

## 3.56.0 — 2026-11-19

### Novedades
- **Resumen semanal y mensual por correo para el responsable del sitio:** los lunes llega el resumen de la semana y el día 1 el del mes, con los totales comparados con el período anterior y una miniatura de cada día. Leen del historial permanente. Solo recuentos.

## 3.55.0 — 2026-11-19

### Novedades
- **Alertas inmediatas por correo para el responsable del sitio:** si hay una racha de errores del servidor, reinicios del motor, memoria cerca del límite o la base de datos sin respuesta, llega un aviso al instante (sin esperar al informe diario y sin repetirse durante 6 horas). Solo recuentos.

## 3.54.0 — 2026-11-19

### Novedades
- **Historial permanente en el panel de administración:** tras la medianoche se guarda un resumen de cada día, por lo que la evolución diaria muestra ahora meses y hasta 2 años (antes solo 90 días). Solo recuentos, como el resto del panel.

## 3.53.0 — 2026-11-19

### Novedades
- **Informe diario por correo para el responsable del sitio:** cada día, justo después de la medianoche, llega un correo con todo lo registrado en el día que acaba de terminar (uso, público, errores y recursos del servidor), comparado con la media de los 7 días anteriores, para seguir la app sin abrir el panel. Solo recuentos: nunca datos de los visitantes.

## 3.52.0 — 2026-11-19

### Mejorado
- **Comentarios sin dirección IP:** en lugar de la IP, se guarda solo el país desde el que se envió el comentario (solo lo ve el responsable del sitio). La dirección IP ya no se guarda: las de los comentarios anteriores se borraron y se actualizó la Política de privacidad.

## 3.51.0 — 2026-11-19

### Novedades
- **Comentarios:** una página «Comentarios» donde todos ven lo que opinan los demás del generador, y una página para dejar el suyo: puede permanecer anónimo/a o mostrar un nombre (sin nombre aparece «Visitante n.º …»). La dirección IP se guarda solo para el responsable del sitio, para frenar abusos, nunca se muestra y se borra a los 90 días.
- **Informar de un problema:** nueva página donde describe un error y, al pulsar «Abrir», se crea directamente en el GitHub del proyecto, sin necesidad de cuenta (su IP no se envía y la información técnica del navegador solo va si la añade).
- Las dos páginas y los botones «Comentarios» e «Informar de un problema» están a la vista en la cabecera, el menú y el pie de página; la Política de privacidad (22 idiomas) explica qué se guarda.

## 3.50.0 — 2026-11-18

### Mejorado
- **Cabecera que se adapta a la pantalla:** todas las opciones quedan a la derecha, en una sola fila y sin huecos, y a medida que la pantalla se reduce pasan una a una a un menú «hamburguesa» (primero el modo claro/oscuro y el estilo, al final el donativo). En el móvil solo quedan el nombre de la aplicación y el botón del menú, que se abre con las páginas, la ayuda, compartir y los ajustes.

## 3.49.0 — 2026-11-18

### Novedades
- **Panel con la evolución día a día:** una nueva vista «Evolución diaria» muestra, a lo largo de hasta 90 días, todo lo que el servidor guarda en la base de datos (sesiones, generaciones, números generados, idiomas, países, estilos, galería, editor, API, peticiones, tiempos de respuesta, CPU y memoria…), con la tendencia de cada indicador y la descarga de todo en CSV. Es una función del panel del propietario: los visitantes no notan diferencia.

## 3.48.0 — 2026-11-18

### Mejorado
- **Menú «Ayuda» en la cabecera:** el tutorial, el vídeo y las guías «Cómo hacerlo» pasan a una sola pestaña, «Ayuda». La cabecera es más corta y el nombre de la aplicación se ve siempre completo y en una sola línea, en cualquier idioma y tamaño de pantalla.

## 3.47.0 — 2026-11-15

### Mejorado
- **Galería de plantillas:** la lista de diseños ya no queda cortada ni fuera de sitio en algunos temas; cada premio tiene su número; todos los cuadros de texto muestran el límite de caracteres (por ejemplo 12/50); y el botón «Usar esta plantilla» ya no queda pegado al último cuadro.
- **Fecha del sorteo en un calendario propio:** en vez del campo del navegador (que mostraba «dd/mm/aaaa» y un selector en un idioma distinto del del sitio), hay un calendario en los 22 idiomas, con los meses y los días de la semana en el idioma elegido, la fecha escrita como la escribe ese idioma, el primer día de la semana correcto y los botones «Hoy» y «Borrar». Funciona con el teclado (flechas, Re Pág/Av Pág, Inicio/Fin, Intro y Esc).
- **«Acerca de» más completo:** el texto se ha reescrito, en los 22 idiomas, y explica para quién es el generador, qué hace, qué hacer tras imprimir, cómo protege la privacidad y dónde se puede usar.

## 3.46.0 — 2026-11-15

### Mejorado
- **Donativo más a la vista:** cuando el servicio tiene un enlace de donativo, el botón aparece ahora en la cabecera (junto a «Compartir») y, tras generar los archivos, con una frase de invitación. También sigue en el pie de página.

## 3.45.0 — 2026-11-14

### Mejorado
- **Galería de plantillas en una sola línea:** los 24 diseños se eligen ahora en una caja de una línea en la que cada opción muestra un mini dibujo de la plantilla, en vez de una larga lista de botones. Funciona con ratón, toque y teclado (flechas, Inicio/Fin, una letra, Intro y Esc).

## 3.44.0 — 2026-11-14

### Mejorado
- **Privacidad:** los recuentos de uso incluyen ahora el país de la visita (solo el código, deducido por la red del alojamiento; la dirección IP sigue sin guardarse). La Política de privacidad lo explica en las 22 lenguas.

## 3.43.1 — 2026-11-14

### Mejorado
- **Pie de página más limpio:** las guías «Cómo hacer» ahora solo aparecen en el grupo de la cabecera; ya no se repiten al final de la página.

## 3.43.0 — 2026-11-14

### Mejorado
- **Fecha del sorteo en un calendario:** en la galería de plantillas eliges la fecha en un calendario y luego cómo aparece en la rifa (31/12/2026, 31 dic 2026, 31 de diciembre de 2026 o con el día de la semana), escrita en el idioma del sitio. También se puede escribir a mano, ahora hasta 60 caracteres.
- **Textos más anchos:** las páginas de texto (guías, tutorial, términos…) ocupan ahora todo el ancho de la página, con menos líneas y párrafos.

## 3.42.0 — 2026-11-14

### Mejorado
- **Cabecera:** el nuevo grupo «Cómo hacer», junto al tutorial, reúne las guías (escuelas, asociaciones, clubes, bomberos, fiestas de barrio y parroquias). El botón «Compartir» pasó del pie a la cabecera, destacado, y su lista muestra los iconos de WhatsApp, Telegram, Facebook, correo y «Copiar enlace».

## 3.41.0 — 2026-11-14

### Mejorado
- **Vista previa automática:** al cambiar la plantilla, los dígitos, el logotipo o cualquier campo que altere la página final (números, dígitos, hoja, series, colores, QR…), la vista previa con números reales se rehace sola, sin pulsar «Vista previa». Si algo falla, el motivo aparece junto al visor, sin ventanas.

## 3.40.0 — 2026-11-14

### Novedades
- **De 3 a 10 premios en la galería:** en los 24 diseños de la galería eliges cuántos premios lleva la rifa (de 3 a 10; antes eran 3 como máximo). A partir de 6 pasan a dos columnas. También en la app de Windows.

## 3.39.0 — 2026-11-13

### Novedades
- **App de Windows 2.7:** la galería y el editor de plantillas aceptan ahora latín extendido, vietnamita, griego, cirílico, chino, japonés y coreano, como el sitio desde la 3.37 (el hindi, el árabe y el hebreo siguen sin estar). Se descarga desde la página del Changelog.

## 3.38.0 — 2026-11-13

### Novedades
- **Botón «Compartir»:** en el pie y, tras generar los archivos, en la tarjeta de entrega. Abre una lista corta (compartir del móvil o del ordenador, WhatsApp, Telegram, Facebook, correo y «Copiar enlace») para dar a conocer el generador a otras asociaciones, colegios y comisiones de fiestas. Los enlaces llevan solo la dirección del sitio en el idioma en que está: sin rastreo y sin guardar nada. Tiene tema en el tutorial y vídeo.

## 3.37.0 — 2026-11-13

### Novedades
- **Más letras en la galería y en el editor de plantillas:** los textos pueden usar ahora latín extendido (polaco, checo, rumano, turco…), **vietnamita, griego, cirílico (ruso, ucraniano)**, **chino, japonés y coreano**. El hindi, el árabe y el hebreo siguen sin estar (necesitan una tecnología de escritura que el generador de PDF no tiene) y dan un aviso en vez de una imagen estropeada. En los PDF solo cambia el texto escrito por quien usa; lo que ya salía igual sigue igual.

## 3.36.0 — 2026-11-13

### Novedades
- **Guía «Cómo hacer» para parroquias:** «Para parroquias» (enlace en el pie), con el paso a paso para hacer una rifa para la parroquia: fiestas del patrón, verbenas, obras, cestas de Navidad y catequesis. Está en las 22 lenguas y recuerda consultar en el ayuntamiento si la rifa necesita licencia.

## 3.35.0 — 2026-11-13

### Novedades
- **App de Windows 2.6:** el menú «Extras» gana «Guardar pedido…» y «Abrir pedido…» (un archivo .rifas con los números, el nombre, las series, los colores y las marcas de corte, sin plantilla ni rutas), el editor de plantillas puede añadir imágenes (PNG o JPG) y «Ver → Visual» pasa de 2 a los 14 temas del sitio (solo los colores). Incluye también lo que llegó desde la 2.4: el editor, los 24 diseños de la galería y las 22 lenguas.

## 3.34.0 — 2026-11-13

### Novedades
- **Tres guías «Cómo hacer» nuevas:** «Para clubes», «Para bomberos» y «Para fiestas de barrio» (enlaces en el pie), con el paso a paso para hacer una rifa en cada caso. Están en las 22 lenguas y recuerdan consultar en el ayuntamiento si la rifa necesita licencia.

## 3.33.0 — 2026-11-13

### Novedades
- **API pública por lotes** (`/api/v1`, con Swagger en `/api/v1/docs`): permite que otros programas generen varios pedidos de rifas a partir de una sola plantilla, con clave, cuotas diarias y límites. Quien usa el sitio pasa siempre primero.
- **Cuatro idiomas nuevos:** catalán, ucraniano, indonesio y vietnamita. El sitio y la app de Windows pasan a tener 22 idiomas, con tutorial, términos, privacidad, guías «cómo hacerlo» y capturas.
- **Textos para los buscadores editables por idioma:** el dueño edita en el panel de administración los títulos, las descripciones y las guías de cada idioma, guardados en la base de datos y sin nuevo despliegue.

## 3.32.0 — 2026-11-13

### Novedades
- **20 plantillas nuevas en la galería (24 en total):** Páscoa, Carnaval, Santos Populares, Coração, Praia, Halloween, Magusto, Futebol, Escola, Festival, Solidária, Bombeiros, Retro, Minimalista, Vindima, Arraial, Tesouro, Primavera, Inverno, Cinema. Todas dibujadas desde cero para este proyecto, con talón, en el sitio y en la app de Windows (donde la galería pasa a ser una lista desplegable).

## 3.31.0 — 2026-11-13

### Novedades
- **Editor de plantillas v2:** deshacer y rehacer (Ctrl+Z, Ctrl+Y), duplicar (Ctrl+D), cambiar el orden de dibujo, añadir el logotipo (PNG o JPG) y **compartir el diseño por enlace**: se guarda 90 días desde el último acceso, sin imágenes y sin datos de quien comparte (solo aparece cuando el servicio tiene base de datos). La Política de privacidad lo dice.
- **App de Windows 2.5:** incorpora el editor de plantillas (menú Extras) y pasa a Python 3.15.

### Mejorado
- El Changelog tiene un enlace para descargar la app de Windows.

## 3.30.0 — 2026-11-12

### Novedades
- **Páginas «Cómo hacer»:** dos guías escritas, «Para colegios» y «Para asociaciones» (enlaces en el pie), con el paso a paso para hacer una rifa: diseñar el boleto, una serie por clase o vendedor, imprimir con marcas de corte, controlar las ventas y hacer un sorteo verificable. Están en las 18 lenguas y recuerdan consultar en el ayuntamiento si la rifa necesita licencia.

## 3.29.0 — 2026-11-12

### Mejorado
- **Anuncios en los laterales:** cuando los anuncios están activos (por ahora no lo están), en pantallas anchas aparecen a ambos lados del contenido, uno a cada lado, fijos y sin mover la página; en las demás pantallas queda un solo bloque al final de la página. Siguen sin aparecer en el editor, en los archivos generados ni en la app de Windows.

## 3.28.0 — 2026-11-12

### Novedades
- **Anuncios de Google (preparados, desactivados):** el sitio puede mostrar un bloque de anuncios de Google (AdSense) al final de la página de inicio, del tutorial, de «Acerca de», del sorteo y del changelog. Nunca aparecen en el editor, en los archivos generados, en la verificación de boletos, en el panel ni en la app de Windows, y en el Espacio Económico Europeo y el Reino Unido solo después de elegir en el mensaje de consentimiento de Google. La Política de privacidad lo dice, en las 18 lenguas, cuando los anuncios están activos; por ahora están desactivados hasta que el dueño del servicio los configure.

## 3.27.0 — 2026-11-12

### Novedades
- **Editor de plantillas:** en lugar de usar una plantilla de Canva, diseñe la rifa en el sitio (página «Editor de plantillas», enlazada desde el paso 1): añada textos, rectángulos, líneas y el número 0001 (una vez, o dos si tiene talón), arrastre cada elemento con el ratón o las flechas, cambie colores, tamaños y el fondo, y pulse «Usar esta plantilla». La pantalla usa la letra Vera, la misma del PDF, así que lo que ve es lo que sale; el borrador queda solo en el navegador. Los textos no pueden contener secuencias como 0123, que el programa confundiría con el número del boleto (la pantalla y el servidor avisan).

## 3.26.0 — 2026-11-12

### Novedades
- **Cinco temas nuevos:** Halloween, Playa, Periódico antiguo, Terminal verde y Cartel de circo, cada uno en claro y oscuro. El sitio pasa a tener 14 temas; la estructura es la misma en todos (solo cambian los colores y el aspecto).

## 3.25.0 — 2026-11-08

### Novedades
- **Una dirección por idioma para los buscadores:** cada idioma tiene su propia dirección (/en, /ja/tutorial…) con título, descripción y texto en ese idioma, y el sitio indica a Google qué versiones son equivalentes (hreflang). El portugués sigue en /. El idioma elegido aparece ahora en la barra de direcciones.

## 3.24.1 — 2026-11-08

### Mejorado
- **Casillas alineadas:** «Un color por serie» y las demás casillas quedan junto a su texto, no al otro extremo de la tarjeta.

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
