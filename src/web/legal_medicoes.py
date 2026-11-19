"""O que a Política de privacidade diz sobre as medições do site: a origem das visitas (e, mais tarde, o desempenho nos browsers).

`textos_legais` acrescenta, no fim da página, uma secção «Origem das visitas»: só categorias gerais (nunca o endereço da página de origem nem o IP) e o nome da campanha
(`utm_source`) se o endereço o trouxer. Um texto por língua (provisório como os restantes: sem revisão nativa nem jurídica; em caso de divergência vale o português).
"""
from __future__ import annotations

TEXTOS: dict[str, dict] = {
    "pt": {"titulo": "Origem das visitas", "paragrafos": [
        "Para saber de onde vêm as visitas, registamos a origem de cada uma em categorias gerais (por exemplo «pesquisa», «rede social», «e-mail», «outro site» ou «direta») e, se o endereço da ligação o trouxer, o nome de campanha (utm_source). Nunca guardamos o endereço completo da página de onde veio nem o seu endereço IP.",
    ]},
    "en": {"titulo": "Where visits come from", "paragrafos": [
        "To know where visits come from, we record the origin of each one in general categories (for example “search”, “social network”, “e-mail”, “other site” or “direct”) and, if the link carries it, the campaign name (utm_source). We never store the full address of the page you came from, nor your IP address.",
    ]},
    "es": {"titulo": "Origen de las visitas", "paragrafos": [
        "Para saber de dónde vienen las visitas, registramos el origen de cada una en categorías generales (por ejemplo «búsqueda», «red social», «correo», «otro sitio» o «directa») y, si el enlace lo trae, el nombre de campaña (utm_source). Nunca guardamos la dirección completa de la página de la que viene ni su dirección IP.",
    ]},
    "fr": {"titulo": "Origine des visites", "paragrafos": [
        "Pour savoir d'où viennent les visites, nous enregistrons l'origine de chacune en catégories générales (par exemple « recherche », « réseau social », « e-mail », « autre site » ou « directe ») et, si le lien le contient, le nom de campagne (utm_source). Nous ne conservons jamais l'adresse complète de la page d'où vous venez, ni votre adresse IP.",
    ]},
    "de": {"titulo": "Herkunft der Besuche", "paragrafos": [
        "Um zu wissen, woher die Besuche kommen, erfassen wir die Herkunft jedes Besuchs in allgemeinen Kategorien (zum Beispiel „Suche“, „soziales Netzwerk“, „E-Mail“, „andere Website“ oder „direkt“) und, falls der Link ihn enthält, den Kampagnennamen (utm_source). Wir speichern nie die vollständige Adresse der Seite, von der Sie kommen, und auch nicht Ihre IP-Adresse.",
    ]},
    "it": {"titulo": "Provenienza delle visite", "paragrafos": [
        "Per sapere da dove arrivano le visite, registriamo la provenienza di ciascuna in categorie generali (ad esempio «ricerca», «social network», «e-mail», «altro sito» o «diretta») e, se il link lo contiene, il nome della campagna (utm_source). Non conserviamo mai l'indirizzo completo della pagina da cui arrivi né il tuo indirizzo IP.",
    ]},
    "nl": {"titulo": "Herkomst van bezoeken", "paragrafos": [
        "Om te weten waar bezoeken vandaan komen, registreren we de herkomst van elk bezoek in algemene categorieën (bijvoorbeeld “zoeken”, “sociaal netwerk”, “e-mail”, “andere site” of “direct”) en, als de link die bevat, de campagnenaam (utm_source). We bewaren nooit het volledige adres van de pagina waar u vandaan komt, noch uw IP-adres.",
    ]},
    "pl": {"titulo": "Źródło wizyt", "paragrafos": [
        "Aby wiedzieć, skąd przychodzą wizyty, zapisujemy źródło każdej z nich w ogólnych kategoriach (na przykład „wyszukiwarka”, „sieć społecznościowa”, „e-mail”, „inna strona” lub „bezpośrednio”) oraz, jeśli link go zawiera, nazwę kampanii (utm_source). Nigdy nie zapisujemy pełnego adresu strony, z której Państwo przychodzą, ani adresu IP.",
    ]},
    "sv": {"titulo": "Varifrån besöken kommer", "paragrafos": [
        "För att veta varifrån besöken kommer registrerar vi ursprunget för varje besök i allmänna kategorier (till exempel ”sökning”, ”socialt nätverk”, ”e-post”, ”annan webbplats” eller ”direkt”) och, om länken innehåller det, kampanjnamnet (utm_source). Vi sparar aldrig den fullständiga adressen till sidan du kom från och inte heller din IP-adress.",
    ]},
    "cs": {"titulo": "Původ návštěv", "paragrafos": [
        "Abychom věděli, odkud návštěvy přicházejí, zaznamenáváme původ každé z nich v obecných kategoriích (například „vyhledávání“, „sociální síť“, „e-mail“, „jiný web“ nebo „přímo“) a, pokud ho odkaz obsahuje, název kampaně (utm_source). Nikdy neukládáme úplnou adresu stránky, odkud přicházíte, ani vaši IP adresu.",
    ]},
    "ro": {"titulo": "Proveniența vizitelor", "paragrafos": [
        "Pentru a ști de unde vin vizitele, înregistrăm proveniența fiecăreia în categorii generale (de exemplu „căutare”, „rețea socială”, „e-mail”, „alt site” sau „directă”) și, dacă linkul îl conține, numele campaniei (utm_source). Nu păstrăm niciodată adresa completă a paginii de unde veniți și nici adresa dvs. IP.",
    ]},
    "el": {"titulo": "Προέλευση των επισκέψεων", "paragrafos": [
        "Για να ξέρουμε από πού έρχονται οι επισκέψεις, καταγράφουμε την προέλευση κάθε μίας σε γενικές κατηγορίες (για παράδειγμα «αναζήτηση», «κοινωνικό δίκτυο», «e-mail», «άλλος ιστότοπος» ή «άμεση») και, αν ο σύνδεσμος την περιέχει, το όνομα της καμπάνιας (utm_source). Δεν αποθηκεύουμε ποτέ την πλήρη διεύθυνση της σελίδας από την οποία έρχεστε ούτε τη διεύθυνση IP σας.",
    ]},
    "ru": {"titulo": "Откуда приходят посетители", "paragrafos": [
        "Чтобы знать, откуда приходят посетители, мы записываем источник каждого визита в общих категориях (например, «поиск», «социальная сеть», «e-mail», «другой сайт» или «напрямую») и, если ссылка его содержит, название кампании (utm_source). Мы никогда не сохраняем полный адрес страницы, с которой вы пришли, и ваш IP-адрес.",
    ]},
    "tr": {"titulo": "Ziyaretlerin kaynağı", "paragrafos": [
        "Ziyaretlerin nereden geldiğini bilmek için her birinin kaynağını genel kategoriler halinde (örneğin “arama”, “sosyal ağ”, “e-posta”, “başka site” veya “doğrudan”) ve bağlantı taşıyorsa kampanya adını (utm_source) kaydederiz. Geldiğiniz sayfanın tam adresini ve IP adresinizi asla saklamayız.",
    ]},
    "zh": {"titulo": "访问来源", "paragrafos": [
        "为了了解访问从何而来，我们按一般类别记录每次访问的来源（例如“搜索”“社交网络”“电子邮件”“其他网站”或“直接访问”），如果链接带有活动名称（utm_source），也会记录。我们绝不保存您所来自页面的完整地址，也不保存您的 IP 地址。",
    ]},
    "ja": {"titulo": "訪問の流入元", "paragrafos": [
        "訪問がどこから来たかを知るため、各訪問の流入元を一般的なカテゴリ（たとえば「検索」「SNS」「メール」「その他のサイト」「直接」）で記録し、リンクに含まれていればキャンペーン名（utm_source）も記録します。訪問元ページの完全なアドレスやIPアドレスは保存しません。",
    ]},
    "ko": {"titulo": "방문 경로", "paragrafos": [
        "방문이 어디에서 오는지 알기 위해 각 방문의 경로를 일반적인 범주(예: “검색”, “소셜 네트워크”, “이메일”, “다른 사이트”, “직접”)로 기록하고, 링크에 포함되어 있으면 캠페인 이름(utm_source)도 기록합니다. 방문하신 이전 페이지의 전체 주소나 IP 주소는 절대 저장하지 않습니다.",
    ]},
    "hi": {"titulo": "विज़िट कहाँ से आती हैं", "paragrafos": [
        "यह जानने के लिए कि विज़िट कहाँ से आती हैं, हम हर विज़िट का स्रोत सामान्य श्रेणियों में दर्ज करते हैं (जैसे “खोज”, “सोशल नेटवर्क”, “ईमेल”, “अन्य साइट” या “सीधे”) और, यदि लिंक में हो, तो अभियान का नाम (utm_source)। आप जिस पेज से आए उसका पूरा पता और आपका IP पता हम कभी सहेजते नहीं।",
    ]},
    "ca": {"titulo": "Origen de les visites", "paragrafos": [
        "Per saber d'on vénen les visites, registrem l'origen de cadascuna en categories generals (per exemple «cerca», «xarxa social», «correu», «un altre lloc» o «directa») i, si l'enllaç el porta, el nom de campanya (utm_source). Mai no desem l'adreça completa de la pàgina d'on veniu ni la vostra adreça IP.",
    ]},
    "uk": {"titulo": "Звідки приходять відвідувачі", "paragrafos": [
        "Щоб знати, звідки приходять відвідувачі, ми записуємо джерело кожного візиту в загальних категоріях (наприклад, «пошук», «соціальна мережа», «e-mail», «інший сайт» або «напряму») і, якщо посилання його містить, назву кампанії (utm_source). Ми ніколи не зберігаємо повну адресу сторінки, з якої ви прийшли, та вашу IP-адресу.",
    ]},
    "id": {"titulo": "Asal kunjungan", "paragrafos": [
        "Untuk mengetahui dari mana kunjungan berasal, kami mencatat asal tiap kunjungan dalam kategori umum (misalnya “pencarian”, “jejaring sosial”, “email”, “situs lain” atau “langsung”) dan, jika tautannya memuat, nama kampanye (utm_source). Kami tidak pernah menyimpan alamat lengkap halaman asal Anda maupun alamat IP Anda.",
    ]},
    "vi": {"titulo": "Nguồn của các lượt truy cập", "paragrafos": [
        "Để biết lượt truy cập đến từ đâu, chúng tôi ghi lại nguồn của từng lượt theo các nhóm chung (ví dụ “tìm kiếm”, “mạng xã hội”, “email”, “trang khác” hoặc “trực tiếp”) và, nếu liên kết có, tên chiến dịch (utm_source). Chúng tôi không bao giờ lưu địa chỉ đầy đủ của trang bạn đến từ đâu, cũng như địa chỉ IP của bạn.",
    ]},
}


def aplicar(pagina: dict, lingua: str) -> dict:
    """A página de privacidade com a secção da origem das visitas, no fim (`pagina` já copiada e preenchida)."""
    d = TEXTOS.get(lingua, TEXTOS["pt"])
    pagina["seccoes"].append({"titulo": d["titulo"], "paragrafos": list(d["paragrafos"])})
    return pagina
