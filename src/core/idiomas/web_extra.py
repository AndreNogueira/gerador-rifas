"""Textos da interface web acrescentados depois da versao 3.9: uma chave de cada vez, com as 18 linguas lado a lado.

Cada chave tem de ter todas as linguas de `ORDEM` (um teste verifica-o). Juntam-se aos de `ui_<lingua>.py` em `TEXTOS` (ver
`__init__.py`). Os nomes dos temas e as paginas Changelog, Termos e Privacidade em si sao so em portugues; aqui ficam so as etiquetas.
Para acrescentar uma chave: um bloco novo em CHAVES (e subir as contagens em tests/test_i18n.py e tests/test_web_api.py).
"""
CHAVES: dict[str, dict[str, str]] = {
    "web_termos": {
        "pt": "Termos", "en": "Terms", "es": "Términos", "fr": "Conditions", "de": "Nutzungsbedingungen", "it": "Termini",
        "nl": "Voorwaarden", "pl": "Regulamin", "sv": "Villkor", "cs": "Podmínky", "ro": "Termeni", "el": "Όροι",
        "ru": "Условия", "tr": "Koşullar", "zh": "条款", "ja": "利用規約", "ko": "이용약관", "hi": "शर्तें",
    },
    "web_privacidade": {
        "pt": "Privacidade", "en": "Privacy", "es": "Privacidad", "fr": "Confidentialité", "de": "Datenschutz", "it": "Privacy",
        "nl": "Privacy", "pl": "Prywatność", "sv": "Integritet", "cs": "Soukromí", "ro": "Confidențialitate", "el": "Απόρρητο",
        "ru": "Конфиденциальность", "tr": "Gizlilik", "zh": "隐私", "ja": "プライバシー", "ko": "개인정보", "hi": "गोपनीयता",
    },
    "web_contacto": {
        "pt": "Contacto", "en": "Contact", "es": "Contacto", "fr": "Contact", "de": "Kontakt", "it": "Contatti",
        "nl": "Contact", "pl": "Kontakt", "sv": "Kontakt", "cs": "Kontakt", "ro": "Contact", "el": "Επικοινωνία",
        "ru": "Контакты", "tr": "İletişim", "zh": "联系", "ja": "お問い合わせ", "ko": "문의", "hi": "संपर्क",
    },
    "web_donativo": {
        "pt": "Donativo", "en": "Donate", "es": "Donar", "fr": "Faire un don", "de": "Spenden", "it": "Dona",
        "nl": "Doneren", "pl": "Wesprzyj", "sv": "Donera", "cs": "Přispět", "ro": "Donează", "el": "Δωρεά",
        "ru": "Пожертвовать", "tr": "Bağış yap", "zh": "捐赠", "ja": "寄付", "ko": "후원", "hi": "दान करें",
    },
}


def para(lingua: str) -> dict[str, str]:
    """As chaves desta lingua (as que faltarem aparecem como erro no teste, nunca em silencio)."""
    return {k: v[lingua] for k, v in CHAVES.items() if lingua in v}
