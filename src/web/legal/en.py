"""Terms, privacy and contact in English: a translation of `pt.py` (same pages, sections, paragraphs and {placeholders}). No native review; the Portuguese prevails."""
FRASES = {
    "responsavel_com": "The service is run by {nome}.",
    "responsavel_sem": "The service is run by its author, the person who makes it available online.",
    "contacto_com": "You can contact us at {email}.",
    "contacto_sem": "There is no public contact at the moment.",
    "contacto_pagina_com": "For questions, errors or suggestions, write to {email}.",
    "contacto_pagina_sem": "There is no public contact at the moment. Please come back to this page later.",
    "atualizado": "November 8, 2026",
}

AVISO = ("Provisional version, to be reviewed with legal support. If anything here differs from what the service does, please ask us to correct it. "
         "This is a translation without native review: if the versions differ, the Portuguese one prevails.")

TEXTOS = {
    "termos": {
        "titulo": "Terms of use",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "What this service is",
             "paragrafos": ["The Raffle Generator creates, from a PDF template, numbered raffle tickets ready to print. That is all it does: it does not sell tickets, "
                            "receive money, keep lists of participants or run draws with legal value.",
                            "{responsavel}"]},
            {"titulo": "Whoever organizes the raffle is responsible for it",
             "paragrafos": ["Raffles, tombolas and draws are subject to legal rules (for example, licenses from the town council and rules for associations) that vary "
                            "from case to case. Whoever organizes the raffle is solely responsible for obeying the law, for collecting payments and for handing over "
                            "the prizes. This service does not give legal advice."]},
            {"titulo": "Permitted use",
             "paragrafos": ["The service is free and for reasonable use. It may not be used to produce tickets for frauds or to overload the server: there are limits on file "
                            "size, on numbers per request ({max_numeros}) and on requests per minute, and only one generation at a time."]},
            {"titulo": "Your files",
             "paragrafos": ["The template and the digits are used only to generate your tickets and are deleted from the server after {validade} minutes without activity, "
                            "or when you press “Clear everything”. We use them for nothing else. They remain yours: you only need the right to use what you upload "
                            "(images, fonts, logos)."]},
            {"titulo": "No warranties",
             "paragrafos": ["The service is provided “as is”, with no guarantee that it is always available or error-free. Always check the PDFs before printing (the service "
                            "verifies the generated numbers, but the final check is yours). To the extent allowed by law, we are not liable for losses linked to using the service."]},
            {"titulo": "Changes",
             "paragrafos": ["These terms may change; the date of the last update is {atualizado}. If the service ever becomes paid, this will be stated clearly before charging."]},
            {"titulo": "Contact", "paragrafos": ["{contacto}"]},
        ],
    },
    "privacidade": {
        "titulo": "Privacy policy",
        "aviso": AVISO,
        "seccoes": [
            {"titulo": "Summary",
             "paragrafos": ["There are no accounts, no ads and no third-party tracking tools. Your files are deleted from the server within {validade} minutes. "
                            "Usage statistics are aggregate numbers only."]},
            {"titulo": "What data we process",
             "paragrafos": ["The files you upload (template and digits) are processed only to generate the tickets, stay in a temporary folder on the server and are deleted "
                            "after {validade} minutes without activity or when you press “Clear everything”.",
                            "To know how the service is used, we record counts: how many visits, generations and downloads, the language and theme chosen and the screen type. "
                            "We also record the visit's country (only the code, for example “PT”), which the hosting network deduces from the IP address; we do not keep the IP itself. We never record IP addresses, file names, file contents or the full browser identification.",
                            "The IP address is used only in memory, for moments, to limit the number of requests per minute, and is not stored by us. The hosting provider "
                            "(Render, in Frankfurt, European Union) may record IP addresses in its technical logs."]},
            {"titulo": "In your browser",
             "paragrafos": ["We store your preferences in your browser (local storage): the language, the visual theme, light or dark mode and the last form values. So you do not "
                            "repeat the work from one year to the next, the digits file may also be kept in your browser (never on our server); “Clear everything” erases it. "
                            "We use no advertising or tracking cookies."]},
            {"titulo": "Legal basis and retention",
             "paragrafos": ["We process this data on the basis of our legitimate interest in providing the service and keeping it secure (GDPR, Article 6(1)(f)). "
                            "Files last minutes; the aggregate counts identify no one."]},
            {"titulo": "Your rights",
             "paragrafos": ["You have the right of access, rectification, erasure and objection, and to lodge a complaint with your data protection authority (in Portugal, the "
                            "CNPD, cnpd.pt). As we keep no data that identifies you, in practice there is little to access or erase; if in doubt, talk to us."]},
            {"titulo": "Who is responsible", "paragrafos": ["{responsavel}", "{contacto}"]},
            {"titulo": "Update", "paragrafos": ["Last updated: {atualizado}."]},
        ],
    },
    "contacto": {
        "titulo": "Contact",
        "aviso": "",
        "seccoes": [
            {"titulo": "Get in touch",
             "paragrafos": ["{contacto_pagina}",
                            "If you find an error, tell us what you did and what you expected; do not send your template if it contains personal data."]},
        ],
    },
}
