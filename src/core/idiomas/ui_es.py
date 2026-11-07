T = {
    "m_ficheiro": "Archivo", "m_ver": "Ver", "m_idioma": "Idioma", "m_ajuda": "Ayuda",
    "mi_abrir_template": "Abrir plantilla…", "mi_abrir_alg": "Elegir archivo de dígitos…",
    "mi_destino": "Elegir carpeta de destino…", "mi_sair": "Salir",
    "mi_zoom_mais": "Acercar", "mi_zoom_menos": "Alejar", "mi_ajustar": "Ajustar a la ventana",
    "mi_expandir": "Ampliar la vista previa", "mi_reduzir": "Reducir la vista previa",
    "mi_tema": "Tema", "mi_tema_sistema": "Igual que Windows", "mi_tema_claro": "Claro", "mi_tema_escuro": "Oscuro",
    "mi_tutorial": "Tutorial paso a paso", "mi_sobre": "Acerca de…",
    "sobre_texto": ("{app}\nVersión {versao}\n\nCrea PDF de rifas numeradas a partir de una plantilla de Canva.\n\n"
                    "Usa las bibliotecas pypdf, pypdfium2, Pillow y CustomTkinter (licencias permisivas)."),
    "tip_tema": "Cambiar entre tema claro y oscuro",
    "tut_titulo": "Tutorial", "tut_ant": "Anterior", "tut_seg": "Siguiente",
    "tut_t0": "Resumen",
    "tut_b0": ("Este programa toma su diseño de rifa hecho en Canva y crea PDF listos para imprimir con los números "
               "que quiera.\n\n"
               "Solo hay 4 pasos, en el orden en que aparecen a la izquierda:\n\n"
               "• 1 – elija la plantilla (el PDF de Canva);\n"
               "• 2 – elija el archivo con los dígitos del 0 al 9;\n"
               "• 3 – indique desde qué número hasta cuál, y si quiere varios PDF o uno solo;\n"
               "• 4 – elija la carpeta y escriba el nombre de los archivos.\n\n"
               "Después pulse «{previa}» para ver una página y «{gerar}». Al final cada PDF se verifica "
               "automáticamente."),
    "tut_b1": ("En Canva, diseñe la rifa y escriba en cada boleto los números de ejemplo 0001, 0002, 0003, … "
               "(uno por boleto). Cada número aparece 2 veces: una en el talón y otra en la parte principal del "
               "boleto (como muestra la imagen).\n\n"
               "Descárguelo en PDF y elija ese archivo en el paso 1.\n\n"
               "• El programa detecta solo cuántos boletos hay por página y la orientación del texto del talón.\n"
               "• Los números deben ser texto, no imagen.\n"
               "• Otros números del diseño (año, teléfono…) se dejan como están.\n"
               "• Solo se usa la 1.ª página del PDF."),
    "tut_b3": ("• {de} / {ate}: el primer y el último número que generar (por ejemplo del 1 al 1000).\n"
               "• {algarismos}: con cuántos dígitos escribir (4 → 0001). Por defecto es el del diseño de la "
               "plantilla; si pide más, el tamaño de los números se reduce para que quepan.\n"
               "• {varios}: divide en archivos con el máximo de números que indique (múltiplo de los boletos "
               "por página).\n"
               "• {unico}: todo en un solo archivo.\n\n"
               "Abajo ve el resumen: cuántos números, archivos y páginas se van a generar."),
    "tut_b4": ("Elija la carpeta donde guardar los PDF y escriba el nombre de los archivos (obligatorio; el programa "
               "nunca sugiere uno). Los archivos quedan «NOMBRE - 0001 - 0300.pdf», «NOMBRE - 0301 - 0600.pdf», … "
               "o solo «NOMBRE - 0001 - 1000.pdf» si elige un único PDF.\n\n"
               "Si ya existen archivos con esos nombres, el programa pregunta antes de reemplazarlos."),
    "tut_t5": "Vista previa y generar",
    "tut_b5": ("«{previa}» muestra la 1.ª página con números reales, para comprobar la letra, el tamaño y la "
               "posición antes de generarlo todo.\n\n"
               "En el visor:\n"
               "• − / + o Ctrl + rueda del ratón: zoom;\n"
               "• arrastre para mover; doble clic o «{ajustar}»: ver la hoja entera;\n"
               "• el botón de ampliar da toda la ventana a la vista previa; púlselo otra vez para volver;\n"
               "• la divisoria entre los ajustes y el visor también se puede arrastrar.\n\n"
               "Pulse «{gerar}». La barra muestra el progreso (puede cancelar). Al final cada PDF se verifica "
               "automáticamente (páginas y números) y aparece el botón «{pasta}»."),
    "tut_t6": "Consejos y problemas",
    "tut_b6": ("• «No encontré los números de ejemplo»: en Canva los números deben ser texto, con el formato "
               "0001, 0002, … (cada uno 2 veces).\n"
               "• Los números salen con otra letra: el archivo de dígitos debe usar exactamente la misma letra que "
               "la plantilla. Compruébelo en la vista previa.\n"
               "• Números pequeños o raros: con PNG/JPG use una imagen grande (≥ 100 px de alto); el PDF siempre es mejor.\n"
               "• «No pude guardar»: cierre el PDF si está abierto en otro programa.\n"
               "• Más dígitos que el diseño: el tamaño se reduce automáticamente (aviso en el registro).\n"
               "• Puede cambiar el idioma y el tema (claro/oscuro) en los menús; los colores siguen a Windows."),
    'err_folha_varias': 'Solo se puede repetir en la hoja un template con un único boleto.',
    'err_rifa_grande': 'El boleto ({w} × {h} mm) no cabe en una hoja {papel} con márgenes de {margem} mm.\n\nElija un papel más grande, reduzca el margen o diseñe un boleto más pequeño.',
    'log_folha': 'Hoja {papel}: {n} boletos por hoja ({w} × {h} mm cada uno).',
    'aviso_muitas': '⚠ {n} boletos por hoja: quedan muy pequeños y difíciles de recortar. Revise el tamaño del boleto.',
    'c1_ok_uma': '✔ Template con 1 boleto · número de ejemplo {primeiro}',
    'lay_info': 'El template tiene un solo boleto: el programa llena la hoja con copias, todas las que quepan.',
    'lay_papel': 'Papel',
    'lay_margem': 'Margen (mm)',
    'lay_por_folha': 'Boletos por hoja',
    'lay_resultado': 'Boleto de {w} × {h} mm → {n} por hoja {papel} (máximo {max})',
    'lay_recortada': ' · recortado al diseño',
    'lay_rodadas': ' · {r} girados 90°',
    'lay_acima': 'Solo caben {max} por hoja.',
    'conf_muitas': 'Va a generar {n} boletos por hoja ({w} × {h} mm cada uno). Es un valor muy alto: quedan pequeños y difíciles de recortar.\n\n¿Continuar?',
    'mi_video': 'Vídeo tutorial',
    'video_falta': 'No encontré el vídeo ({nome}).',
    'tut_t_uma': 'Un solo boleto en el template',
    'tut_b_uma': 'No hace falta diseñar toda la hoja. En Canva, cree una página del tamaño de un boleto («Tamaño personalizado», por ejemplo 19 × 5,5 cm) y escriba un solo número de ejemplo, 0001 (en la matriz y en la parte principal, o solo en un sitio).\n\nAl elegir ese PDF, el programa ve que hay un solo boleto y muestra «{papel}», «{margem}» y «{porfolha}»: llena la hoja con copias del boleto, todas las que quepan (las gira 90° si así caben más), y las numera en orden. La vista previa muestra la hoja tal como saldrá.\n\n• Se pueden cambiar el papel (A4, A3, A5, Letter, Legal) y el margen (las impresoras no imprimen hasta el borde).\n• Si la página del PDF es mayor que el boleto, el programa recorta la zona dibujada.\n• «{porfolha}» empieza en el máximo; puede pedir menos.\n• Si caben muchos boletos (más de 24), el programa avisa: quedan pequeños y difíciles de recortar.\n• Si su PDF ya tiene varios boletos por página (0001, 0002, …), todo funciona como antes.',
    'tut_video': '¿Prefiere verlo en vídeo? Abra el menú «{ajuda}» › «{video}».',
    'limpar': 'Limpiar todo',
    'tut_limpar': 'Al terminar, «{limpar}» (o menú «{ficheiro}» › «{limpar}») lo deja todo limpio — template, dígitos, carpeta, nombre, números y vista previa — para empezar otra rifa.',
}

# --- interface web (src/web)
T.update({
    'web_descarregar': 'Descargar',
    'web_senha': 'Contraseña',
    'web_entrar': 'Entrar',
    'web_senha_errada': 'Contraseña incorrecta.',
    'web_demasiado_grande': 'El archivo supera el límite ({mb} MB).',
    'web_ocupado': 'Ya hay una generación en curso. Inténtelo de nuevo en un momento.',
    'web_voltar': 'Volver',
    'web_ficheiros_gerados': 'PDF generados',
    'web_nova_janela': 'Abrir en una ventana nueva',
    'web_tema_auto': 'Automático',
})
T.update({'web_demasiados': 'Como máximo {max} números por pedido.'})
