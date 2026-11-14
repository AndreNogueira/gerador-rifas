"""O que a Política de privacidade diz quando o serviço mostra anúncios (variável `ADSENSE_CLIENTE`, ver `docs/ADSENSE.md`).

O texto normal (`legal/<língua>.py`) promete «sem anúncios» e «sem cookies de publicidade»: com os anúncios ligados isso deixa de ser verdade, por isso
`textos_legais.pagina("privacidade", …)` troca, **só nesse caso**, a 1.ª frase do Resumo (`RESUMO`) e a última do parágrafo «No seu browser» (`COOKIES`)
e acrescenta uma secção «Publicidade» (`SECCAO`) depois da do browser. Um texto por língua, com as mesmas ideias; provisório como os restantes
(sem revisão nativa nem jurídica: o aviso da página diz que, havendo divergência, vale o português).
"""
from __future__ import annotations

import re

_FIM = re.compile(r"\.(?=\s|$)|[。।]")        # onde acaba uma frase (ponto, ponto chinês/japonês, danda hindi)

PT = {
    "resumo": "Não há contas. O site mostra anúncios da Google (AdSense), que podem usar cookies; fora isso, não usamos ferramentas de seguimento de terceiros.",
    "cookies": "Os únicos cookies de publicidade são os dos anúncios (ver «Publicidade»).",
    "seccao": {
        "titulo": "Publicidade",
        "paragrafos": [
            "Este site mostra anúncios da Google (AdSense) para se financiar. A Google e os seus parceiros podem usar cookies e identificadores para mostrar anúncios, personalizados ou não, e medir os resultados; nós não recebemos esses dados nem os ligamos a nenhum ficheiro seu.",
            "Os anúncios só aparecem depois de escolher na mensagem de consentimento que a Google mostra ao abrir o site (obrigatória no Espaço Económico Europeu e no Reino Unido); a base legal dos cookies de publicidade é o seu consentimento (RGPD, artigo 6.º, n.º 1, alínea a), e pode rever a escolha nas opções de privacidade dessa mensagem. Os anúncios nunca aparecem nos ficheiros gerados, no painel nem na app Windows.",
            "Saiba como a Google usa os dados em policies.google.com/technologies/partner-sites e gira os anúncios personalizados em adssettings.google.com.",
        ],
    },
}

TEXTOS: dict[str, dict] = {
    "pt": PT,
    "en": {
        "resumo": "There are no accounts. The site shows Google ads (AdSense), which may use cookies; apart from that, we use no third-party tracking tools.",
        "cookies": "The only advertising cookies are those of the ads (see “Advertising”).",
        "seccao": {
            "titulo": "Advertising",
            "paragrafos": [
                "This site shows Google ads (AdSense) to fund itself. Google and its partners may use cookies and identifiers to show ads, personalized or not, and to measure results; we do not receive that data nor link it to any of your files.",
                "Ads only appear after you choose in the consent message that Google shows when you open the site (required in the European Economic Area and the United Kingdom); the legal basis for advertising cookies is your consent (GDPR, Article 6(1)(a)), and you can review your choice in the privacy options of that message. Ads never appear in the generated files, in the dashboard or in the Windows app.",
                "See how Google uses data at policies.google.com/technologies/partner-sites and manage personalized ads at adssettings.google.com.",
            ],
        },
    },
    "es": {
        "resumo": "No hay cuentas. El sitio muestra anuncios de Google (AdSense), que pueden usar cookies; aparte de eso, no usamos herramientas de seguimiento de terceros.",
        "cookies": "Las únicas cookies de publicidad son las de los anuncios (véase «Publicidad»).",
        "seccao": {
            "titulo": "Publicidad",
            "paragrafos": [
                "Este sitio muestra anuncios de Google (AdSense) para financiarse. Google y sus socios pueden usar cookies e identificadores para mostrar anuncios, personalizados o no, y medir los resultados; nosotros no recibimos esos datos ni los vinculamos a ningún archivo suyo.",
                "Los anuncios solo aparecen después de elegir en el mensaje de consentimiento que Google muestra al abrir el sitio (obligatorio en el Espacio Económico Europeo y el Reino Unido); la base jurídica de las cookies de publicidad es su consentimiento (RGPD, artículo 6, apartado 1, letra a), y puede revisar su elección en las opciones de privacidad de ese mensaje. Los anuncios nunca aparecen en los archivos generados, en el panel ni en la app de Windows.",
                "Consulte cómo usa Google los datos en policies.google.com/technologies/partner-sites y gestione los anuncios personalizados en adssettings.google.com.",
            ],
        },
    },
    "fr": {
        "resumo": "Il n'y a pas de comptes. Le site affiche des publicités Google (AdSense), qui peuvent utiliser des cookies ; hormis cela, nous n'utilisons aucun outil de suivi tiers.",
        "cookies": "Les seuls cookies publicitaires sont ceux des annonces (voir « Publicité »).",
        "seccao": {
            "titulo": "Publicité",
            "paragrafos": [
                "Ce site affiche des publicités Google (AdSense) pour se financer. Google et ses partenaires peuvent utiliser des cookies et des identifiants pour afficher des annonces, personnalisées ou non, et mesurer les résultats ; nous ne recevons pas ces données et ne les relions à aucun de vos fichiers.",
                "Les annonces n'apparaissent qu'après votre choix dans le message de consentement que Google affiche à l'ouverture du site (obligatoire dans l'Espace économique européen et au Royaume-Uni) ; la base légale des cookies publicitaires est votre consentement (RGPD, article 6, paragraphe 1, point a), et vous pouvez revoir votre choix dans les options de confidentialité de ce message. Les annonces n'apparaissent jamais dans les fichiers générés, dans le tableau de bord ni dans l'appli Windows.",
                "Découvrez comment Google utilise les données sur policies.google.com/technologies/partner-sites et gérez les annonces personnalisées sur adssettings.google.com.",
            ],
        },
    },
    "de": {
        "resumo": "Es gibt keine Konten. Die Website zeigt Google-Anzeigen (AdSense), die Cookies verwenden können; darüber hinaus nutzen wir keine Tracking-Werkzeuge Dritter.",
        "cookies": "Die einzigen Werbe-Cookies sind die der Anzeigen (siehe „Werbung“).",
        "seccao": {
            "titulo": "Werbung",
            "paragrafos": [
                "Diese Website zeigt Google-Anzeigen (AdSense), um sich zu finanzieren. Google und seine Partner können Cookies und Kennungen verwenden, um Anzeigen (personalisiert oder nicht) auszuspielen und Ergebnisse zu messen; wir erhalten diese Daten nicht und verknüpfen sie mit keiner Ihrer Dateien.",
                "Anzeigen erscheinen erst, nachdem Sie in der Einwilligungsmeldung gewählt haben, die Google beim Öffnen der Website anzeigt (im Europäischen Wirtschaftsraum und im Vereinigten Königreich vorgeschrieben); Rechtsgrundlage der Werbe-Cookies ist Ihre Einwilligung (DSGVO, Artikel 6 Absatz 1 Buchstabe a), und Sie können Ihre Wahl in den Datenschutzoptionen dieser Meldung ändern. Anzeigen erscheinen nie in den erzeugten Dateien, im Dashboard oder in der Windows-App.",
                "Wie Google Daten verwendet, steht unter policies.google.com/technologies/partner-sites; personalisierte Anzeigen verwalten Sie unter adssettings.google.com.",
            ],
        },
    },
    "it": {
        "resumo": "Non ci sono account. Il sito mostra annunci di Google (AdSense), che possono usare cookie; a parte questo, non usiamo strumenti di tracciamento di terzi.",
        "cookies": "Gli unici cookie pubblicitari sono quelli degli annunci (vedere «Pubblicità»).",
        "seccao": {
            "titulo": "Pubblicità",
            "paragrafos": [
                "Questo sito mostra annunci di Google (AdSense) per finanziarsi. Google e i suoi partner possono usare cookie e identificatori per mostrare annunci, personalizzati o no, e misurarne i risultati; noi non riceviamo questi dati né li colleghiamo a nessuno dei suoi file.",
                "Gli annunci compaiono solo dopo la sua scelta nel messaggio di consenso che Google mostra all'apertura del sito (obbligatorio nello Spazio economico europeo e nel Regno Unito); la base giuridica dei cookie pubblicitari è il suo consenso (GDPR, articolo 6, paragrafo 1, lettera a), e può rivedere la scelta nelle opzioni sulla privacy di quel messaggio. Gli annunci non compaiono mai nei file generati, nel pannello né nell'app Windows.",
                "Veda come Google usa i dati su policies.google.com/technologies/partner-sites e gestisca gli annunci personalizzati su adssettings.google.com.",
            ],
        },
    },
    "nl": {
        "resumo": "Er zijn geen accounts. De site toont Google-advertenties (AdSense), die cookies kunnen gebruiken; verder gebruiken we geen volgtools van derden.",
        "cookies": "De enige advertentiecookies zijn die van de advertenties (zie ‘Advertenties’).",
        "seccao": {
            "titulo": "Advertenties",
            "paragrafos": [
                "Deze site toont Google-advertenties (AdSense) om zichzelf te financieren. Google en zijn partners kunnen cookies en identificatiegegevens gebruiken om advertenties te tonen, gepersonaliseerd of niet, en de resultaten te meten; wij ontvangen die gegevens niet en koppelen ze aan geen enkel bestand van u.",
                "Advertenties verschijnen pas nadat u hebt gekozen in het toestemmingsbericht dat Google toont bij het openen van de site (verplicht in de Europese Economische Ruimte en het Verenigd Koninkrijk); de rechtsgrond voor advertentiecookies is uw toestemming (AVG, artikel 6, lid 1, onder a), en u kunt uw keuze herzien in de privacyopties van dat bericht. Advertenties verschijnen nooit in de gegenereerde bestanden, in het dashboard of in de Windows-app.",
                "Lees hoe Google gegevens gebruikt op policies.google.com/technologies/partner-sites en beheer gepersonaliseerde advertenties op adssettings.google.com.",
            ],
        },
    },
    "pl": {
        "resumo": "Nie ma kont. Strona wyświetla reklamy Google (AdSense), które mogą używać plików cookie; poza tym nie używamy zewnętrznych narzędzi śledzących.",
        "cookies": "Jedyne reklamowe pliki cookie pochodzą z reklam (zob. „Reklamy”).",
        "seccao": {
            "titulo": "Reklamy",
            "paragrafos": [
                "Ta strona wyświetla reklamy Google (AdSense), aby się finansować. Google i jego partnerzy mogą używać plików cookie i identyfikatorów do wyświetlania reklam, spersonalizowanych lub nie, oraz do mierzenia wyników; nie otrzymujemy tych danych ani nie łączymy ich z żadnym z twoich plików.",
                "Reklamy pojawiają się dopiero po dokonaniu wyboru w komunikacie o zgodzie, który Google wyświetla po otwarciu strony (obowiązkowym w Europejskim Obszarze Gospodarczym i Wielkiej Brytanii); podstawą prawną reklamowych plików cookie jest zgoda (RODO, art. 6 ust. 1 lit. a), a wybór można zmienić w opcjach prywatności tego komunikatu. Reklamy nigdy nie pojawiają się w wygenerowanych plikach, w panelu ani w aplikacji Windows.",
                "Jak Google wykorzystuje dane, sprawdzisz na policies.google.com/technologies/partner-sites, a spersonalizowanymi reklamami zarządzasz na adssettings.google.com.",
            ],
        },
    },
    "sv": {
        "resumo": "Det finns inga konton. Webbplatsen visar Google-annonser (AdSense), som kan använda cookies; i övrigt använder vi inga spårningsverktyg från tredje part.",
        "cookies": "De enda reklamcookies är annonsernas egna (se ”Annonser”).",
        "seccao": {
            "titulo": "Annonser",
            "paragrafos": [
                "Den här webbplatsen visar Google-annonser (AdSense) för att finansiera sig själv. Google och dess partner kan använda cookies och identifierare för att visa annonser, personliga eller inte, och mäta resultat; vi får inte dessa uppgifter och kopplar dem inte till någon av dina filer.",
                "Annonser visas först efter att du har valt i det samtyckesmeddelande som Google visar när du öppnar webbplatsen (obligatoriskt i Europeiska ekonomiska samarbetsområdet och Storbritannien); den rättsliga grunden för reklamcookies är ditt samtycke (GDPR, artikel 6.1 a), och du kan ändra ditt val i meddelandets integritetsalternativ. Annonser visas aldrig i de skapade filerna, i panelen eller i Windows-appen.",
                "Läs hur Google använder uppgifter på policies.google.com/technologies/partner-sites och hantera personliga annonser på adssettings.google.com.",
            ],
        },
    },
    "cs": {
        "resumo": "Nejsou zde žádné účty. Web zobrazuje reklamy Google (AdSense), které mohou používat cookies; jinak nepoužíváme žádné sledovací nástroje třetích stran.",
        "cookies": "Jediné reklamní cookies jsou ty od reklam (viz „Reklama“).",
        "seccao": {
            "titulo": "Reklama",
            "paragrafos": [
                "Tento web zobrazuje reklamy Google (AdSense), aby se financoval. Google a jeho partneři mohou používat cookies a identifikátory k zobrazování reklam, personalizovaných i ne, a k měření výsledků; tyto údaje neobdržíme ani je nespojujeme s žádným vaším souborem.",
                "Reklamy se zobrazí až poté, co si vyberete ve zprávě o souhlasu, kterou Google zobrazí při otevření webu (povinné v Evropském hospodářském prostoru a ve Spojeném království); právním základem reklamních cookies je váš souhlas (GDPR, čl. 6 odst. 1 písm. a) a svou volbu můžete změnit v možnostech soukromí této zprávy. Reklamy se nikdy nezobrazují ve vytvořených souborech, v panelu ani v aplikaci pro Windows.",
                "Jak Google používá data, zjistíte na policies.google.com/technologies/partner-sites a personalizované reklamy spravujete na adssettings.google.com.",
            ],
        },
    },
    "ro": {
        "resumo": "Nu există conturi. Site-ul afișează reclame Google (AdSense), care pot folosi cookie-uri; în rest, nu folosim instrumente de urmărire ale terților.",
        "cookies": "Singurele cookie-uri publicitare sunt cele ale reclamelor (vezi „Publicitate”).",
        "seccao": {
            "titulo": "Publicitate",
            "paragrafos": [
                "Acest site afișează reclame Google (AdSense) pentru a se finanța. Google și partenerii săi pot folosi cookie-uri și identificatori pentru a afișa reclame, personalizate sau nu, și pentru a măsura rezultatele; noi nu primim aceste date și nu le legăm de niciun fișier al dumneavoastră.",
                "Reclamele apar doar după ce alegeți în mesajul de consimțământ pe care Google îl afișează la deschiderea site-ului (obligatoriu în Spațiul Economic European și în Regatul Unit); temeiul legal al cookie-urilor publicitare este consimțământul dumneavoastră (RGPD, articolul 6 alineatul (1) litera a), iar alegerea poate fi revizuită în opțiunile de confidențialitate ale mesajului. Reclamele nu apar niciodată în fișierele generate, în panou sau în aplicația Windows.",
                "Aflați cum folosește Google datele la policies.google.com/technologies/partner-sites și gestionați reclamele personalizate la adssettings.google.com.",
            ],
        },
    },
    "el": {
        "resumo": "Δεν υπάρχουν λογαριασμοί. Ο ιστότοπος εμφανίζει διαφημίσεις της Google (AdSense), που μπορεί να χρησιμοποιούν cookies· εκτός αυτού, δεν χρησιμοποιούμε εργαλεία παρακολούθησης τρίτων.",
        "cookies": "Τα μόνα διαφημιστικά cookies είναι αυτά των διαφημίσεων (βλ. «Διαφήμιση»).",
        "seccao": {
            "titulo": "Διαφήμιση",
            "paragrafos": [
                "Αυτός ο ιστότοπος εμφανίζει διαφημίσεις της Google (AdSense) για να χρηματοδοτείται. Η Google και οι συνεργάτες της μπορεί να χρησιμοποιούν cookies και αναγνωριστικά για να εμφανίζουν διαφημίσεις, εξατομικευμένες ή μη, και να μετρούν τα αποτελέσματα· εμείς δεν λαμβάνουμε αυτά τα δεδομένα ούτε τα συνδέουμε με κανένα αρχείο σας.",
                "Οι διαφημίσεις εμφανίζονται μόνο αφού επιλέξετε στο μήνυμα συγκατάθεσης που εμφανίζει η Google όταν ανοίγετε τον ιστότοπο (υποχρεωτικό στον Ευρωπαϊκό Οικονομικό Χώρο και στο Ηνωμένο Βασίλειο)· η νομική βάση των διαφημιστικών cookies είναι η συγκατάθεσή σας (ΓΚΠΔ, άρθρο 6 παρ. 1 στοιχ. α) και μπορείτε να αναθεωρήσετε την επιλογή σας στις επιλογές απορρήτου του μηνύματος. Οι διαφημίσεις δεν εμφανίζονται ποτέ στα αρχεία που δημιουργούνται, στον πίνακα ελέγχου ή στην εφαρμογή Windows.",
                "Δείτε πώς χρησιμοποιεί η Google τα δεδομένα στο policies.google.com/technologies/partner-sites και διαχειριστείτε τις εξατομικευμένες διαφημίσεις στο adssettings.google.com.",
            ],
        },
    },
    "ru": {
        "resumo": "Учётных записей нет. На сайте показывается реклама Google (AdSense), которая может использовать файлы cookie; кроме этого, мы не применяем сторонние средства отслеживания.",
        "cookies": "Единственные рекламные cookie — это cookie самой рекламы (см. «Реклама»).",
        "seccao": {
            "titulo": "Реклама",
            "paragrafos": [
                "Чтобы финансировать себя, сайт показывает рекламу Google (AdSense). Google и его партнёры могут использовать cookie и идентификаторы для показа рекламы, персонализированной или нет, и измерения результатов; мы не получаем эти данные и не связываем их ни с одним вашим файлом.",
                "Реклама появляется только после того, как вы сделаете выбор в сообщении о согласии, которое Google показывает при открытии сайта (обязательно в Европейской экономической зоне и Великобритании); правовое основание для рекламных cookie — ваше согласие (GDPR, статья 6, пункт 1, подпункт a), и вы можете пересмотреть выбор в параметрах конфиденциальности этого сообщения. Реклама никогда не появляется в созданных файлах, в панели и в приложении для Windows.",
                "О том, как Google использует данные, читайте на policies.google.com/technologies/partner-sites, а персонализированной рекламой управляйте на adssettings.google.com.",
            ],
        },
    },
    "tr": {
        "resumo": "Hesap yoktur. Site, çerez kullanabilen Google reklamları (AdSense) gösterir; bunun dışında üçüncü taraf izleme araçları kullanmayız.",
        "cookies": "Tek reklam çerezleri reklamların kendi çerezleridir (bkz. “Reklam”).",
        "seccao": {
            "titulo": "Reklam",
            "paragrafos": [
                "Bu site, kendini finanse etmek için Google reklamları (AdSense) gösterir. Google ve ortakları, kişiselleştirilmiş veya kişiselleştirilmemiş reklamlar göstermek ve sonuçları ölçmek için çerezler ve tanımlayıcılar kullanabilir; biz bu verileri almayız ve hiçbir dosyanızla ilişkilendirmeyiz.",
                "Reklamlar yalnızca siteyi açtığınızda Google'ın gösterdiği onay mesajında seçim yaptıktan sonra görünür (Avrupa Ekonomik Alanı ve Birleşik Krallık'ta zorunludur); reklam çerezlerinin hukuki dayanağı onayınızdır (GDPR, madde 6/1-a) ve seçiminizi o mesajın gizlilik seçeneklerinden gözden geçirebilirsiniz. Reklamlar oluşturulan dosyalarda, panelde veya Windows uygulamasında asla görünmez.",
                "Google'ın verileri nasıl kullandığını policies.google.com/technologies/partner-sites adresinde görün, kişiselleştirilmiş reklamları adssettings.google.com adresinden yönetin.",
            ],
        },
    },
    "zh": {
        "resumo": "没有账户。网站会显示 Google 广告（AdSense），这些广告可能使用 Cookie；除此之外，我们不使用任何第三方跟踪工具。",
        "cookies": "唯一的广告 Cookie 来自广告本身（见“广告”）。",
        "seccao": {
            "titulo": "广告",
            "paragrafos": [
                "本网站显示 Google 广告（AdSense）以维持运营。Google 及其合作伙伴可能使用 Cookie 和标识符来展示广告（个性化或非个性化）并衡量效果；我们不会收到这些数据，也不会把它们与您的任何文件关联。",
                "只有在您于打开网站时 Google 显示的同意提示中做出选择之后，才会出现广告（在欧洲经济区和英国为强制要求）；广告 Cookie 的法律依据是您的同意（GDPR 第 6 条第 1 款 a 项），您可以在该提示的隐私选项中重新选择。广告绝不会出现在生成的文件、管理面板或 Windows 应用中。",
                "了解 Google 如何使用数据，请访问 policies.google.com/technologies/partner-sites；个性化广告可在 adssettings.google.com 管理。",
            ],
        },
    },
    "ja": {
        "resumo": "アカウントはありません。このサイトは Google の広告（AdSense）を表示し、Cookie が使われることがあります。それ以外に、第三者の追跡ツールは使いません。",
        "cookies": "広告用の Cookie は広告そのものが使うものだけです（「広告」を参照）。",
        "seccao": {
            "titulo": "広告",
            "paragrafos": [
                "このサイトは運営費をまかなうため Google の広告（AdSense）を表示します。Google とそのパートナーは、パーソナライズの有無にかかわらず広告を表示し成果を測定するために Cookie や識別子を使うことがあります。私たちはそのデータを受け取らず、あなたのどのファイルとも結び付けません。",
                "広告は、サイトを開いたときに Google が表示する同意メッセージで選択した後にのみ表示されます（欧州経済領域と英国では必須）。広告 Cookie の法的根拠はあなたの同意（GDPR 第6条第1項(a)）であり、選択はそのメッセージのプライバシー設定でいつでも見直せます。広告は、生成されたファイル、管理パネル、Windows アプリには表示されません。",
                "Google のデータの使い方は policies.google.com/technologies/partner-sites で、パーソナライズ広告の管理は adssettings.google.com で確認できます。",
            ],
        },
    },
    "ko": {
        "resumo": "계정은 없습니다. 이 사이트는 쿠키를 사용할 수 있는 Google 광고(AdSense)를 표시하며, 그 외에는 제3자 추적 도구를 사용하지 않습니다.",
        "cookies": "광고용 쿠키는 광고 자체의 쿠키뿐입니다(‘광고’ 참조).",
        "seccao": {
            "titulo": "광고",
            "paragrafos": [
                "이 사이트는 운영 비용을 충당하기 위해 Google 광고(AdSense)를 표시합니다. Google과 파트너는 맞춤 또는 일반 광고를 표시하고 성과를 측정하기 위해 쿠키와 식별자를 사용할 수 있으며, 저희는 그 데이터를 받지 않고 귀하의 어떤 파일과도 연결하지 않습니다.",
                "광고는 사이트를 열 때 Google이 표시하는 동의 메시지에서 선택한 뒤에만 나타납니다(유럽경제지역과 영국에서는 필수). 광고 쿠키의 법적 근거는 귀하의 동의(GDPR 제6조 제1항 a호)이며, 그 메시지의 개인정보 옵션에서 선택을 다시 검토할 수 있습니다. 광고는 생성된 파일, 관리 패널, Windows 앱에는 절대 표시되지 않습니다.",
                "Google이 데이터를 사용하는 방식은 policies.google.com/technologies/partner-sites에서, 맞춤 광고 관리는 adssettings.google.com에서 확인하세요.",
            ],
        },
    },
    "hi": {
        "resumo": "कोई खाते नहीं हैं। साइट Google के विज्ञापन (AdSense) दिखाती है, जो कुकी का उपयोग कर सकते हैं; इसके अलावा हम तीसरे पक्ष के ट्रैकिंग टूल का उपयोग नहीं करते।",
        "cookies": "विज्ञापन-संबंधी कुकी केवल विज्ञापनों की अपनी कुकी हैं (देखें “विज्ञापन”)।",
        "seccao": {
            "titulo": "विज्ञापन",
            "paragrafos": [
                "यह साइट अपना खर्च चलाने के लिए Google के विज्ञापन (AdSense) दिखाती है। Google और उसके साझेदार विज्ञापन दिखाने (वैयक्तिकृत या नहीं) और परिणाम मापने के लिए कुकी और पहचानकर्ताओं का उपयोग कर सकते हैं; हमें यह डेटा नहीं मिलता और हम इसे आपकी किसी फ़ाइल से नहीं जोड़ते।",
                "विज्ञापन तभी दिखते हैं जब आप साइट खोलने पर Google द्वारा दिखाए गए सहमति संदेश में अपनी पसंद चुन लेते हैं (यूरोपीय आर्थिक क्षेत्र और यूनाइटेड किंगडम में अनिवार्य); विज्ञापन कुकी का कानूनी आधार आपकी सहमति है (GDPR, अनुच्छेद 6(1)(a)), और आप उस संदेश के गोपनीयता विकल्पों में अपनी पसंद दोबारा देख सकते हैं। विज्ञापन कभी बनाई गई फ़ाइलों, डैशबोर्ड या Windows ऐप में नहीं दिखते।",
                "Google डेटा का उपयोग कैसे करता है, यह policies.google.com/technologies/partner-sites पर देखें और वैयक्तिकृत विज्ञापन adssettings.google.com पर प्रबंधित करें।",
            ],
        },
    },
}


def _fins(p: str) -> list:
    return [m.end() for m in _FIM.finditer(p)]


def trocar_primeira_frase(paragrafo: str, nova: str) -> str:
    """A 1.ª frase do parágrafo passa a ser `nova` (o resto fica)."""
    fins = _fins(paragrafo)
    if not fins:
        return nova
    resto = paragrafo[fins[0]:]
    return nova + (" " if resto[:1].isspace() else "") + resto.lstrip()


def trocar_ultima_frase(paragrafo: str, nova: str) -> str:
    """A última frase do parágrafo passa a ser `nova` (o resto fica)."""
    fins = _fins(paragrafo)
    if len(fins) < 2:
        return nova
    antes = paragrafo[:fins[-2]]
    return antes + (" " if paragrafo[fins[-2]:fins[-2] + 1].isspace() else "") + nova


def aplicar(pagina: dict, lingua: str) -> dict:
    """A página de privacidade com os anúncios (`pagina` já copiada e preenchida; devolve-a alterada)."""
    d = TEXTOS.get(lingua, PT)
    seccoes = pagina["seccoes"]
    seccoes[0]["paragrafos"][0] = trocar_primeira_frase(seccoes[0]["paragrafos"][0], d["resumo"])
    seccoes[2]["paragrafos"][-1] = trocar_ultima_frase(seccoes[2]["paragrafos"][-1], d["cookies"])
    seccoes.insert(3, {"titulo": d["seccao"]["titulo"], "paragrafos": list(d["seccao"]["paragrafos"])})
    return pagina


# as linguas novas trazem estes textos no seu proprio `legal/<lingua>.py` (ver docs/LINGUAS.md)
from importlib import import_module  # noqa: E402

from .legal import LINGUAS_NOVAS  # noqa: E402

for _lg in LINGUAS_NOVAS:
    TEXTOS[_lg] = import_module(f"{__package__}.legal.{_lg}").ANUNCIOS
