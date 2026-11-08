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
    "web_algarismos_lembrados": {
        "pt": "Reutilizámos os algarismos da última vez ({nome}). Escolha outro ficheiro para os trocar.",
        "en": "Reused the digits file from last time ({nome}). Choose another file to replace it.",
        "es": "Hemos reutilizado el archivo de dígitos de la última vez ({nome}). Elija otro para cambiarlo.",
        "fr": "Fichier des chiffres de la dernière fois réutilisé ({nome}). Choisissez-en un autre pour le remplacer.",
        "de": "Die Ziffern-Datei vom letzten Mal wird wiederverwendet ({nome}). Wählen Sie eine andere Datei, um sie zu ersetzen.",
        "it": "Abbiamo riutilizzato il file delle cifre dell'ultima volta ({nome}). Scegline un altro per sostituirlo.",
        "nl": "Het cijferbestand van de vorige keer is hergebruikt ({nome}). Kies een ander bestand om het te vervangen.",
        "pl": "Użyto ponownie pliku z cyframi z ostatniego razu ({nome}). Wybierz inny plik, aby go zastąpić.",
        "sv": "Siffrorna från förra gången används igen ({nome}). Välj en annan fil för att byta.",
        "cs": "Znovu jsme použili soubor s číslicemi z minula ({nome}). Chcete-li jej změnit, vyberte jiný soubor.",
        "ro": "Am refolosit fișierul cu cifre de data trecută ({nome}). Alegeți alt fișier pentru a-l schimba.",
        "el": "Χρησιμοποιήθηκε ξανά το αρχείο ψηφίων της προηγούμενης φοράς ({nome}). Επιλέξτε άλλο για να το αλλάξετε.",
        "ru": "Использован файл с цифрами с прошлого раза ({nome}). Выберите другой файл, чтобы заменить его.",
        "tr": "Geçen seferki rakam dosyası yeniden kullanıldı ({nome}). Değiştirmek için başka bir dosya seçin.",
        "zh": "已重用上次的数字文件（{nome}）。如需更换，请选择其他文件。",
        "ja": "前回の数字ファイルを再利用しました（{nome}）。変更するには別のファイルを選んでください。",
        "ko": "지난번 숫자 파일을 다시 사용했습니다({nome}). 바꾸려면 다른 파일을 선택하세요.",
        "hi": "पिछली बार की अंकों वाली फ़ाइल दोबारा उपयोग की गई ({nome})। बदलने के लिए दूसरी फ़ाइल चुनें।",
    },
    "web_copiar_ligacao": {
        "pt": "Copiar ligação", "en": "Copy link", "es": "Copiar enlace", "fr": "Copier le lien", "de": "Link kopieren",
        "it": "Copia link", "nl": "Link kopiëren", "pl": "Kopiuj link", "sv": "Kopiera länk", "cs": "Kopírovat odkaz",
        "ro": "Copiază linkul", "el": "Αντιγραφή συνδέσμου", "ru": "Копировать ссылку", "tr": "Bağlantıyı kopyala",
        "zh": "复制链接", "ja": "リンクをコピー", "ko": "링크 복사", "hi": "लिंक कॉपी करें",
    },
    "web_ligacao_copiada": {
        "pt": "Ligação copiada. Quem a abrir vê os mesmos valores (os ficheiros não vão na ligação).",
        "en": "Link copied. Anyone who opens it sees the same values (files are not included).",
        "es": "Enlace copiado. Quien lo abra verá los mismos valores (los archivos no se incluyen).",
        "fr": "Lien copié. Quiconque l'ouvre voit les mêmes valeurs (les fichiers ne sont pas inclus).",
        "de": "Link kopiert. Wer ihn öffnet, sieht dieselben Werte (Dateien sind nicht enthalten).",
        "it": "Link copiato. Chi lo apre vede gli stessi valori (i file non sono inclusi).",
        "nl": "Link gekopieerd. Wie hem opent, ziet dezelfde waarden (bestanden zitten er niet in).",
        "pl": "Link skopiowany. Każdy, kto go otworzy, zobaczy te same wartości (pliki nie są dołączone).",
        "sv": "Länken är kopierad. Den som öppnar den ser samma värden (filer ingår inte).",
        "cs": "Odkaz zkopírován. Kdo jej otevře, uvidí stejné hodnoty (soubory v něm nejsou).",
        "ro": "Link copiat. Cine îl deschide vede aceleași valori (fișierele nu sunt incluse).",
        "el": "Ο σύνδεσμος αντιγράφηκε. Όποιος τον ανοίξει βλέπει τις ίδιες τιμές (τα αρχεία δεν περιλαμβάνονται).",
        "ru": "Ссылка скопирована. Тот, кто её откроет, увидит те же значения (файлы в неё не входят).",
        "tr": "Bağlantı kopyalandı. Açan kişi aynı değerleri görür (dosyalar dahil değildir).",
        "zh": "链接已复制。打开它的人会看到相同的数值（不包含文件）。",
        "ja": "リンクをコピーしました。開いた人にも同じ値が表示されます（ファイルは含まれません）。",
        "ko": "링크를 복사했습니다. 열어 보는 사람에게도 같은 값이 표시됩니다(파일은 포함되지 않음).",
        "hi": "लिंक कॉपी हो गया। जो इसे खोलेगा उसे वही मान दिखेंगे (फ़ाइलें शामिल नहीं हैं)।",
    },
}


def para(lingua: str) -> dict[str, str]:
    """As chaves desta lingua (as que faltarem aparecem como erro no teste, nunca em silencio)."""
    return {k: v[lingua] for k, v in CHAVES.items() if lingua in v}
