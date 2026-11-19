"""O que a Política de privacidade diz sobre os comentários dos visitantes e os problemas reportados (`opiniao.py`, `github_issues.py`).

`textos_legais` acrescenta, no fim da página, uma secção «Comentários e problemas reportados»: o que fica guardado (texto, data, nome a mostrar e
o endereço IP, que só o dono vê e se apaga do comentário aos 90 dias), o que se vê em público (nunca o IP) e o que vai para o GitHub (nunca o IP).
Um texto por língua (provisório como os restantes: sem revisão nativa nem jurídica; em caso de divergência vale o português).
"""
from __future__ import annotations

TEXTOS: dict[str, dict] = {
    "pt": {"titulo": "Comentários e problemas reportados", "paragrafos": [
        "Se deixar um comentário na página «Comentários», guardamos o texto, a data e o nome que escolher mostrar (nenhum, se preferir ficar anónimo(a); se pedir para mostrar um nome e não o escrever, aparece «Visitante n.º …»). O comentário fica visível para todos, sem o seu endereço IP. Guardamos também o seu endereço IP, que só o responsável do site vê, apenas para travar abusos: é apagado do comentário ao fim de 90 dias. Não escreva dados pessoais no comentário; se quiser que um comentário seja apagado, escreva-nos (ver Contacto).",
        "Se reportar um problema, o texto que escrever (e, se marcar essa opção, a versão da aplicação, a língua, o navegador e o ecrã) é enviado para o GitHub do projeto, onde fica registado e visível para a equipa. O seu endereço IP não é enviado. Não escreva dados pessoais nem palavras-passe.",
    ]},
    "en": {"titulo": "Comments and reported problems", "paragrafos": [
        "If you leave a comment on the “Comments” page, we store the text, the date and the name you choose to show (none, if you prefer to stay anonymous; if you ask to show a name but leave it blank, “Visitor no. …” appears). The comment is visible to everyone, without your IP address. We also store your IP address, which only the site owner can see, solely to stop abuse: it is deleted from the comment after 90 days. Do not write personal data in the comment; if you want a comment deleted, write to us (see Contact).",
        "If you report a problem, the text you write (and, if you tick that option, the app version, language, browser and screen) is sent to the project's GitHub, where it is recorded and visible to the team. Your IP address is not sent. Do not write personal data or passwords.",
    ]},
    "es": {"titulo": "Comentarios y problemas informados", "paragrafos": [
        "Si deja un comentario en la página «Comentarios», guardamos el texto, la fecha y el nombre que elija mostrar (ninguno, si prefiere permanecer anónimo/a; si pide mostrar un nombre y no lo escribe, aparece «Visitante n.º …»). El comentario es visible para todos, sin su dirección IP. También guardamos su dirección IP, que solo ve el responsable del sitio, únicamente para frenar abusos: se borra del comentario a los 90 días. No escriba datos personales en el comentario; si quiere que se borre, escríbanos (vea Contacto).",
        "Si informa de un problema, el texto que escriba (y, si marca esa opción, la versión de la aplicación, el idioma, el navegador y la pantalla) se envía al GitHub del proyecto, donde queda registrado y visible para el equipo. Su dirección IP no se envía. No escriba datos personales ni contraseñas.",
    ]},
    "fr": {"titulo": "Commentaires et problèmes signalés", "paragrafos": [
        "Si vous laissez un commentaire sur la page « Commentaires », nous conservons le texte, la date et le nom que vous choisissez d'afficher (aucun, si vous préférez rester anonyme ; si vous demandez d'afficher un nom sans l'écrire, « Visiteur n° … » apparaît). Le commentaire est visible par tous, sans votre adresse IP. Nous conservons aussi votre adresse IP, que seul le responsable du site voit, uniquement pour limiter les abus : elle est supprimée du commentaire au bout de 90 jours. N'écrivez pas de données personnelles dans le commentaire ; pour le faire supprimer, écrivez-nous (voir Contact).",
        "Si vous signalez un problème, le texte que vous écrivez (et, si vous cochez cette option, la version de l'application, la langue, le navigateur et l'écran) est envoyé au GitHub du projet, où il est enregistré et visible par l'équipe. Votre adresse IP n'est pas envoyée. N'écrivez ni données personnelles ni mots de passe.",
    ]},
    "de": {"titulo": "Kommentare und gemeldete Probleme", "paragrafos": [
        "Wenn Sie auf der Seite „Kommentare“ einen Kommentar hinterlassen, speichern wir den Text, das Datum und den Namen, den Sie anzeigen möchten (keinen, wenn Sie anonym bleiben wollen; wählen Sie einen Namen, lassen ihn aber leer, erscheint „Besucher Nr. …“). Der Kommentar ist für alle sichtbar, ohne Ihre IP-Adresse. Wir speichern außerdem Ihre IP-Adresse, die nur der Betreiber sieht, ausschließlich zur Missbrauchsabwehr: Sie wird nach 90 Tagen aus dem Kommentar gelöscht. Schreiben Sie keine persönlichen Daten in den Kommentar; zum Löschen schreiben Sie uns (siehe Kontakt).",
        "Wenn Sie ein Problem melden, wird der von Ihnen geschriebene Text (und, wenn Sie die Option anhaken, Version der Anwendung, Sprache, Browser und Bildschirm) an das GitHub des Projekts gesendet, wo er erfasst und für das Team sichtbar ist. Ihre IP-Adresse wird nicht gesendet. Schreiben Sie keine persönlichen Daten oder Passwörter.",
    ]},
    "it": {"titulo": "Commenti e problemi segnalati", "paragrafos": [
        "Se lascia un commento nella pagina «Commenti», conserviamo il testo, la data e il nome che sceglie di mostrare (nessuno, se preferisce restare anonimo/a; se chiede di mostrare un nome e non lo scrive, compare «Visitatore n. …»). Il commento è visibile a tutti, senza il suo indirizzo IP. Conserviamo anche il suo indirizzo IP, che vede solo il responsabile del sito, unicamente per limitare gli abusi: viene eliminato dal commento dopo 90 giorni. Non scriva dati personali nel commento; per farlo eliminare ci scriva (vedi Contatti).",
        "Se segnala un problema, il testo che scrive (e, se seleziona l'opzione, versione dell'app, lingua, browser e schermo) viene inviato al GitHub del progetto, dove è registrato e visibile al team. Il suo indirizzo IP non viene inviato. Non scriva dati personali né password.",
    ]},
    "nl": {"titulo": "Reacties en gemelde problemen", "paragrafos": [
        "Als u een reactie achterlaat op de pagina ‘Reacties’, bewaren we de tekst, de datum en de naam die u wilt tonen (geen, als u anoniem wilt blijven; vraagt u om een naam te tonen maar laat u hem leeg, dan staat er ‘Bezoeker nr. …’). De reactie is voor iedereen zichtbaar, zonder uw IP-adres. We bewaren ook uw IP-adres, dat alleen de beheerder ziet, uitsluitend tegen misbruik: het wordt na 90 dagen uit de reactie verwijderd. Schrijf geen persoonsgegevens in de reactie; wilt u haar laten verwijderen, schrijf ons (zie Contact).",
        "Als u een probleem meldt, wordt de tekst die u schrijft (en, als u die optie aanvinkt, de appversie, taal, browser en scherm) naar de GitHub van het project gestuurd, waar hij wordt vastgelegd en zichtbaar is voor het team. Uw IP-adres wordt niet verstuurd. Schrijf geen persoonsgegevens of wachtwoorden.",
    ]},
    "pl": {"titulo": "Komentarze i zgłoszone problemy", "paragrafos": [
        "Jeśli zostawisz komentarz na stronie „Komentarze”, przechowujemy tekst, datę i imię, które wybierzesz do wyświetlenia (żadne, jeśli wolisz pozostać anonimowy; jeśli poprosisz o pokazanie imienia, ale go nie wpiszesz, pojawi się „Gość nr …”). Komentarz jest widoczny dla wszystkich, bez twojego adresu IP. Przechowujemy też twój adres IP, który widzi tylko administrator serwisu, wyłącznie po to, by ograniczać nadużycia: po 90 dniach jest usuwany z komentarza. Nie wpisuj w komentarzu danych osobowych; aby usunąć komentarz, napisz do nas (zob. Kontakt).",
        "Jeśli zgłosisz problem, wpisany tekst (oraz, jeśli zaznaczysz tę opcję, wersja aplikacji, język, przeglądarka i ekran) jest wysyłany do GitHuba projektu, gdzie zostaje zapisany i widoczny dla zespołu. Twój adres IP nie jest wysyłany. Nie wpisuj danych osobowych ani haseł.",
    ]},
    "sv": {"titulo": "Kommentarer och rapporterade problem", "paragrafos": [
        "Om du lämnar en kommentar på sidan ”Kommentarer” sparar vi texten, datumet och det namn du väljer att visa (inget, om du vill vara anonym; ber du om att visa ett namn men lämnar det tomt visas ”Besökare nr …”). Kommentaren är synlig för alla, utan din IP-adress. Vi sparar också din IP-adress, som bara webbplatsens ansvarige ser, uteslutande för att stoppa missbruk: den raderas från kommentaren efter 90 dagar. Skriv inga personuppgifter i kommentaren; vill du att den raderas, skriv till oss (se Kontakt).",
        "Om du rapporterar ett problem skickas texten du skriver (och, om du kryssar i alternativet, appens version, språk, webbläsare och skärm) till projektets GitHub, där den registreras och syns för teamet. Din IP-adress skickas inte. Skriv inga personuppgifter eller lösenord.",
    ]},
    "cs": {"titulo": "Komentáře a nahlášené problémy", "paragrafos": [
        "Pokud zanecháte komentář na stránce „Komentáře“, uložíme text, datum a jméno, které se rozhodnete zobrazit (žádné, chcete-li zůstat anonymní; požádáte-li o zobrazení jména a nevyplníte ho, zobrazí se „Návštěvník č. …“). Komentář je viditelný všem, bez vaší IP adresy. Ukládáme také vaši IP adresu, kterou vidí jen provozovatel webu, výhradně proti zneužití: z komentáře se maže po 90 dnech. Nepište do komentáře osobní údaje; chcete-li jej smazat, napište nám (viz Kontakt).",
        "Nahlásíte-li problém, text, který napíšete (a, zaškrtnete-li tuto volbu, verze aplikace, jazyk, prohlížeč a obrazovka), se odešle na GitHub projektu, kde je zaznamenán a viditelný pro tým. Vaše IP adresa se neodesílá. Nepište osobní údaje ani hesla.",
    ]},
    "ro": {"titulo": "Comentarii și probleme raportate", "paragrafos": [
        "Dacă lași un comentariu pe pagina „Comentarii”, păstrăm textul, data și numele pe care alegi să-l afișezi (niciunul, dacă preferi să rămâi anonim; dacă ceri să apară un nume și nu-l scrii, apare „Vizitator nr. …”). Comentariul este vizibil pentru toți, fără adresa ta IP. Păstrăm și adresa ta IP, pe care o vede doar responsabilul site-ului, exclusiv pentru a opri abuzurile: se șterge din comentariu după 90 de zile. Nu scrie date personale în comentariu; dacă vrei să fie șters, scrie-ne (vezi Contact).",
        "Dacă raportezi o problemă, textul scris (și, dacă bifezi opțiunea, versiunea aplicației, limba, browserul și ecranul) este trimis către GitHub-ul proiectului, unde este înregistrat și vizibil pentru echipă. Adresa ta IP nu este trimisă. Nu scrie date personale sau parole.",
    ]},
    "el": {"titulo": "Σχόλια και αναφορές προβλημάτων", "paragrafos": [
        "Αν αφήσετε ένα σχόλιο στη σελίδα «Σχόλια», φυλάσσουμε το κείμενο, την ημερομηνία και το όνομα που επιλέγετε να εμφανίζεται (κανένα, αν προτιμάτε να μείνετε ανώνυμοι· αν ζητήσετε να εμφανιστεί όνομα και δεν το γράψετε, εμφανίζεται «Επισκέπτης αρ. …»). Το σχόλιο είναι ορατό σε όλους, χωρίς τη διεύθυνση IP σας. Φυλάσσουμε επίσης τη διεύθυνση IP σας, που τη βλέπει μόνο ο υπεύθυνος του ιστότοπου, αποκλειστικά για την αποτροπή κατάχρησης: διαγράφεται από το σχόλιο μετά από 90 ημέρες. Μη γράφετε προσωπικά δεδομένα στο σχόλιο· για διαγραφή, γράψτε μας (βλ. Επικοινωνία).",
        "Αν αναφέρετε ένα πρόβλημα, το κείμενο που γράφετε (και, αν επιλέξετε αυτή τη δυνατότητα, η έκδοση της εφαρμογής, η γλώσσα, το πρόγραμμα περιήγησης και η οθόνη) αποστέλλεται στο GitHub του έργου, όπου καταγράφεται και είναι ορατό στην ομάδα. Η διεύθυνση IP σας δεν αποστέλλεται. Μη γράφετε προσωπικά δεδομένα ή κωδικούς.",
    ]},
    "ru": {"titulo": "Отзывы и сообщения о проблемах", "paragrafos": [
        "Если вы оставите отзыв на странице «Отзывы», мы сохраним текст, дату и имя, которое вы решите показать (никакого, если хотите остаться анонимным; если вы просите показать имя, но не вводите его, появится «Посетитель № …»). Отзыв виден всем, без вашего IP-адреса. Мы также храним ваш IP-адрес, который видит только владелец сайта, исключительно для защиты от злоупотреблений: он удаляется из отзыва через 90 дней. Не пишите в отзыве личные данные; чтобы удалить отзыв, напишите нам (см. Контакты).",
        "Если вы сообщите о проблеме, написанный вами текст (и, если вы отметите эту опцию, версия приложения, язык, браузер и экран) отправляется на GitHub проекта, где он регистрируется и виден команде. Ваш IP-адрес не передаётся. Не пишите личные данные и пароли.",
    ]},
    "tr": {"titulo": "Yorumlar ve bildirilen sorunlar", "paragrafos": [
        "«Yorumlar» sayfasına yorum bırakırsanız metni, tarihi ve göstermeyi seçtiğiniz adı saklarız (anonim kalmak isterseniz hiçbiri; ad gösterilmesini isteyip boş bırakırsanız «Ziyaretçi no. …» görünür). Yorum herkese, IP adresiniz olmadan görünür. IP adresinizi de, yalnızca site sorumlusunun görebileceği biçimde ve sadece kötüye kullanımı önlemek için saklarız: 90 gün sonra yorumdan silinir. Yoruma kişisel veri yazmayın; silinmesini isterseniz bize yazın (bkz. İletişim).",
        "Bir sorun bildirirseniz yazdığınız metin (ve bu seçeneği işaretlerseniz uygulama sürümü, dil, tarayıcı ve ekran) projenin GitHub sayfasına gönderilir; orada kaydedilir ve ekip tarafından görülür. IP adresiniz gönderilmez. Kişisel veri veya parola yazmayın.",
    ]},
    "zh": {"titulo": "评论和报告的问题", "paragrafos": [
        "如果您在“评论”页面发表评论，我们会保存文本、日期和您选择显示的名字（若想匿名则不显示；若选择显示名字却未填写，则显示“访客 …号”）。评论对所有人可见，但不含您的 IP 地址。我们还会保存您的 IP 地址，仅网站负责人可见，目的仅是防止滥用：90 天后会从评论中删除。请勿在评论中写个人信息；如需删除评论，请联系我们（见“联系”）。",
        "如果您报告问题，您写的文字（以及勾选该选项时的应用版本、语言、浏览器和屏幕）会发送到项目的 GitHub，在那里记录并对团队可见。不会发送您的 IP 地址。请勿填写个人信息或密码。",
    ]},
    "ja": {"titulo": "コメントと報告された問題", "paragrafos": [
        "「コメント」ページにコメントを残すと、本文、日付、表示する名前を保存します（匿名の場合は名前なし。名前の表示を選んで空欄にした場合は「訪問者 No. …」と表示されます）。コメントはIPアドレスなしで全員に表示されます。また、サイト運営者だけが見られるIPアドレスを不正防止のためだけに保存し、90日後にコメントから削除します。コメントに個人情報を書かないでください。削除を希望する場合はご連絡ください（お問い合わせ参照）。",
        "問題を報告すると、入力した内容（およびオプションを選んだ場合はアプリのバージョン、言語、ブラウザ、画面）がプロジェクトのGitHubに送られ、記録されてチームに表示されます。IPアドレスは送信されません。個人情報やパスワードは書かないでください。",
    ]},
    "ko": {"titulo": "댓글과 신고된 문제", "paragrafos": [
        "'댓글' 페이지에 댓글을 남기면 내용, 날짜, 표시하기로 한 이름을 저장합니다(익명이면 이름 없음, 이름 표시를 선택하고 비워 두면 '방문자 번호 …'로 표시). 댓글은 IP 주소 없이 모두에게 보입니다. 또한 사이트 운영자만 볼 수 있는 IP 주소를 오직 남용 방지를 위해 저장하며, 90일 후 댓글에서 삭제됩니다. 댓글에 개인정보를 쓰지 마세요. 삭제를 원하시면 문의해 주세요(문의 참조).",
        "문제를 신고하면 작성한 내용(그리고 옵션을 선택한 경우 앱 버전, 언어, 브라우저, 화면)이 프로젝트의 GitHub로 전송되어 기록되고 팀에게 보입니다. IP 주소는 전송되지 않습니다. 개인정보나 비밀번호는 쓰지 마세요.",
    ]},
    "hi": {"titulo": "टिप्पणियाँ और रिपोर्ट की गई समस्याएँ", "paragrafos": [
        "यदि आप «टिप्पणियाँ» पेज पर टिप्पणी छोड़ते हैं, तो हम पाठ, तारीख और वह नाम सहेजते हैं जो आप दिखाना चुनते हैं (गुमनाम रहना चाहें तो कोई नहीं; नाम दिखाने को कहें पर खाली छोड़ दें तो «आगंतुक क्र. …» दिखता है)। टिप्पणी सभी को आपके IP पते के बिना दिखती है। हम आपका IP पता भी सहेजते हैं, जिसे केवल साइट का ज़िम्मेदार व्यक्ति देखता है, सिर्फ़ दुरुपयोग रोकने के लिए: वह 90 दिन बाद टिप्पणी से मिटा दिया जाता है। टिप्पणी में व्यक्तिगत जानकारी न लिखें; मिटाने के लिए हमें लिखें (संपर्क देखें)।",
        "यदि आप कोई समस्या रिपोर्ट करते हैं, तो आपका लिखा पाठ (और, यह विकल्प चुनने पर, ऐप का संस्करण, भाषा, ब्राउज़र और स्क्रीन) प्रोजेक्ट के GitHub पर भेजा जाता है, जहाँ वह दर्ज होता है और टीम को दिखता है। आपका IP पता नहीं भेजा जाता। व्यक्तिगत जानकारी या पासवर्ड न लिखें।",
    ]},
}


def aplicar(pagina: dict, lingua: str) -> dict:
    """A página de privacidade com a secção dos comentários e problemas, no fim (`pagina` já copiada e preenchida)."""
    d = TEXTOS.get(lingua, TEXTOS["pt"])
    pagina["seccoes"].append({"titulo": d["titulo"], "paragrafos": list(d["paragrafos"])})
    return pagina


# as linguas novas trazem estes textos no seu proprio `legal/<lingua>.py` (ver docs/LINGUAS.md)
from importlib import import_module  # noqa: E402

from .legal import LINGUAS_NOVAS  # noqa: E402

for _lg in LINGUAS_NOVAS:
    TEXTOS[_lg] = import_module(f"{__package__}.legal.{_lg}").OPINIAO
