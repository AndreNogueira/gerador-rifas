"""O que a Política de privacidade diz sobre os comentários dos visitantes e os problemas reportados (`opiniao.py`, `github_issues.py`).

`textos_legais` acrescenta, no fim da página, uma secção «Comentários e problemas reportados»: o que fica guardado (texto, data, nome a mostrar e
o país (nunca o endereço IP), que só o dono vê), o que se vê em público (nunca o IP) e o que vai para o GitHub (nunca o IP).
Um texto por língua (provisório como os restantes: sem revisão nativa nem jurídica; em caso de divergência vale o português).
"""
from __future__ import annotations

TEXTOS: dict[str, dict] = {
    "pt": {"titulo": "Comentários e problemas reportados", "paragrafos": [
        "Se deixar um comentário na página «Comentários», guardamos o texto, a data, o país de onde o envia (por exemplo PT, indicado pela rede do alojamento; não guardamos o endereço IP) e o nome que escolher mostrar (nenhum, se preferir ficar anónimo(a); se pedir para mostrar um nome e não o escrever, aparece «Visitante n.º …»). O texto e o nome ficam visíveis para todos; o país só o responsável do site o vê. Para travar abusos o servidor conta em memória, durante uma hora, quantos comentários chegam de cada endereço, sem os guardar. Não escreva dados pessoais no comentário; se quiser que um comentário seja apagado, escreva-nos (ver Contacto).",
        "Se reportar um problema, o texto que escrever (e, se marcar essa opção, a versão da aplicação, a língua, o navegador e o ecrã) é enviado para o GitHub do projeto, onde fica registado e visível para a equipa. O seu endereço IP não é enviado. Não escreva dados pessoais nem palavras-passe.",
    ]},
    "en": {"titulo": "Comments and reported problems", "paragrafos": [
        "If you leave a comment on the “Comments” page, we store the text, the date, the country it is sent from (for example PT, given by the hosting network; we do not store the IP address) and the name you choose to show (none, if you prefer to stay anonymous; if you ask to show a name but leave it blank, “Visitor no. …” appears). The text and name are visible to everyone; only the site owner sees the country. To stop abuse the server counts in memory, for one hour, how many comments come from each address, without storing them. Do not write personal data in the comment; if you want a comment deleted, write to us (see Contact).",
        "If you report a problem, the text you write (and, if you tick that option, the app version, language, browser and screen) is sent to the project's GitHub, where it is recorded and visible to the team. Your IP address is not sent. Do not write personal data or passwords.",
    ]},
    "es": {"titulo": "Comentarios y problemas informados", "paragrafos": [
        "Si deja un comentario en la página «Comentarios», guardamos el texto, la fecha, el país desde el que se envía (por ejemplo PT, indicado por la red del alojamiento; no guardamos la dirección IP) y el nombre que elija mostrar (ninguno, si prefiere permanecer anónimo/a; si pide mostrar un nombre y no lo escribe, aparece «Visitante n.º …»). El texto y el nombre son visibles para todos; el país solo lo ve el responsable del sitio. Para frenar abusos el servidor cuenta en memoria, durante una hora, cuántos comentarios llegan de cada dirección, sin guardarlos. No escriba datos personales en el comentario; si quiere que se borre, escríbanos (vea Contacto).",
        "Si informa de un problema, el texto que escriba (y, si marca esa opción, la versión de la aplicación, el idioma, el navegador y la pantalla) se envía al GitHub del proyecto, donde queda registrado y visible para el equipo. Su dirección IP no se envía. No escriba datos personales ni contraseñas.",
    ]},
    "fr": {"titulo": "Commentaires et problèmes signalés", "paragrafos": [
        "Si vous laissez un commentaire sur la page « Commentaires », nous conservons le texte, la date, le pays d'où il est envoyé (par exemple PT, indiqué par le réseau d'hébergement ; nous ne conservons pas l'adresse IP) et le nom que vous choisissez d'afficher (aucun, si vous préférez rester anonyme ; si vous demandez d'afficher un nom sans l'écrire, « Visiteur n° … » apparaît). Le texte et le nom sont visibles par tous ; seul le responsable du site voit le pays. Pour limiter les abus, le serveur compte en mémoire, pendant une heure, combien de commentaires arrivent de chaque adresse, sans les conserver. N'écrivez pas de données personnelles dans le commentaire ; pour le faire supprimer, écrivez-nous (voir Contact).",
        "Si vous signalez un problème, le texte que vous écrivez (et, si vous cochez cette option, la version de l'application, la langue, le navigateur et l'écran) est envoyé au GitHub du projet, où il est enregistré et visible par l'équipe. Votre adresse IP n'est pas envoyée. N'écrivez ni données personnelles ni mots de passe.",
    ]},
    "de": {"titulo": "Kommentare und gemeldete Probleme", "paragrafos": [
        "Wenn Sie auf der Seite „Kommentare“ einen Kommentar hinterlassen, speichern wir den Text, das Datum, das Land, aus dem er gesendet wird (zum Beispiel PT, vom Hosting-Netz mitgeteilt; die IP-Adresse speichern wir nicht) und den Namen, den Sie anzeigen möchten (keinen, wenn Sie anonym bleiben wollen; wählen Sie einen Namen, lassen ihn aber leer, erscheint „Besucher Nr. …“). Text und Name sind für alle sichtbar; das Land sieht nur der Betreiber. Zur Missbrauchsabwehr zählt der Server eine Stunde lang im Speicher, wie viele Kommentare von jeder Adresse kommen, ohne sie zu speichern. Schreiben Sie keine persönlichen Daten in den Kommentar; zum Löschen schreiben Sie uns (siehe Kontakt).",
        "Wenn Sie ein Problem melden, wird der von Ihnen geschriebene Text (und, wenn Sie die Option anhaken, Version der Anwendung, Sprache, Browser und Bildschirm) an das GitHub des Projekts gesendet, wo er erfasst und für das Team sichtbar ist. Ihre IP-Adresse wird nicht gesendet. Schreiben Sie keine persönlichen Daten oder Passwörter.",
    ]},
    "it": {"titulo": "Commenti e problemi segnalati", "paragrafos": [
        "Se lascia un commento nella pagina «Commenti», conserviamo il testo, la data, il paese da cui viene inviato (per esempio PT, indicato dalla rete di hosting; non conserviamo l'indirizzo IP) e il nome che sceglie di mostrare (nessuno, se preferisce restare anonimo/a; se chiede di mostrare un nome e non lo scrive, compare «Visitatore n. …»). Il testo e il nome sono visibili a tutti; il paese lo vede solo il responsabile del sito. Per limitare gli abusi il server conta in memoria, per un'ora, quanti commenti arrivano da ogni indirizzo, senza conservarli. Non scriva dati personali nel commento; per farlo eliminare ci scriva (vedi Contatti).",
        "Se segnala un problema, il testo che scrive (e, se seleziona l'opzione, versione dell'app, lingua, browser e schermo) viene inviato al GitHub del progetto, dove è registrato e visibile al team. Il suo indirizzo IP non viene inviato. Non scriva dati personali né password.",
    ]},
    "nl": {"titulo": "Reacties en gemelde problemen", "paragrafos": [
        "Als u een reactie achterlaat op de pagina ‘Reacties’, bewaren we de tekst, de datum, het land waaruit ze wordt verstuurd (bijvoorbeeld PT, doorgegeven door het hostingnetwerk; we bewaren het IP-adres niet) en de naam die u wilt tonen (geen, als u anoniem wilt blijven; vraagt u om een naam te tonen maar laat u hem leeg, dan staat er ‘Bezoeker nr. …’). Tekst en naam zijn voor iedereen zichtbaar; het land ziet alleen de beheerder. Tegen misbruik telt de server een uur lang in het geheugen hoeveel reacties van elk adres komen, zonder ze te bewaren. Schrijf geen persoonsgegevens in de reactie; wilt u haar laten verwijderen, schrijf ons (zie Contact).",
        "Als u een probleem meldt, wordt de tekst die u schrijft (en, als u die optie aanvinkt, de appversie, taal, browser en scherm) naar de GitHub van het project gestuurd, waar hij wordt vastgelegd en zichtbaar is voor het team. Uw IP-adres wordt niet verstuurd. Schrijf geen persoonsgegevens of wachtwoorden.",
    ]},
    "pl": {"titulo": "Komentarze i zgłoszone problemy", "paragrafos": [
        "Jeśli zostawisz komentarz na stronie „Komentarze”, przechowujemy tekst, datę, kraj, z którego go wysłano (np. PT, podany przez sieć hostingową; nie przechowujemy adresu IP) i imię, które wybierzesz do wyświetlenia (żadne, jeśli wolisz pozostać anonimowy; jeśli poprosisz o pokazanie imienia, ale go nie wpiszesz, pojawi się „Gość nr …”). Tekst i imię są widoczne dla wszystkich; kraj widzi tylko administrator serwisu. Aby ograniczać nadużycia, serwer przez godzinę liczy w pamięci, ile komentarzy przychodzi z każdego adresu, bez ich zapisywania. Nie wpisuj w komentarzu danych osobowych; aby usunąć komentarz, napisz do nas (zob. Kontakt).",
        "Jeśli zgłosisz problem, wpisany tekst (oraz, jeśli zaznaczysz tę opcję, wersja aplikacji, język, przeglądarka i ekran) jest wysyłany do GitHuba projektu, gdzie zostaje zapisany i widoczny dla zespołu. Twój adres IP nie jest wysyłany. Nie wpisuj danych osobowych ani haseł.",
    ]},
    "sv": {"titulo": "Kommentarer och rapporterade problem", "paragrafos": [
        "Om du lämnar en kommentar på sidan ”Kommentarer” sparar vi texten, datumet, landet den skickas från (till exempel PT, angivet av värdnätverket; vi sparar inte IP-adressen) och det namn du väljer att visa (inget, om du vill vara anonym; ber du om att visa ett namn men lämnar det tomt visas ”Besökare nr …”). Texten och namnet är synliga för alla; landet ser bara webbplatsens ansvarige. För att stoppa missbruk räknar servern i minnet, under en timme, hur många kommentarer som kommer från varje adress, utan att spara dem. Skriv inga personuppgifter i kommentaren; vill du att den raderas, skriv till oss (se Kontakt).",
        "Om du rapporterar ett problem skickas texten du skriver (och, om du kryssar i alternativet, appens version, språk, webbläsare och skärm) till projektets GitHub, där den registreras och syns för teamet. Din IP-adress skickas inte. Skriv inga personuppgifter eller lösenord.",
    ]},
    "cs": {"titulo": "Komentáře a nahlášené problémy", "paragrafos": [
        "Pokud zanecháte komentář na stránce „Komentáře“, uložíme text, datum, zemi, ze které je odeslán (např. PT, uvedenou hostingovou sítí; IP adresu neukládáme) a jméno, které se rozhodnete zobrazit (žádné, chcete-li zůstat anonymní; požádáte-li o zobrazení jména a nevyplníte ho, zobrazí se „Návštěvník č. …“). Text a jméno jsou viditelné všem; zemi vidí jen provozovatel webu. Proti zneužití server po dobu jedné hodiny počítá v paměti, kolik komentářů přichází z každé adresy, aniž by je ukládal. Nepište do komentáře osobní údaje; chcete-li jej smazat, napište nám (viz Kontakt).",
        "Nahlásíte-li problém, text, který napíšete (a, zaškrtnete-li tuto volbu, verze aplikace, jazyk, prohlížeč a obrazovka), se odešle na GitHub projektu, kde je zaznamenán a viditelný pro tým. Vaše IP adresa se neodesílá. Nepište osobní údaje ani hesla.",
    ]},
    "ro": {"titulo": "Comentarii și probleme raportate", "paragrafos": [
        "Dacă lași un comentariu pe pagina „Comentarii”, păstrăm textul, data, țara din care este trimis (de exemplu PT, indicată de rețeaua de găzduire; nu păstrăm adresa IP) și numele pe care alegi să-l afișezi (niciunul, dacă preferi să rămâi anonim; dacă ceri să apară un nume și nu-l scrii, apare „Vizitator nr. …”). Textul și numele sunt vizibile pentru toți; țara o vede doar responsabilul site-ului. Pentru a opri abuzurile, serverul numără în memorie, timp de o oră, câte comentarii vin de la fiecare adresă, fără a le păstra. Nu scrie date personale în comentariu; dacă vrei să fie șters, scrie-ne (vezi Contact).",
        "Dacă raportezi o problemă, textul scris (și, dacă bifezi opțiunea, versiunea aplicației, limba, browserul și ecranul) este trimis către GitHub-ul proiectului, unde este înregistrat și vizibil pentru echipă. Adresa ta IP nu este trimisă. Nu scrie date personale sau parole.",
    ]},
    "el": {"titulo": "Σχόλια και αναφορές προβλημάτων", "paragrafos": [
        "Αν αφήσετε ένα σχόλιο στη σελίδα «Σχόλια», φυλάσσουμε το κείμενο, την ημερομηνία, τη χώρα από την οποία στέλνεται (π.χ. PT, όπως τη δίνει το δίκτυο φιλοξενίας· δεν φυλάσσουμε τη διεύθυνση IP) και το όνομα που επιλέγετε να εμφανίζεται (κανένα, αν προτιμάτε να μείνετε ανώνυμοι· αν ζητήσετε να εμφανιστεί όνομα και δεν το γράψετε, εμφανίζεται «Επισκέπτης αρ. …»). Το κείμενο και το όνομα είναι ορατά σε όλους· τη χώρα τη βλέπει μόνο ο υπεύθυνος του ιστότοπου. Για την αποτροπή κατάχρησης ο διακομιστής μετρά στη μνήμη, για μία ώρα, πόσα σχόλια έρχονται από κάθε διεύθυνση, χωρίς να τα φυλάσσει. Μη γράφετε προσωπικά δεδομένα στο σχόλιο· για διαγραφή, γράψτε μας (βλ. Επικοινωνία).",
        "Αν αναφέρετε ένα πρόβλημα, το κείμενο που γράφετε (και, αν επιλέξετε αυτή τη δυνατότητα, η έκδοση της εφαρμογής, η γλώσσα, το πρόγραμμα περιήγησης και η οθόνη) αποστέλλεται στο GitHub του έργου, όπου καταγράφεται και είναι ορατό στην ομάδα. Η διεύθυνση IP σας δεν αποστέλλεται. Μη γράφετε προσωπικά δεδομένα ή κωδικούς.",
    ]},
    "ru": {"titulo": "Отзывы и сообщения о проблемах", "paragrafos": [
        "Если вы оставите отзыв на странице «Отзывы», мы сохраним текст, дату, страну, из которой он отправлен (например, PT, её сообщает сеть хостинга; IP-адрес мы не храним), и имя, которое вы решите показать (никакого, если хотите остаться анонимным; если вы просите показать имя, но не вводите его, появится «Посетитель № …»). Текст и имя видны всем; страну видит только владелец сайта. Для защиты от злоупотреблений сервер в течение часа считает в памяти, сколько отзывов приходит с каждого адреса, не сохраняя их. Не пишите в отзыве личные данные; чтобы удалить отзыв, напишите нам (см. Контакты).",
        "Если вы сообщите о проблеме, написанный вами текст (и, если вы отметите эту опцию, версия приложения, язык, браузер и экран) отправляется на GitHub проекта, где он регистрируется и виден команде. Ваш IP-адрес не передаётся. Не пишите личные данные и пароли.",
    ]},
    "tr": {"titulo": "Yorumlar ve bildirilen sorunlar", "paragrafos": [
        "«Yorumlar» sayfasına yorum bırakırsanız metni, tarihi, gönderildiği ülkeyi (örneğin PT, barındırma ağı tarafından bildirilir; IP adresini saklamıyoruz) ve göstermeyi seçtiğiniz adı saklarız (anonim kalmak isterseniz hiçbiri; ad gösterilmesini isteyip boş bırakırsanız «Ziyaretçi no. …» görünür). Metin ve ad herkese görünür; ülkeyi yalnızca site sorumlusu görür. Kötüye kullanımı önlemek için sunucu bir saat boyunca her adresten kaç yorum geldiğini bellekte sayar, saklamaz. Yoruma kişisel veri yazmayın; silinmesini isterseniz bize yazın (bkz. İletişim).",
        "Bir sorun bildirirseniz yazdığınız metin (ve bu seçeneği işaretlerseniz uygulama sürümü, dil, tarayıcı ve ekran) projenin GitHub sayfasına gönderilir; orada kaydedilir ve ekip tarafından görülür. IP adresiniz gönderilmez. Kişisel veri veya parola yazmayın.",
    ]},
    "zh": {"titulo": "评论和报告的问题", "paragrafos": [
        "如果您在“评论”页面发表评论，我们会保存文本、日期、发送所在的国家（例如 PT，由托管网络提供；我们不保存 IP 地址）以及您选择显示的名字（若想匿名则不显示；若选择显示名字却未填写，则显示“访客 …号”）。文本和名字对所有人可见；国家仅网站负责人可见。为防止滥用，服务器会在内存中统计一小时内每个地址发来的评论数量，但不保存。请勿在评论中写个人信息；如需删除评论，请联系我们（见“联系”）。",
        "如果您报告问题，您写的文字（以及勾选该选项时的应用版本、语言、浏览器和屏幕）会发送到项目的 GitHub，在那里记录并对团队可见。不会发送您的 IP 地址。请勿填写个人信息或密码。",
    ]},
    "ja": {"titulo": "コメントと報告された問題", "paragrafos": [
        "「コメント」ページにコメントを残すと、本文、日付、送信元の国（例：PT。ホスティングのネットワークが示すもので、IPアドレスは保存しません）、表示する名前を保存します（匿名の場合は名前なし。名前の表示を選んで空欄にした場合は「訪問者 No. …」と表示）。本文と名前は全員に表示され、国は運営者だけが見られます。不正防止のため、サーバーは1時間だけ各アドレスから届いたコメント数をメモリ上で数え、保存はしません。コメントに個人情報を書かないでください。削除を希望する場合はご連絡ください（お問い合わせ参照）。",
        "問題を報告すると、入力した内容（およびオプションを選んだ場合はアプリのバージョン、言語、ブラウザ、画面）がプロジェクトのGitHubに送られ、記録されてチームに表示されます。IPアドレスは送信されません。個人情報やパスワードは書かないでください。",
    ]},
    "ko": {"titulo": "댓글과 신고된 문제", "paragrafos": [
        "'댓글' 페이지에 댓글을 남기면 내용, 날짜, 보낸 국가(예: PT, 호스팅 네트워크가 알려 주며 IP 주소는 저장하지 않음), 표시하기로 한 이름을 저장합니다(익명이면 이름 없음, 이름 표시를 선택하고 비워 두면 '방문자 번호 …'로 표시). 내용과 이름은 모두에게 보이고 국가는 사이트 운영자만 볼 수 있습니다. 남용을 막기 위해 서버는 한 시간 동안 각 주소에서 온 댓글 수를 메모리에서만 세며 저장하지 않습니다. 댓글에 개인정보를 쓰지 마세요. 삭제를 원하시면 문의해 주세요(문의 참조).",
        "문제를 신고하면 작성한 내용(그리고 옵션을 선택한 경우 앱 버전, 언어, 브라우저, 화면)이 프로젝트의 GitHub로 전송되어 기록되고 팀에게 보입니다. IP 주소는 전송되지 않습니다. 개인정보나 비밀번호는 쓰지 마세요.",
    ]},
    "hi": {"titulo": "टिप्पणियाँ और रिपोर्ट की गई समस्याएँ", "paragrafos": [
        "यदि आप «टिप्पणियाँ» पेज पर टिप्पणी छोड़ते हैं, तो हम पाठ, तारीख, वह देश जहाँ से वह भेजी गई (जैसे PT, होस्टिंग नेटवर्क बताता है; हम IP पता नहीं सहेजते) और वह नाम सहेजते हैं जो आप दिखाना चुनते हैं (गुमनाम रहना चाहें तो कोई नहीं; नाम दिखाने को कहें पर खाली छोड़ दें तो «आगंतुक क्र. …» दिखता है)। पाठ और नाम सभी को दिखते हैं; देश केवल साइट का ज़िम्मेदार व्यक्ति देखता है। दुरुपयोग रोकने के लिए सर्वर एक घंटे तक मेमोरी में गिनता है कि हर पते से कितनी टिप्पणियाँ आईं, उन्हें सहेजे बिना। टिप्पणी में व्यक्तिगत जानकारी न लिखें; मिटाने के लिए हमें लिखें (संपर्क देखें)।",
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
