"""O que a Política de privacidade diz sobre as medições do site: a origem das visitas (só categorias, `metricas.categoria_de_origem`) e o desempenho nos browsers
(LCP, CLS e INP: três números, `desempenho.ts`).

`textos_legais` acrescenta, no fim da página (antes da secção dos comentários), uma secção «Origem das visitas e desempenho»: só categorias gerais (nunca o endereço da
página de origem nem o IP), o nome da campanha (`utm_source`) se o endereço o trouxer e três números de desempenho anónimos. Um texto por língua (provisório como os
restantes: sem revisão nativa nem jurídica; em caso de divergência vale o português).
"""

from __future__ import annotations

TEXTOS: dict[str, dict] = {
    "pt": {"titulo": "Origem das visitas e desempenho", "paragrafos": [
        "Para saber de onde vêm as visitas, registamos a origem de cada uma em categorias gerais (por exemplo «pesquisa», «rede social», «e-mail», «outro site» ou «direta») e, se o endereço da ligação o trouxer, o nome de campanha (utm_source). Nunca guardamos o endereço completo da página de onde veio nem o seu endereço IP.",
        "Medimos também, de forma anónima, o desempenho do site no seu navegador: quanto tempo a página demora a aparecer, quanto o conteúdo se mexe enquanto carrega e quanto demora a responder a um clique. São apenas três números (por exemplo «2,1 segundos»), enviados uma vez por visita, sem nada que o identifique, sem a página que viu e sem o seu endereço IP.",
    ]},
    "en": {"titulo": "Where visits come from, and performance", "paragrafos": [
        "To know where visits come from, we record the origin of each one in general categories (for example “search”, “social network”, “e-mail”, “other site” or “direct”) and, if the link carries it, the campaign name (utm_source). We never store the full address of the page you came from, nor your IP address.",
        "We also measure, anonymously, how the site performs in your browser: how long the page takes to appear, how much the content moves while loading and how long it takes to respond to a click. These are just three numbers (for example “2.1 seconds”), sent once per visit, with nothing that identifies you, without the page you saw and without your IP address.",
    ]},
    "es": {"titulo": "Origen de las visitas y rendimiento", "paragrafos": [
        "Para saber de dónde vienen las visitas, registramos el origen de cada una en categorías generales (por ejemplo «búsqueda», «red social», «correo», «otro sitio» o «directa») y, si el enlace lo trae, el nombre de campaña (utm_source). Nunca guardamos la dirección completa de la página de la que viene ni su dirección IP.",
        "También medimos, de forma anónima, el rendimiento del sitio en su navegador: cuánto tarda en aparecer la página, cuánto se mueve el contenido mientras carga y cuánto tarda en responder a un clic. Son solo tres números (por ejemplo «2,1 segundos»), enviados una vez por visita, sin nada que le identifique, sin la página que vio y sin su dirección IP.",
    ]},
    "fr": {"titulo": "Origine des visites et performances", "paragrafos": [
        "Pour savoir d'où viennent les visites, nous enregistrons l'origine de chacune en catégories générales (par exemple « recherche », « réseau social », « e-mail », « autre site » ou « directe ») et, si le lien le contient, le nom de campagne (utm_source). Nous ne conservons jamais l'adresse complète de la page d'où vous venez, ni votre adresse IP.",
        "Nous mesurons aussi, de façon anonyme, les performances du site dans votre navigateur : le temps que met la page à apparaître, de combien le contenu bouge pendant le chargement et le temps de réponse à un clic. Ce ne sont que trois nombres (par exemple « 2,1 secondes »), envoyés une fois par visite, sans rien qui vous identifie, sans la page consultée et sans votre adresse IP.",
    ]},
    "de": {"titulo": "Herkunft der Besuche und Leistung", "paragrafos": [
        "Um zu wissen, woher die Besuche kommen, erfassen wir die Herkunft jedes Besuchs in allgemeinen Kategorien (zum Beispiel „Suche“, „soziales Netzwerk“, „E-Mail“, „andere Website“ oder „direkt“) und, falls der Link ihn enthält, den Kampagnennamen (utm_source). Wir speichern nie die vollständige Adresse der Seite, von der Sie kommen, und auch nicht Ihre IP-Adresse.",
        "Wir messen außerdem anonym, wie die Website in Ihrem Browser abschneidet: wie lange die Seite bis zur Anzeige braucht, wie stark sich der Inhalt beim Laden verschiebt und wie lange die Reaktion auf einen Klick dauert. Das sind nur drei Zahlen (zum Beispiel „2,1 Sekunden“), einmal pro Besuch gesendet, ohne etwas, das Sie identifiziert, ohne die besuchte Seite und ohne Ihre IP-Adresse.",
    ]},
    "it": {"titulo": "Provenienza delle visite e prestazioni", "paragrafos": [
        "Per sapere da dove arrivano le visite, registriamo la provenienza di ciascuna in categorie generali (ad esempio «ricerca», «social network», «e-mail», «altro sito» o «diretta») e, se il link lo contiene, il nome della campagna (utm_source). Non conserviamo mai l'indirizzo completo della pagina da cui arrivi né il tuo indirizzo IP.",
        "Misuriamo anche, in forma anonima, le prestazioni del sito nel tuo browser: quanto impiega la pagina ad apparire, quanto si sposta il contenuto durante il caricamento e quanto impiega a rispondere a un clic. Sono solo tre numeri (ad esempio «2,1 secondi»), inviati una volta per visita, senza nulla che ti identifichi, senza la pagina vista e senza il tuo indirizzo IP.",
    ]},
    "nl": {"titulo": "Herkomst van bezoeken en prestaties", "paragrafos": [
        "Om te weten waar bezoeken vandaan komen, registreren we de herkomst van elk bezoek in algemene categorieën (bijvoorbeeld “zoeken”, “sociaal netwerk”, “e-mail”, “andere site” of “direct”) en, als de link die bevat, de campagnenaam (utm_source). We bewaren nooit het volledige adres van de pagina waar u vandaan komt, noch uw IP-adres.",
        "We meten ook, anoniem, hoe de site presteert in uw browser: hoe lang de pagina erover doet om te verschijnen, hoeveel de inhoud verschuift tijdens het laden en hoe lang het duurt om op een klik te reageren. Het zijn slechts drie getallen (bijvoorbeeld “2,1 seconden”), eenmaal per bezoek verstuurd, zonder iets dat u identificeert, zonder de bekeken pagina en zonder uw IP-adres.",
    ]},
    "pl": {"titulo": "Źródło wizyt i wydajność", "paragrafos": [
        "Aby wiedzieć, skąd przychodzą wizyty, zapisujemy źródło każdej z nich w ogólnych kategoriach (na przykład „wyszukiwarka”, „sieć społecznościowa”, „e-mail”, „inna strona” lub „bezpośrednio”) oraz, jeśli link go zawiera, nazwę kampanii (utm_source). Nigdy nie zapisujemy pełnego adresu strony, z której Państwo przychodzą, ani adresu IP.",
        "Mierzymy też anonimowo, jak strona działa w Państwa przeglądarce: ile czasu trwa jej pojawienie się, jak bardzo zawartość przesuwa się podczas ładowania i ile trwa reakcja na kliknięcie. To tylko trzy liczby (na przykład „2,1 sekundy”), wysyłane raz na wizytę, bez niczego, co Państwa identyfikuje, bez oglądanej strony i bez adresu IP.",
    ]},
    "sv": {"titulo": "Varifrån besöken kommer och prestanda", "paragrafos": [
        "För att veta varifrån besöken kommer registrerar vi ursprunget för varje besök i allmänna kategorier (till exempel ”sökning”, ”socialt nätverk”, ”e-post”, ”annan webbplats” eller ”direkt”) och, om länken innehåller det, kampanjnamnet (utm_source). Vi sparar aldrig den fullständiga adressen till sidan du kom från och inte heller din IP-adress.",
        "Vi mäter också, anonymt, hur webbplatsen presterar i din webbläsare: hur lång tid sidan tar på sig att visas, hur mycket innehållet flyttar sig medan den laddas och hur lång tid det tar att svara på ett klick. Det är bara tre siffror (till exempel ”2,1 sekunder”), skickade en gång per besök, utan något som identifierar dig, utan sidan du såg och utan din IP-adress.",
    ]},
    "cs": {"titulo": "Původ návštěv a výkon", "paragrafos": [
        "Abychom věděli, odkud návštěvy přicházejí, zaznamenáváme původ každé z nich v obecných kategoriích (například „vyhledávání“, „sociální síť“, „e-mail“, „jiný web“ nebo „přímo“) a, pokud ho odkaz obsahuje, název kampaně (utm_source). Nikdy neukládáme úplnou adresu stránky, odkud přicházíte, ani vaši IP adresu.",
        "Anonymně také měříme, jak se web chová ve vašem prohlížeči: jak dlouho trvá, než se stránka zobrazí, jak moc se obsah při načítání posouvá a jak dlouho trvá odpověď na kliknutí. Jsou to jen tři čísla (například „2,1 sekundy“), odesílaná jednou za návštěvu, bez čehokoli, co by vás identifikovalo, bez zobrazené stránky a bez vaší IP adresy.",
    ]},
    "ro": {"titulo": "Proveniența vizitelor și performanța", "paragrafos": [
        "Pentru a ști de unde vin vizitele, înregistrăm proveniența fiecăreia în categorii generale (de exemplu „căutare”, „rețea socială”, „e-mail”, „alt site” sau „directă”) și, dacă linkul îl conține, numele campaniei (utm_source). Nu păstrăm niciodată adresa completă a paginii de unde veniți și nici adresa dvs. IP.",
        "Măsurăm, de asemenea, anonim, cum se comportă site-ul în browserul dvs.: cât durează până apare pagina, cât se mișcă conținutul în timpul încărcării și cât durează să răspundă la un clic. Sunt doar trei numere (de exemplu „2,1 secunde”), trimise o dată pe vizită, fără nimic care să vă identifice, fără pagina văzută și fără adresa dvs. IP.",
    ]},
    "el": {"titulo": "Προέλευση των επισκέψεων και απόδοση", "paragrafos": [
        "Για να ξέρουμε από πού έρχονται οι επισκέψεις, καταγράφουμε την προέλευση κάθε μίας σε γενικές κατηγορίες (για παράδειγμα «αναζήτηση», «κοινωνικό δίκτυο», «e-mail», «άλλος ιστότοπος» ή «άμεση») και, αν ο σύνδεσμος την περιέχει, το όνομα της καμπάνιας (utm_source). Δεν αποθηκεύουμε ποτέ την πλήρη διεύθυνση της σελίδας από την οποία έρχεστε ούτε τη διεύθυνση IP σας.",
        "Μετράμε επίσης, ανώνυμα, πώς αποδίδει ο ιστότοπος στο πρόγραμμα περιήγησής σας: πόσο αργεί να εμφανιστεί η σελίδα, πόσο μετακινείται το περιεχόμενο κατά τη φόρτωση και πόσο αργεί να ανταποκριθεί σε ένα κλικ. Είναι μόνο τρεις αριθμοί (για παράδειγμα «2,1 δευτερόλεπτα»), που στέλνονται μία φορά ανά επίσκεψη, χωρίς τίποτα που να σας ταυτοποιεί, χωρίς τη σελίδα που είδατε και χωρίς τη διεύθυνση IP σας.",
    ]},
    "ru": {"titulo": "Откуда приходят посетители и производительность", "paragrafos": [
        "Чтобы знать, откуда приходят посетители, мы записываем источник каждого визита в общих категориях (например, «поиск», «социальная сеть», «e-mail», «другой сайт» или «напрямую») и, если ссылка его содержит, название кампании (utm_source). Мы никогда не сохраняем полный адрес страницы, с которой вы пришли, и ваш IP-адрес.",
        "Мы также анонимно измеряем, как сайт работает в вашем браузере: сколько времени страница появляется, насколько смещается содержимое при загрузке и сколько времени уходит на отклик на щелчок. Это всего три числа (например, «2,1 секунды»), отправляемые один раз за визит, без чего-либо, что вас идентифицирует, без просмотренной страницы и без вашего IP-адреса.",
    ]},
    "tr": {"titulo": "Ziyaretlerin kaynağı ve performans", "paragrafos": [
        "Ziyaretlerin nereden geldiğini bilmek için her birinin kaynağını genel kategoriler halinde (örneğin “arama”, “sosyal ağ”, “e-posta”, “başka site” veya “doğrudan”) ve bağlantı taşıyorsa kampanya adını (utm_source) kaydederiz. Geldiğiniz sayfanın tam adresini ve IP adresinizi asla saklamayız.",
        "Ayrıca sitenin tarayıcınızda nasıl çalıştığını anonim olarak ölçeriz: sayfanın görünmesinin ne kadar sürdüğünü, yüklenirken içeriğin ne kadar kaydığını ve bir tıklamaya ne kadar sürede yanıt verdiğini. Bunlar yalnızca üç sayıdır (örneğin “2,1 saniye”), ziyaret başına bir kez gönderilir; sizi tanımlayan hiçbir şey, gördüğünüz sayfa ve IP adresiniz içermez.",
    ]},
    "zh": {"titulo": "访问来源与性能", "paragrafos": [
        "为了了解访问从何而来，我们按一般类别记录每次访问的来源（例如“搜索”“社交网络”“电子邮件”“其他网站”或“直接访问”），如果链接带有活动名称（utm_source），也会记录。我们绝不保存您所来自页面的完整地址，也不保存您的 IP 地址。",
        "我们还会匿名测量网站在您浏览器中的表现：页面出现需要多长时间、加载时内容移动了多少，以及响应一次点击需要多长时间。这只有三个数字（例如“2.1 秒”），每次访问发送一次，不含任何可识别您的信息，也不含您看过的页面和您的 IP 地址。",
    ]},
    "ja": {"titulo": "訪問の流入元とパフォーマンス", "paragrafos": [
        "訪問がどこから来たかを知るため、各訪問の流入元を一般的なカテゴリ（たとえば「検索」「SNS」「メール」「その他のサイト」「直接」）で記録し、リンクに含まれていればキャンペーン名（utm_source）も記録します。訪問元ページの完全なアドレスやIPアドレスは保存しません。",
        "また、サイトがお使いのブラウザでどの程度動作するかを匿名で測定します：ページが表示されるまでの時間、読み込み中にコンテンツがどれだけ動くか、クリックへの応答にかかる時間です。数値は3つだけ（例：「2.1秒」）で、1回の訪問につき1度送信され、お客様を特定するものも、閲覧したページも、IPアドレスも含まれません。",
    ]},
    "ko": {"titulo": "방문 경로와 성능", "paragrafos": [
        "방문이 어디에서 오는지 알기 위해 각 방문의 경로를 일반적인 범주(예: “검색”, “소셜 네트워크”, “이메일”, “다른 사이트”, “직접”)로 기록하고, 링크에 포함되어 있으면 캠페인 이름(utm_source)도 기록합니다. 방문하신 이전 페이지의 전체 주소나 IP 주소는 절대 저장하지 않습니다.",
        "또한 웹사이트가 브라우저에서 어떻게 동작하는지 익명으로 측정합니다: 페이지가 나타나는 데 걸리는 시간, 로딩 중 콘텐츠가 움직이는 정도, 클릭에 반응하는 데 걸리는 시간입니다. 숫자 세 개(예: “2.1초”)뿐이며 방문당 한 번 전송되고, 사용자를 식별하는 정보도, 본 페이지도, IP 주소도 포함하지 않습니다.",
    ]},
    "hi": {"titulo": "विज़िट कहाँ से आती हैं और प्रदर्शन", "paragrafos": [
        "यह जानने के लिए कि विज़िट कहाँ से आती हैं, हम हर विज़िट का स्रोत सामान्य श्रेणियों में दर्ज करते हैं (जैसे “खोज”, “सोशल नेटवर्क”, “ईमेल”, “अन्य साइट” या “सीधे”) और, यदि लिंक में हो, तो अभियान का नाम (utm_source)। आप जिस पेज से आए उसका पूरा पता और आपका IP पता हम कभी सहेजते नहीं।",
        "हम गुमनाम रूप से यह भी मापते हैं कि साइट आपके ब्राउज़र में कैसा प्रदर्शन करती है: पेज दिखने में कितना समय लगता है, लोड होते समय सामग्री कितनी हिलती है और क्लिक का जवाब देने में कितना समय लगता है। ये केवल तीन संख्याएँ हैं (जैसे “2.1 सेकंड”), जो प्रति विज़िट एक बार भेजी जाती हैं, बिना ऐसी किसी चीज़ के जो आपको पहचाने, बिना देखे गए पेज के और बिना आपके IP पते के।",
    ]},
    "ca": {"titulo": "Origen de les visites i rendiment", "paragrafos": [
        "Per saber d'on vénen les visites, registrem l'origen de cadascuna en categories generals (per exemple «cerca», «xarxa social», «correu», «un altre lloc» o «directa») i, si l'enllaç el porta, el nom de campanya (utm_source). Mai no desem l'adreça completa de la pàgina d'on veniu ni la vostra adreça IP.",
        "També mesurem, de forma anònima, el rendiment del lloc al vostre navegador: quant triga a aparèixer la pàgina, quant es mou el contingut mentre carrega i quant triga a respondre a un clic. Són només tres números (per exemple «2,1 segons»), enviats un cop per visita, sense res que us identifiqui, sense la pàgina que heu vist i sense la vostra adreça IP.",
    ]},
    "uk": {"titulo": "Звідки приходять відвідувачі та продуктивність", "paragrafos": [
        "Щоб знати, звідки приходять відвідувачі, ми записуємо джерело кожного візиту в загальних категоріях (наприклад, «пошук», «соціальна мережа», «e-mail», «інший сайт» або «напряму») і, якщо посилання його містить, назву кампанії (utm_source). Ми ніколи не зберігаємо повну адресу сторінки, з якої ви прийшли, та вашу IP-адресу.",
        "Ми також анонімно вимірюємо, як сайт працює у вашому браузері: скільки часу з'являється сторінка, наскільки зміщується вміст під час завантаження і скільки триває відповідь на клік. Це лише три числа (наприклад, «2,1 секунди»), що надсилаються раз за візит, без нічого, що вас ідентифікує, без переглянутої сторінки та без вашої IP-адреси.",
    ]},
    "id": {"titulo": "Asal kunjungan dan kinerja", "paragrafos": [
        "Untuk mengetahui dari mana kunjungan berasal, kami mencatat asal tiap kunjungan dalam kategori umum (misalnya “pencarian”, “jejaring sosial”, “email”, “situs lain” atau “langsung”) dan, jika tautannya memuat, nama kampanye (utm_source). Kami tidak pernah menyimpan alamat lengkap halaman asal Anda maupun alamat IP Anda.",
        "Kami juga mengukur, secara anonim, kinerja situs di peramban Anda: berapa lama halaman muncul, seberapa banyak konten bergeser saat dimuat, dan berapa lama merespons sebuah klik. Hanya tiga angka (misalnya “2,1 detik”), dikirim sekali per kunjungan, tanpa sesuatu yang mengidentifikasi Anda, tanpa halaman yang Anda lihat dan tanpa alamat IP Anda.",
    ]},
    "vi": {"titulo": "Nguồn của các lượt truy cập và hiệu năng", "paragrafos": [
        "Để biết lượt truy cập đến từ đâu, chúng tôi ghi lại nguồn của từng lượt theo các nhóm chung (ví dụ “tìm kiếm”, “mạng xã hội”, “email”, “trang khác” hoặc “trực tiếp”) và, nếu liên kết có, tên chiến dịch (utm_source). Chúng tôi không bao giờ lưu địa chỉ đầy đủ của trang bạn đến từ đâu, cũng như địa chỉ IP của bạn.",
        "Chúng tôi cũng đo ẩn danh hiệu năng của trang trong trình duyệt của bạn: trang mất bao lâu để hiện ra, nội dung dịch chuyển bao nhiêu khi đang tải và mất bao lâu để phản hồi một cú nhấp. Chỉ có ba con số (ví dụ “2,1 giây”), gửi một lần mỗi lượt truy cập, không có gì định danh bạn, không có trang bạn xem và không có địa chỉ IP của bạn.",
    ]},
}


def aplicar(pagina: dict, lingua: str) -> dict:
    """A página de privacidade com a secção da origem das visitas e do desempenho, no fim (`pagina` já copiada e preenchida)."""
    d = TEXTOS.get(lingua, TEXTOS["pt"])
    pagina["seccoes"].append({"titulo": d["titulo"], "paragrafos": list(d["paragrafos"])})
    return pagina
