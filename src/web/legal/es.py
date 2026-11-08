"""Términos, privacidad y contacto en español: traducción de `pt.py` (mismas páginas, secciones, párrafos y {marcadores}). Sin revisión nativa; prevalece el portugués."""
FRASES = {
    "responsavel_com": "El servicio lo gestiona {nome}.",
    "responsavel_sem": "El servicio lo gestiona su autor, la persona que lo ofrece en línea.",
    "contacto_com": "Puede contactarnos en {email}.",
    "contacto_sem": "De momento no hay un contacto público.",
    "contacto_pagina_com": "Para dudas, errores o sugerencias, escriba a {email}.",
    "contacto_pagina_sem": "De momento no hay un contacto público. Vuelva a esta página más tarde.",
    "atualizado": "8 de noviembre de 2026",
}

AVISO = ("Versión provisional, pendiente de revisión con apoyo jurídico. Si algo de aquí difiere de lo que hace el servicio, pídanos que lo corrijamos. "
         "Es una traducción sin revisión nativa: si las versiones difieren, prevalece la portuguesa.")

TEXTOS = {
    "termos": {
        "titulo": "Términos de uso",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Qué es este servicio",
             "paragrafos": ["El Generador de Rifas crea, a partir de una plantilla en PDF, los boletos numerados de una rifa listos para imprimir. Solo hace eso: no vende boletos, "
                            "no recibe dinero, no guarda listas de participantes y no realiza sorteos con valor legal.",
                            "{responsavel}"]},
            {"titulo": "Quien organiza la rifa es responsable de ella",
             "paragrafos": ["Las rifas, tómbolas y sorteos están sujetos a normas legales (por ejemplo, licencias del ayuntamiento y reglas para asociaciones) que varían según el caso. "
                            "Quien organiza la rifa es el único responsable de cumplir la ley, de cobrar y de entregar los premios. Este servicio no da asesoramiento jurídico."]},
            {"titulo": "Uso permitido",
             "paragrafos": ["El servicio es gratuito y para uso razonable. No puede usarse para generar boletos de fraudes ni para sobrecargar el servidor: hay límites de tamaño de los archivos, "
                            "de números por pedido ({max_numeros}) y de pedidos por minuto, y una generación cada vez."]},
            {"titulo": "Sus archivos",
             "paragrafos": ["La plantilla y los dígitos sirven solo para generar sus rifas y se borran del servidor pasados {validade} minutos sin actividad, o al pulsar «Borrar todo». "
                            "No los usamos para nada más. Siguen siendo suyos: solo debe tener derecho a usar lo que sube (imágenes, letras, logotipos)."]},
            {"titulo": "Sin garantías",
             "paragrafos": ["El servicio se ofrece «tal cual», sin garantía de que esté siempre disponible o libre de errores. Compruebe siempre los PDF antes de imprimir (el servicio verifica "
                            "los números generados, pero la comprobación final es suya). En la medida que permita la ley, no respondemos por pérdidas ligadas al uso del servicio."]},
            {"titulo": "Cambios",
             "paragrafos": ["Estos términos pueden cambiar; la fecha de la última actualización es {atualizado}. Si algún día el servicio pasa a ser de pago, se dirá con claridad antes de cobrar."]},
            {"titulo": "Contacto", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Política de privacidad",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Resumen",
             "paragrafos": ["No hay cuentas, ni anuncios, ni herramientas de seguimiento de terceros. Sus archivos se borran del servidor en {validade} minutos. "
                            "Las estadísticas de uso son solo números agregados."]},
            {"titulo": "Qué datos tratamos",
             "paragrafos": ["Los archivos que sube (plantilla y dígitos) se tratan solo para generar las rifas, quedan en una carpeta temporal del servidor y se borran pasados {validade} minutos "
                            "sin actividad o al pulsar «Borrar todo».",
                            "Para saber cómo se usa el servicio registramos recuentos: cuántas visitas, generaciones y descargas, el idioma y el tema elegidos y el tipo de pantalla. "
                            "Nunca registramos direcciones IP, nombres de archivos, el contenido de los archivos ni la identificación completa del navegador.",
                            "La dirección IP se usa solo en memoria, unos instantes, para limitar el número de pedidos por minuto, y no la guardamos. El proveedor de alojamiento "
                            "(Render, en Fráncfort, Unión Europea) puede registrar direcciones IP en sus registros técnicos."]},
            {"titulo": "En su navegador",
             "paragrafos": ["Guardamos en su navegador (almacenamiento local) sus preferencias: el idioma, el tema visual, el modo claro u oscuro y los últimos valores del formulario. "
                            "Para no repetir el trabajo de un año a otro, el archivo de dígitos también puede quedar guardado en su navegador (nunca en nuestro servidor); «Borrar todo» lo elimina. "
                            "No usamos cookies de publicidad ni de seguimiento."]},
            {"titulo": "Base legal y conservación",
             "paragrafos": ["Tratamos estos datos por interés legítimo en prestar el servicio y mantenerlo seguro (RGPD, artículo 6.1.f). Los archivos duran minutos; "
                            "los recuentos agregados no identifican a nadie."]},
            {"titulo": "Sus derechos",
             "paragrafos": ["Tiene derecho de acceso, rectificación, supresión y oposición, y a presentar una reclamación ante su autoridad de protección de datos (en Portugal, la CNPD, cnpd.pt). "
                            "Como no guardamos datos que lo identifiquen, en la práctica hay poco que consultar o borrar; si tiene dudas, hable con nosotros."]},
            {"titulo": "Quién responde", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Actualización", "paragrafos": ["Última actualización: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Contacto",
        "aviso": "",
        "seccoes": [
            {"titulo": "Hable con nosotros",
             "paragrafos": ["{contacto_pagina}",
                            "Si encuentra un error, díganos qué hizo y qué esperaba; no envíe su plantilla si contiene datos personales."]},
        ],
    },
}
