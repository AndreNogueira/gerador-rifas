"""O que a Política de privacidade diz quando o editor de templates pode partilhar desenhos por ligação (`partilhas.py`, só com `DATABASE_URL`).

Sem a base de dados a funcionalidade não existe e o texto normal continua verdadeiro («os ficheiros são apagados em minutos»). Com ela, `textos_legais`
acrescenta, depois da secção «Que dados tratamos», uma secção «Desenhos partilhados»: o que fica guardado, durante quanto tempo e o que não fica.
Um texto por língua (provisório como os restantes: sem revisão nativa nem jurídica; em caso de divergência vale o português).
"""
from __future__ import annotations

TEXTOS: dict[str, dict] = {
    "pt": {"titulo": "Desenhos partilhados", "paragrafos": [
        "Se carregar em «Partilhar por ligação» no Editor de templates, o desenho (formas, textos e cores, sem imagens) fica guardado no nosso servidor, com um endereço difícil de adivinhar, durante 90 dias depois do último acesso, e qualquer pessoa com a ligação pode abri-lo. Não guardamos o seu endereço IP nem outros dados sobre quem partilha: não escreva no desenho dados pessoais nem segredos. Um desenho que não partilhe só é enviado ao servidor para criar o template e apaga-se com a sessão."]},
    "en": {"titulo": "Shared designs", "paragrafos": [
        "If you press “Share by link” in the Template editor, the design (shapes, texts and colors, without images) is stored on our server, under an address that is hard to guess, for 90 days after its last access, and anyone with the link can open it. We do not store your IP address or other data about who shares: do not write personal data or secrets in the design. A design you do not share is only sent to the server to create the template and is deleted with the session."]},
    "es": {"titulo": "Diseños compartidos", "paragrafos": [
        "Si pulsa «Compartir por enlace» en el Editor de plantillas, el diseño (formas, textos y colores, sin imágenes) se guarda en nuestro servidor, con una dirección difícil de adivinar, durante 90 días desde el último acceso, y cualquiera con el enlace puede abrirlo. No guardamos su dirección IP ni otros datos de quien comparte: no escriba en el diseño datos personales ni secretos. Un diseño que no comparta solo se envía al servidor para crear la plantilla y se borra con la sesión."]},
    "fr": {"titulo": "Dessins partagés", "paragrafos": [
        "Si vous cliquez sur « Partager par lien » dans l'Éditeur de modèles, le dessin (formes, textes et couleurs, sans images) est conservé sur notre serveur, sous une adresse difficile à deviner, pendant 90 jours après le dernier accès, et toute personne ayant le lien peut l'ouvrir. Nous ne conservons ni votre adresse IP ni d'autres données sur qui partage : n'écrivez pas de données personnelles ni de secrets dans le dessin. Un dessin que vous ne partagez pas n'est envoyé au serveur que pour créer le modèle et est supprimé avec la session."]},
    "de": {"titulo": "Geteilte Entwürfe", "paragrafos": [
        "Wenn Sie im Vorlageneditor auf „Per Link teilen“ klicken, wird der Entwurf (Formen, Texte und Farben, ohne Bilder) auf unserem Server unter einer schwer zu erratenden Adresse 90 Tage nach dem letzten Zugriff gespeichert, und jeder mit dem Link kann ihn öffnen. Wir speichern weder Ihre IP-Adresse noch andere Daten darüber, wer teilt: Schreiben Sie keine persönlichen Daten oder Geheimnisse in den Entwurf. Ein nicht geteilter Entwurf wird nur zum Erstellen der Vorlage an den Server gesendet und mit der Sitzung gelöscht."]},
    "it": {"titulo": "Disegni condivisi", "paragrafos": [
        "Se preme «Condividi con un link» nell'Editor di modelli, il disegno (forme, testi e colori, senza immagini) viene conservato sul nostro server, con un indirizzo difficile da indovinare, per 90 giorni dall'ultimo accesso, e chiunque abbia il link può aprirlo. Non conserviamo il suo indirizzo IP né altri dati su chi condivide: non scriva nel disegno dati personali né segreti. Un disegno che non condivide viene inviato al server solo per creare il modello e viene cancellato con la sessione."]},
    "nl": {"titulo": "Gedeelde ontwerpen", "paragrafos": [
        "Als u in de Sjablooneditor op ‘Delen via link’ klikt, wordt het ontwerp (vormen, teksten en kleuren, zonder afbeeldingen) 90 dagen na de laatste toegang op onze server bewaard, onder een adres dat moeilijk te raden is, en kan iedereen met de link het openen. We bewaren uw IP-adres en andere gegevens over wie deelt niet: schrijf geen persoonsgegevens of geheimen in het ontwerp. Een ontwerp dat u niet deelt wordt alleen naar de server gestuurd om het sjabloon te maken en verdwijnt met de sessie."]},
    "pl": {"titulo": "Udostępnione projekty", "paragrafos": [
        "Jeśli klikniesz „Udostępnij linkiem” w Edytorze szablonów, projekt (kształty, teksty i kolory, bez obrazów) zostanie zapisany na naszym serwerze pod trudnym do odgadnięcia adresem na 90 dni od ostatniego dostępu, a każdy z linkiem może go otworzyć. Nie przechowujemy twojego adresu IP ani innych danych o osobie udostępniającej: nie wpisuj w projekcie danych osobowych ani sekretów. Projekt, którego nie udostępniasz, trafia na serwer tylko po to, by utworzyć szablon, i znika razem z sesją."]},
    "sv": {"titulo": "Delade designer", "paragrafos": [
        "Om du trycker på ”Dela med länk” i Mallredigeraren sparas designen (former, texter och färger, utan bilder) på vår server, under en adress som är svår att gissa, i 90 dagar efter senaste åtkomst, och alla med länken kan öppna den. Vi sparar inte din IP-adress eller andra uppgifter om vem som delar: skriv inga personuppgifter eller hemligheter i designen. En design du inte delar skickas bara till servern för att skapa mallen och raderas med sessionen."]},
    "cs": {"titulo": "Sdílené návrhy", "paragrafos": [
        "Pokud v Editoru šablon kliknete na „Sdílet odkazem“, návrh (tvary, texty a barvy, bez obrázků) se uloží na náš server pod těžko uhodnutelnou adresou na 90 dní od posledního přístupu a kdokoli s odkazem jej může otevřít. Neukládáme vaši IP adresu ani jiné údaje o tom, kdo sdílí: nepište do návrhu osobní údaje ani tajemství. Návrh, který nesdílíte, se na server posílá jen kvůli vytvoření šablony a smaže se spolu s relací."]},
    "ro": {"titulo": "Desene partajate", "paragrafos": [
        "Dacă apeși „Distribuie prin link” în Editorul de șabloane, desenul (forme, texte și culori, fără imagini) este păstrat pe serverul nostru, la o adresă greu de ghicit, 90 de zile după ultimul acces, iar oricine are linkul îl poate deschide. Nu păstrăm adresa ta IP și nici alte date despre cine distribuie: nu scrie în desen date personale sau secrete. Un desen pe care nu îl distribui este trimis la server doar pentru a crea șablonul și se șterge odată cu sesiunea."]},
    "el": {"titulo": "Κοινόχρηστα σχέδια", "paragrafos": [
        "Αν πατήσετε «Κοινοποίηση με σύνδεσμο» στον Επεξεργαστή προτύπων, το σχέδιο (σχήματα, κείμενα και χρώματα, χωρίς εικόνες) αποθηκεύεται στον διακομιστή μας, με διεύθυνση δύσκολη στην εικασία, για 90 ημέρες μετά την τελευταία πρόσβαση, και όποιος έχει τον σύνδεσμο μπορεί να το ανοίξει. Δεν αποθηκεύουμε τη διεύθυνση IP σας ούτε άλλα δεδομένα για όποιον κοινοποιεί: μη γράφετε στο σχέδιο προσωπικά δεδομένα ή μυστικά. Ένα σχέδιο που δεν κοινοποιείτε στέλνεται στον διακομιστή μόνο για τη δημιουργία του προτύπου και διαγράφεται με τη συνεδρία."]},
    "ru": {"titulo": "Общие макеты", "paragrafos": [
        "Если нажать «Поделиться ссылкой» в Редакторе шаблонов, макет (фигуры, тексты и цвета, без изображений) сохраняется на нашем сервере по трудно угадываемому адресу на 90 дней после последнего обращения, и открыть его может любой, у кого есть ссылка. Мы не сохраняем ваш IP-адрес и другие данные о том, кто делится: не вписывайте в макет личные данные и секреты. Макет, которым вы не делитесь, отправляется на сервер только для создания шаблона и удаляется вместе с сеансом."]},
    "tr": {"titulo": "Paylaşılan tasarımlar", "paragrafos": [
        "Şablon düzenleyicide „Bağlantıyla paylaş”a basarsanız tasarım (şekiller, metinler ve renkler, görseller olmadan) sunucumuzda tahmini zor bir adresle son erişimden sonra 90 gün saklanır ve bağlantıya sahip herkes açabilir. IP adresinizi veya paylaşan kişiyle ilgili başka verileri saklamayız: tasarıma kişisel veri veya sır yazmayın. Paylaşmadığınız bir tasarım yalnızca şablonu oluşturmak için sunucuya gönderilir ve oturumla birlikte silinir."]},
    "zh": {"titulo": "分享的设计", "paragrafos": [
        "如果您在模板编辑器中点击“通过链接分享”，设计（形状、文字和颜色，不含图片）会保存在我们的服务器上，地址难以猜测，自最后一次访问起保留 90 天，任何拥有链接的人都可以打开。我们不保存您的 IP 地址或其他关于分享者的数据：请勿在设计中写入个人信息或机密。您没有分享的设计只会为生成模板而发送到服务器，并随会话一起删除。"]},
    "ja": {"titulo": "共有されたデザイン", "paragrafos": [
        "テンプレートエディターで「リンクで共有」を押すと、デザイン（図形・文字・色。画像は含みません）が推測されにくいアドレスで当サーバーに、最後のアクセスから90日間保存され、リンクを知っている人なら誰でも開けます。IP アドレスや共有した人に関するその他のデータは保存しません。デザインに個人情報や秘密を書かないでください。共有しないデザインは、テンプレートを作るためにだけサーバーへ送られ、セッションとともに削除されます。"]},
    "ko": {"titulo": "공유된 디자인", "paragrafos": [
        "템플릿 편집기에서 ‘링크로 공유’를 누르면 디자인(도형, 텍스트, 색상, 이미지 제외)이 추측하기 어려운 주소로 저희 서버에 마지막 접근 후 90일간 저장되며, 링크가 있는 누구나 열 수 있습니다. IP 주소나 공유한 사람에 대한 다른 데이터는 저장하지 않습니다. 디자인에 개인정보나 비밀을 쓰지 마세요. 공유하지 않은 디자인은 템플릿을 만들 때만 서버로 전송되며 세션과 함께 삭제됩니다."]},
    "hi": {"titulo": "साझा किए गए डिज़ाइन", "paragrafos": [
        "यदि आप टेम्पलेट संपादक में “लिंक से साझा करें” दबाते हैं, तो डिज़ाइन (आकृतियाँ, टेक्स्ट और रंग, चित्रों के बिना) हमारे सर्वर पर एक ऐसे पते के साथ, जिसका अनुमान लगाना कठिन है, आख़िरी पहुँच के बाद 90 दिन तक सहेजा जाता है, और लिंक वाला कोई भी इसे खोल सकता है। हम आपका IP पता या साझा करने वाले के बारे में कोई और डेटा नहीं सहेजते: डिज़ाइन में निजी जानकारी या रहस्य न लिखें। जो डिज़ाइन आप साझा नहीं करते, वह केवल टेम्पलेट बनाने के लिए सर्वर को भेजा जाता है और सत्र के साथ मिट जाता है।"]},
}


def aplicar(pagina: dict, lingua: str) -> dict:
    """A página de privacidade com a secção dos desenhos partilhados, depois de «Que dados tratamos» (`pagina` já copiada e preenchida)."""
    d = TEXTOS.get(lingua, TEXTOS["pt"])
    pagina["seccoes"].insert(2, {"titulo": d["titulo"], "paragrafos": list(d["paragrafos"])})
    return pagina


# as linguas novas trazem estes textos no seu proprio `legal/<lingua>.py` (ver docs/LINGUAS.md)
from importlib import import_module  # noqa: E402

from .legal import LINGUAS_NOVAS  # noqa: E402

for _lg in LINGUAS_NOVAS:
    TEXTOS[_lg] = import_module(f"{__package__}.legal.{_lg}").PARTILHAS


from core import ptbr  # noqa: E402

TEXTOS["pt-br"] = ptbr.derivar_tudo(TEXTOS["pt"])       # o português do Brasil deriva-se do de Portugal (core/ptbr.py)
