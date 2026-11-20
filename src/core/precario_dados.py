"""Os dados do catálogo do preçário (`core/precario_catalogo.py` lê-os e valida-os): categorias, artigos e ocasiões, nas 22 línguas, uma linha por entrada.

Formato de uma linha de artigo: `id|emoji|categoria|região|nome pt|en|es|fr|de|it|nl|pl|sv|cs|ro|el|ru|tr|zh|ja|ko|hi|ca|uk|id|vi[|nome pt-br]` (a ordem das línguas é `LINGUAS`
abaixo). `emoji` é o código hexadecimal do emoji (a imagem do artigo, fase 3: `core/icones_precario/`). `região` é vazio (qualquer língua), `pt` (só com a língua de Portugal) ou `br` (só com o
português do Brasil). Um nome que é igual em todas as línguas (pratos locais, nomes próprios) escreve-se `=Nome`. Sem o 23.º campo o nome em pt-br deriva-se do pt (`core/ptbr.py`).
Formato de `ICONES`: `id do artigo|emojis alternativos (até 4, separados por vírgulas)`: com o `emoji` do artigo são até 5 imagens à escolha (a primeira é a de omissão).
Formato de uma ocasião: `id|desenho da galeria|região|meses em que é a sugerida (1-12, separados por vírgulas)|artigos (ids por vírgulas)|nome pt|…|nome vi`.
As traduções não tiveram revisão por falantes nativos.
"""

LINGUAS = ("pt", "en", "es", "fr", "de", "it", "nl", "pl", "sv", "cs", "ro", "el", "ru", "tr", "zh", "ja", "ko", "hi", "ca", "uk", "id", "vi")

CATEGORIAS = """
menus|Menus e combos|Menus and combos|Menús y combos|Menus et formules|Menüs und Kombis|Menu e combo|Menu's en combo's|Zestawy i menu|Menyer och kombos|Menu a kombinace|Meniuri și combo-uri|Μενού και συνδυασμοί|Меню и комбо|Menüler ve kombolar|套餐与组合|セットメニュー|세트 메뉴|मेन्यू और कॉम्बो|Menús i combos|Меню та комбо|Menu dan paket|Thực đơn và combo
bebidas|Bebidas|Drinks|Bebidas|Boissons|Getränke|Bevande|Drankjes|Napoje|Drycker|Nápoje|Băuturi|Ποτά|Напитки|İçecekler|饮品|ドリンク|음료|पेय|Begudes|Напої|Minuman|Đồ uống
alcool|Bebidas alcoólicas|Alcoholic drinks|Bebidas alcohólicas|Boissons alcoolisées|Alkoholische Getränke|Bevande alcoliche|Alcoholische dranken|Napoje alkoholowe|Alkoholhaltiga drycker|Alkoholické nápoje|Băuturi alcoolice|Αλκοολούχα ποτά|Алкогольные напитки|Alkollü içecekler|酒类|アルコール|주류|मदिरा|Begudes alcohòliques|Алкогольні напої|Minuman beralkohol|Đồ uống có cồn
quentes|Café e bebidas quentes|Coffee and hot drinks|Café y bebidas calientes|Café et boissons chaudes|Kaffee und Heißgetränke|Caffè e bevande calde|Koffie en warme dranken|Kawa i napoje gorące|Kaffe och varma drycker|Káva a teplé nápoje|Cafea și băuturi calde|Καφές και ζεστά ροφήματα|Кофе и горячие напитки|Kahve ve sıcak içecekler|咖啡与热饮|コーヒー・温かい飲み物|커피와 따뜻한 음료|कॉफ़ी और गर्म पेय|Cafè i begudes calentes|Кава та гарячі напої|Kopi dan minuman panas|Cà phê và đồ uống nóng
comida|Comida|Food|Comida|Nourriture|Essen|Cibo|Eten|Jedzenie|Mat|Jídlo|Mâncare|Φαγητό|Еда|Yiyecek|美食|フード|음식|खाना|Menjar|Їжа|Makanan|Đồ ăn
doces|Doces|Sweets|Dulces|Sucreries|Süßes|Dolci|Zoetigheden|Słodycze|Sötsaker|Sladkosti|Dulciuri|Γλυκά|Сладости|Tatlılar|甜点|スイーツ|디저트|मिठाइयाँ|Dolços|Солодощі|Kudapan manis|Đồ ngọt
jogos|Jogos e atividades|Games and activities|Juegos y actividades|Jeux et activités|Spiele und Aktivitäten|Giochi e attività|Spelletjes en activiteiten|Gry i atrakcje|Spel och aktiviteter|Hry a aktivity|Jocuri și activități|Παιχνίδια και δραστηριότητες|Игры и развлечения|Oyunlar ve etkinlikler|游戏与活动|ゲーム・アクティビティ|게임과 활동|खेल और गतिविधियाँ|Jocs i activitats|Ігри та розваги|Permainan dan kegiatan|Trò chơi và hoạt động
extras|Outros|Other|Otros|Autres|Sonstiges|Altro|Overig|Inne|Övrigt|Ostatní|Altele|Άλλα|Другое|Diğer|其他|その他|기타|अन्य|Altres|Інше|Lainnya|Khác
"""

ARTIGOS = """
agua|1f4a7|bebidas||Água|Water|Agua|Eau|Wasser|Acqua|Water|Woda|Vatten|Voda|Apă|Νερό|Вода|Su|水|水|물|पानी|Aigua|Вода|Air mineral|Nước
agua_gas|1f9ca|bebidas||Água com gás|Sparkling water|Agua con gas|Eau gazeuse|Mineralwasser mit Kohlensäure|Acqua frizzante|Bruisend water|Woda gazowana|Kolsyrat vatten|Perlivá voda|Apă carbogazoasă|Ανθρακούχο νερό|Газированная вода|Gazlı su|气泡水|炭酸水|탄산수|सोडा वॉटर|Aigua amb gas|Газована вода|Air soda|Nước có ga
refrigerante|1f964|bebidas||Refrigerante|Soft drink|Refresco|Boisson gazeuse|Limonade|Bibita gassata|Frisdrank|Napój gazowany|Läsk|Limonáda|Suc acidulat|Αναψυκτικό|Газировка|Gazlı içecek|汽水|ソフトドリンク|청량음료|कोल्ड ड्रिंक|Refresc|Солодка вода|Minuman soda|Nước ngọt
sumo|1f9c3|bebidas||Sumo|Juice|Zumo|Jus|Saft|Succo|Sap|Sok|Juice|Džus|Suc|Χυμός|Сок|Meyve suyu|果汁|ジュース|주스|जूस|Suc|Сік|Jus|Nước ép|Suco
sumo_laranja|1f34a|bebidas||Sumo de laranja|Orange juice|Zumo de naranja|Jus d'orange|Orangensaft|Succo d'arancia|Sinaasappelsap|Sok pomarańczowy|Apelsinjuice|Pomerančový džus|Suc de portocale|Χυμός πορτοκάλι|Апельсиновый сок|Portakal suyu|橙汁|オレンジジュース|오렌지 주스|संतरे का जूस|Suc de taronja|Апельсиновий сік|Jus jeruk|Nước cam|Suco de laranja
limonada|1f34b|bebidas||Limonada|Lemonade|Limonada|Citronnade|Limonade|Limonata|Limonade|Lemoniada|Lemonad|Limonáda|Limonadă|Λεμονάδα|Лимонад|Limonata|柠檬水|レモネード|레모네이드|नींबू पानी|Llimonada|Лимонад|Limun|Nước chanh
cha_gelado|1f9cb|bebidas||Chá gelado|Iced tea|Té helado|Thé glacé|Eistee|Tè freddo|IJsthee|Mrożona herbata|Iste|Ledový čaj|Ceai rece|Παγωμένο τσάι|Холодный чай|Buzlu çay|冰茶|アイスティー|아이스티|आइस्ड टी|Te gelat|Холодний чай|Es teh|Trà đá
leite_chocolate|1f95b|bebidas||Leite com chocolate|Chocolate milk|Leche con chocolate|Lait chocolaté|Schokomilch|Latte al cioccolato|Chocolademelk|Mleko czekoladowe|Chokladmjölk|Čokoládové mléko|Lapte cu ciocolată|Σοκολατούχο γάλα|Шоколадное молоко|Çikolatalı süt|巧克力牛奶|チョコレートミルク|초콜릿 우유|चॉकलेट दूध|Llet amb xocolata|Шоколадне молоко|Susu cokelat|Sữa sô-cô-la|Achocolatado
agua_coco|1f965|bebidas||Água de coco|Coconut water|Agua de coco|Eau de coco|Kokoswasser|Acqua di cocco|Kokoswater|Woda kokosowa|Kokosvatten|Kokosová voda|Apă de cocos|Νερό καρύδας|Кокосовая вода|Hindistan cevizi suyu|椰子水|ココナッツウォーター|코코넛 워터|नारियल पानी|Aigua de coco|Кокосова вода|Air kelapa|Nước dừa
cerveja|1f37a|alcool||Cerveja|Beer|Cerveza|Bière|Bier|Birra|Bier|Piwo|Öl|Pivo|Bere|Μπύρα|Пиво|Bira|啤酒|ビール|맥주|बीयर|Cervesa|Пиво|Bir|Bia
imperial|1f37b|alcool|pt|=Imperial
chopp|1f37a|alcool|br|=Chopp
vinho_tinto|1f377|alcool||Vinho tinto|Red wine|Vino tinto|Vin rouge|Rotwein|Vino rosso|Rode wijn|Czerwone wino|Rött vin|Červené víno|Vin roșu|Κόκκινο κρασί|Красное вино|Kırmızı şarap|红葡萄酒|赤ワイン|레드 와인|रेड वाइन|Vi negre|Червоне вино|Anggur merah|Rượu vang đỏ
vinho_branco|1f942|alcool||Vinho branco|White wine|Vino blanco|Vin blanc|Weißwein|Vino bianco|Witte wijn|Białe wino|Vitt vin|Bílé víno|Vin alb|Λευκό κρασί|Белое вино|Beyaz şarap|白葡萄酒|白ワイン|화이트 와인|व्हाइट वाइन|Vi blanc|Біле вино|Anggur putih|Rượu vang trắng
sangria|1f379|alcool||=Sangria
cocktail|1f378|alcool||=Cocktail
caipirinha|1f379|alcool|br|=Caipirinha
vinho_quente|1f377|alcool||Vinho quente|Mulled wine|Vino caliente|Vin chaud|Glühwein|Vin brulé|Glühwijn|Grzane wino|Glögg|Svařák|Vin fiert|Ζεστό κρασί|Глинтвейн|Sıcak şarap|热红酒|ホットワイン|뱅쇼|मल्ड वाइन|Vi calent|Глінтвейн|Anggur panas|Rượu vang nóng
quentao|2615|alcool|br|=Quentão
espumante|1f37e|alcool||Espumante|Sparkling wine|Vino espumoso|Mousseux|Sekt|Spumante|Mousserende wijn|Wino musujące|Mousserande vin|Šumivé víno|Vin spumant|Αφρώδης οίνος|Игристое|Köpüklü şarap|起泡酒|スパークリングワイン|스파클링 와인|स्पार्कलिंग वाइन|Escumós|Ігристе|Anggur bersoda|Rượu vang sủi
agua_pe|1f347|alcool|pt|=Água-pé
jeropiga|1f347|alcool|pt|=Jeropiga
cafe|2615|quentes||Café|Coffee|Café|Café|Kaffee|Caffè|Koffie|Kawa|Kaffe|Káva|Cafea|Καφές|Кофе|Kahve|咖啡|コーヒー|커피|कॉफ़ी|Cafè|Кава|Kopi|Cà phê
bica|2615|quentes|pt|=Bica
cha|1f375|quentes||Chá|Tea|Té|Thé|Tee|Tè|Thee|Herbata|Te|Čaj|Ceai|Τσάι|Чай|Çay|茶|お茶|차|चाय|Te|Чай|Teh|Trà
chocolate_quente|2615|quentes||Chocolate quente|Hot chocolate|Chocolate caliente|Chocolat chaud|Heiße Schokolade|Cioccolata calda|Warme chocolademelk|Gorąca czekolada|Varm choklad|Horká čokoláda|Ciocolată caldă|Ζεστή σοκολάτα|Горячий шоколад|Sıcak çikolata|热巧克力|ホットチョコレート|핫초콜릿|हॉट चॉकलेट|Xocolata calenta|Гарячий шоколад|Cokelat panas|Sô-cô-la nóng
hamburguer|1f354|comida||Hambúrguer|Burger|Hamburguesa|Hamburger|Burger|Hamburger|Hamburger|Hamburger|Hamburgare|Hamburger|Hamburger|Μπέργκερ|Бургер|Hamburger|汉堡|ハンバーガー|햄버거|बर्गर|Hamburguesa|Бургер|Burger|Hamburger
cachorro_quente|1f32d|comida||Cachorro-quente|Hot dog|Perrito caliente|Hot-dog|Hotdog|Hot dog|Hotdog|Hot dog|Korv med bröd|Hot dog|Hot dog|Χοτ ντογκ|Хот-дог|Sosisli sandviç|热狗|ホットドッグ|핫도그|हॉट डॉग|Hot dog|Хот-дог|Hot dog|Bánh mì xúc xích
pizza|1f355|comida||Pizza|Pizza|Pizza|Pizza|Pizza|Pizza|Pizza|Pizza|Pizza|Pizza|Pizza|Πίτσα|Пицца|Pizza|披萨|ピザ|피자|पिज़्ज़ा|Pizza|Піца|Pizza|Pizza
sandes|1f96a|comida||Sandes|Sandwich|Sándwich|Sandwich|Sandwich|Panino|Broodje|Kanapka|Smörgås|Sendvič|Sandviș|Σάντουιτς|Бутерброд|Sandviç|三明治|サンドイッチ|샌드위치|सैंडविच|Entrepà|Бутерброд|Roti lapis|Bánh mì kẹp|Sanduíche
bifana|1f956|comida|pt|=Bifana
prego|1f969|comida|pt|=Prego no pão
sardinha|1f41f|comida|pt|Sardinha assada|Grilled sardine|Sardina asada|Sardine grillée|Gegrillte Sardine|Sardina alla griglia|Gegrilde sardine|Grillowana sardynka|Grillad sardin|Grilovaná sardinka|Sardină la grătar|Σαρδέλα ψητή|Жареная сардина|Izgara sardalya|烤沙丁鱼|焼きイワシ|구운 정어리|ग्रिल्ड सार्डिन|Sardina a la brasa|Смажена сардина|Sarden bakar|Cá mòi nướng
caldo_verde|1f963|comida|pt|=Caldo verde
pao_chourico|1f956|comida|pt|=Pão com chouriço
frango_assado|1f357|comida||Frango assado|Roast chicken|Pollo asado|Poulet rôti|Brathähnchen|Pollo arrosto|Gebraden kip|Pieczony kurczak|Grillad kyckling|Pečené kuře|Pui la rotisor|Ψητό κοτόπουλο|Курица гриль|Izgara tavuk|烤鸡|ローストチキン|로스트 치킨|रोस्ट चिकन|Pollastre rostit|Курка гриль|Ayam panggang|Gà nướng
salsicha|1f356|comida||Salsicha grelhada|Grilled sausage|Salchicha a la parrilla|Saucisse grillée|Bratwurst|Salsiccia alla griglia|Gegrilde worst|Kiełbasa z grilla|Grillad korv|Grilovaná klobása|Cârnat la grătar|Λουκάνικο ψητό|Жареная сосиска|Izgara sosis|烤香肠|焼きソーセージ|구운 소시지|ग्रिल्ड सॉसेज|Salsitxa a la graella|Смажена ковбаска|Sosis panggang|Xúc xích nướng
batatas_fritas|1f35f|comida||Batatas fritas|Fries|Patatas fritas|Frites|Pommes frites|Patatine fritte|Friet|Frytki|Pommes frites|Hranolky|Cartofi prăjiți|Τηγανητές πατάτες|Картофель фри|Patates kızartması|薯条|フライドポテト|감자튀김|फ्राइज़|Patates fregides|Картопля фрі|Kentang goreng|Khoai tây chiên|Batata frita
salada|1f957|comida||Salada|Salad|Ensalada|Salade|Salat|Insalata|Salade|Sałatka|Sallad|Salát|Salată|Σαλάτα|Салат|Salata|沙拉|サラダ|샐러드|सलाद|Amanida|Салат|Salad|Salad
sopa|1f372|comida||Sopa|Soup|Sopa|Soupe|Suppe|Zuppa|Soep|Zupa|Soppa|Polévka|Supă|Σούπα|Суп|Çorba|汤|スープ|수프|सूप|Sopa|Суп|Sup|Súp
pipocas|1f37f|comida||Pipocas|Popcorn|Palomitas|Pop-corn|Popcorn|Popcorn|Popcorn|Popcorn|Popcorn|Popcorn|Floricele|Ποπ κορν|Попкорн|Patlamış mısır|爆米花|ポップコーン|팝콘|पॉपकॉर्न|Crispetes|Попкорн|Popcorn|Bắp rang|Pipoca
castanhas_assadas|1f330|comida||Castanhas assadas|Roasted chestnuts|Castañas asadas|Marrons grillés|Geröstete Maronen|Caldarroste|Gebrande kastanjes|Pieczone kasztany|Rostade kastanjer|Pečené kaštany|Castane coapte|Ψητά κάστανα|Жареные каштаны|Kestane kebabı|烤栗子|焼き栗|군밤|भुने शाहबलूत|Castanyes rostides|Печені каштани|Kastanye panggang|Hạt dẻ nướng
tremocos|1f95c|comida|pt|=Tremoços
coxinha|1f357|comida|br|=Coxinha
pastel|1f95f|comida|br|=Pastel
pao_de_queijo|1f9c0|comida|br|=Pão de queijo
espetinho|1f362|comida|br|=Espetinho
milho_cozido|1f33d|comida|br|=Milho cozido
pamonha|1f33d|comida|br|=Pamonha
canjica|1f35a|comida|br|=Canjica
tapioca|1f95e|comida|br|=Tapioca
bolo|1f370|doces||Bolo|Cake|Pastel|Gâteau|Kuchen|Torta|Taart|Ciasto|Tårta|Dort|Tort|Κέικ|Торт|Pasta|蛋糕|ケーキ|케이크|केक|Pastís|Торт|Kue|Bánh ngọt
cupcake|1f9c1|doces||=Cupcake
brownie|1f36b|doces||=Brownie
bolacha|1f36a|doces||Bolacha|Cookie|Galleta|Biscuit|Keks|Biscotto|Koekje|Ciastko|Kaka|Sušenka|Biscuit|Μπισκότο|Печенье|Kurabiye|饼干|クッキー|쿠키|कुकी|Galeta|Печиво|Kue kering|Bánh quy|Biscoito
donut|1f369|doces||=Donut
crepe|1f95e|doces||Crepe|Crêpe|Crepe|Crêpe|Crêpe|Crêpe|Crêpe|Naleśnik|Crêpe|Palačinka|Clătită|Κρέπα|Блин|Krep|可丽饼|クレープ|크레이프|क्रेप|Crep|Млинець|Crepe|Bánh crepe
waffle|1f9c7|doces||Waffle|Waffle|Gofre|Gaufre|Waffel|Waffle|Wafel|Gofr|Våffla|Vafle|Vafă|Βάφλα|Вафля|Waffle|华夫饼|ワッフル|와플|वैफल|Gofre|Вафля|Wafel|Bánh waffle
gelado|1f366|doces||Gelado|Ice cream|Helado|Glace|Eis|Gelato|IJs|Lody|Glass|Zmrzlina|Înghețată|Παγωτό|Мороженое|Dondurma|冰淇淋|アイスクリーム|아이스크림|आइसक्रीम|Gelat|Морозиво|Es krim|Kem|Sorvete
algodao_doce|1f36d|doces||Algodão-doce|Cotton candy|Algodón de azúcar|Barbe à papa|Zuckerwatte|Zucchero filato|Suikerspin|Wata cukrowa|Sockervadd|Cukrová vata|Vată de zahăr|Μαλλί της γριάς|Сахарная вата|Pamuk şeker|棉花糖|綿菓子|솜사탕|कॉटन कैंडी|Cotó de sucre|Цукрова вата|Arum manis|Kẹo bông gòn
maca_amor|1f34e|doces||Maçã do amor|Candy apple|Manzana de caramelo|Pomme d'amour|Liebesapfel|Mela caramellata|Suikerappel|Jabłko w karmelu|Kolaäpple|Jablko v karamelu|Măr în caramel|Μήλο καραμέλα|Яблоко в карамели|Elma şekeri|苹果糖|りんご飴|사과 사탕|कैंडी ऐप्पल|Poma d'amor|Яблуко в карамелі|Apel karamel|Táo bọc đường
rebucados|1f36c|doces||Rebuçados|Sweets|Caramelos|Bonbons|Bonbons|Caramelle|Snoep|Cukierki|Godis|Bonbóny|Bomboane|Καραμέλες|Конфеты|Şekerleme|糖果|キャンディ|사탕|मिठाइयाँ|Caramels|Цукерки|Permen|Kẹo|Balas
chocolate|1f36b|doces||Chocolate|Chocolate|Chocolate|Chocolat|Schokolade|Cioccolato|Chocolade|Czekolada|Choklad|Čokoláda|Ciocolată|Σοκολάτα|Шоколад|Çikolata|巧克力|チョコレート|초콜릿|चॉकलेट|Xocolata|Шоколад|Cokelat|Sô-cô-la
mousse|1f36e|doces||Mousse de chocolate|Chocolate mousse|Mousse de chocolate|Mousse au chocolat|Schokoladenmousse|Mousse al cioccolato|Chocolademousse|Mus czekoladowy|Chokladmousse|Čokoládová pěna|Mousse de ciocolată|Μους σοκολάτας|Шоколадный мусс|Çikolatalı mus|巧克力慕斯|チョコレートムース|초콜릿 무스|चॉकलेट मूस|Mousse de xocolata|Шоколадний мус|Mousse cokelat|Mousse sô-cô-la
fruta|1f353|doces||Fruta|Fruit|Fruta|Fruit|Obst|Frutta|Fruit|Owoce|Frukt|Ovoce|Fructe|Φρούτα|Фрукты|Meyve|水果|フルーツ|과일|फल|Fruita|Фрукти|Buah|Trái cây
pastel_de_nata|1f36e|doces|pt|=Pastel de nata
bola_de_berlim|1f369|doces|pt|=Bola de Berlim
arroz_doce|1f36e|doces|pt|=Arroz-doce
farturas|1f968|doces|pt|=Farturas
brigadeiro|1f36b|doces|br|=Brigadeiro
pacoca|1f95c|doces|br|=Paçoca
quindim|1f36e|doces|br|=Quindim
pe_de_moleque|1f95c|doces|br|=Pé de moleque
tiro_ao_alvo|1f3af|jogos||Tiro ao alvo|Target game|Tiro al blanco|Jeu de tir|Zielwerfen|Tiro al bersaglio|Doelwerpen|Rzutki do tarczy|Måltavla|Střelba na terč|Țintă|Βολές σε στόχο|Тир|Hedef atışı|打靶游戏|射的|사격 게임|निशानेबाज़ी|Tir al blanc|Тир|Lempar sasaran|Bắn mục tiêu
pesca|1f3a3|jogos||Pesca|Fishing game|Pesca|Pêche à la ligne|Angelspiel|Pesca|Hengelspel|Łowienie ryb|Fiskespel|Rybolov|Pescuit|Ψάρεμα|Рыбалка|Balık tutma|钓鱼游戏|魚釣り|낚시 게임|मछली पकड़ना|Pesca|Рибалка|Memancing|Câu cá
pintura_facial|1f3a8|jogos||Pintura facial|Face painting|Pintura facial|Maquillage|Gesichtsbemalung|Face painting|Schmink|Malowanie twarzy|Ansiktsmålning|Malování na obličej|Pictură pe față|Βάψιμο προσώπου|Аквагрим|Yüz boyama|脸部彩绘|フェイスペイント|페이스 페인팅|फेस पेंटिंग|Pintura facial|Аквагрим|Lukis wajah|Vẽ mặt
insuflavel|1f3f0|jogos||Insuflável|Bouncy castle|Castillo hinchable|Château gonflable|Hüpfburg|Castello gonfiabile|Springkussen|Dmuchany zamek|Hoppborg|Skákací hrad|Castel gonflabil|Φουσκωτό|Батут|Şişme oyun parkı|充气城堡|ふわふわドーム|에어바운스|इन्फ्लेटेबल|Castell inflable|Надувний батут|Istana balon|Nhà hơi|Pula-pula
carrossel|1f3a0|jogos||Carrossel|Carousel|Carrusel|Manège|Karussell|Giostra|Draaimolen|Karuzela|Karusell|Kolotoč|Carusel|Καρουζέλ|Карусель|Atlıkarınca|旋转木马|メリーゴーラウンド|회전목마|हिंडोला|Carrusel|Карусель|Komidi putar|Vòng quay ngựa gỗ
jogo_dos_pinos|1f3b3|jogos||Jogo dos pinos|Skittles|Bolos|Quilles|Kegeln|Birilli|Kegelen|Kręgle|Käglor|Kuželky|Popice|Κορίνες|Кегли|Bowling|保龄球|ボウリング|볼링|बॉलिंग|Bitlles|Кеглі|Boling|Bowling
bilhete_rifa|1f39f|jogos||Bilhete de rifa|Raffle ticket|Boleto de rifa|Billet de tombola|Los|Biglietto della lotteria|Lot|Los na loterię|Lott|Los|Bilet de tombolă|Λαχνός|Лотерейный билет|Çekiliş bileti|抽奖券|くじ券|추첨권|रैफ़ल टिकट|Butlleta de rifa|Лотерейний квиток|Tiket undian|Vé bốc thăm
karaoke|1f3a4|jogos||=Karaoke
poni|1f434|jogos||Passeio de pónei|Pony ride|Paseo en poni|Tour de poney|Ponyreiten|Giro in pony|Ponyrit|Przejażdżka na kucyku|Ponnyridning|Projížďka na poníkovi|Plimbare cu ponei|Βόλτα με πόνι|Катание на пони|Midilli binişi|骑小马|ポニー乗り|조랑말 타기|टट्टू की सवारी|Passeig en poni|Катання на поні|Naik poni|Cưỡi ngựa con|Passeio de pônei
bingo|1f3b1|jogos||=Bingo
entrada|1f39f|extras||Entrada|Entry|Entrada|Entrée|Eintritt|Ingresso|Entree|Wstęp|Inträde|Vstupné|Intrare|Είσοδος|Вход|Giriş|入场|入場|입장|प्रवेश|Entrada|Вхід|Tiket masuk|Vé vào cửa
estacionamento|1f17f|extras||Estacionamento|Parking|Aparcamiento|Parking|Parkplatz|Parcheggio|Parkeren|Parking|Parkering|Parkování|Parcare|Στάθμευση|Парковка|Otopark|停车|駐車場|주차|पार्किंग|Aparcament|Паркування|Parkir|Bãi đỗ xe
tshirt|1f455|extras||T-shirt|T-shirt|Camiseta|T-shirt|T-Shirt|Maglietta|T-shirt|Koszulka|T-shirt|Tričko|Tricou|Μπλουζάκι|Футболка|Tişört|T恤|Tシャツ|티셔츠|टी-शर्ट|Samarreta|Футболка|Kaus|Áo thun|Camiseta
bone|1f9e2|extras||Boné|Cap|Gorra|Casquette|Kappe|Berretto|Pet|Czapka z daszkiem|Keps|Kšiltovka|Șapcă|Καπέλο|Кепка|Şapka|帽子|キャップ|모자|टोपी|Gorra|Кепка|Topi|Mũ lưỡi trai
copo_reutilizavel|1f964|extras||Copo reutilizável|Reusable cup|Vaso reutilizable|Gobelet réutilisable|Mehrwegbecher|Bicchiere riutilizzabile|Herbruikbare beker|Kubek wielorazowy|Återanvändbar mugg|Opakovaně použitelný kelímek|Pahar reutilizabil|Επαναχρησιμοποιήσιμο ποτήρι|Многоразовый стакан|Yeniden kullanılabilir bardak|可重复使用杯|リユースカップ|다회용 컵|पुन: उपयोग योग्य कप|Got reutilitzable|Багаторазовий стаканчик|Gelas reusable|Cốc dùng lại
donativo|2764|extras||Donativo|Donation|Donativo|Don|Spende|Donazione|Donatie|Darowizna|Donation|Dar|Donație|Δωρεά|Пожертвование|Bağış|捐款|寄付|기부|दान|Donatiu|Пожертва|Donasi|Quyên góp|Doação
livro|1f4d6|extras||Livro|Book|Libro|Livre|Buch|Libro|Boek|Książka|Bok|Kniha|Carte|Βιβλίο|Книга|Kitap|书|本|책|किताब|Llibre|Книга|Buku|Sách
planta|1f331|extras||Planta|Plant|Planta|Plante|Pflanze|Pianta|Plant|Roślina|Växt|Rostlina|Plantă|Φυτό|Растение|Bitki|植物|植物|식물|पौधा|Planta|Рослина|Tanaman|Cây
saco|1f6cd|extras||Saco|Bag|Bolsa|Sac|Tasche|Borsa|Tas|Torba|Väska|Taška|Geantă|Τσάντα|Сумка|Çanta|袋子|バッグ|가방|बैग|Bossa|Сумка|Tas|Túi|Sacola
caixa_surpresa|1f381|extras||Caixa surpresa|Surprise box|Caja sorpresa|Boîte surprise|Überraschungsbox|Scatola a sorpresa|Verrassingsdoos|Pudełko-niespodzianka|Överraskningslåda|Krabice překvapení|Cutie surpriză|Κουτί έκπληξη|Коробка-сюрприз|Sürpriz kutu|惊喜盒|サプライズボックス|서프라이즈 박스|सरप्राइज़ बॉक्स|Caixa sorpresa|Коробка-сюрприз|Kotak kejutan|Hộp bất ngờ
"""

ICONES = """
agua|1f6b0,1f9ca,1f964,1f95b
agua_gas|1f4a7,1f964,1f9c3,1f6b0
refrigerante|1f9c3,1f95b,1f9ca,1f9cb
sumo|1f34a,1f34e,1f347,1f964
sumo_laranja|1f9c3,1f964,1f34b,1f379
limonada|1f964,1f9c3,1f379,1f9ca
cha_gelado|1f964,1f375,1f9ca,1f9c3
leite_chocolate|1f36b,1f964,1f9c3,2615
agua_coco|1f334,1f964,1f9c3,1f4a7
cerveja|1f37b,1f943,1f378,1f379
imperial|1f37a,1f943,1f378,1f9ca
chopp|1f37b,1f943,1f9ca,1f964
vinho_tinto|1f942,1f347,1f37e,1f943
vinho_branco|1f377,1f37e,1f347,1f378
sangria|1f377,1f378,1f34a,1f353
cocktail|1f379,1f943,1f942,1f37e
caipirinha|1f34b,1f378,1f943,1f9ca
vinho_quente|2615,1f375,1f942,1f943
quentao|1f375,1f377,1f943,1f525
espumante|1f942,1f377,1f389,1f378
agua_pe|1f377,1f37e,1f943,1f9c3
jeropiga|1f377,1f943,1f37e,1f9c3
cafe|1f375,1f950,1f36a,1f95b
bica|1f375,1f95b,1f950,1f36a
cha|2615,1f34b,1f33f,1f36a
chocolate_quente|1f36b,1f375,1f95b,1f36a
hamburguer|1f96a,1f35f,1f32d,1f355
cachorro_quente|1f354,1f96a,1f35f,1f356
pizza|1f9c0,1f354,1f96a,1f35d
sandes|1f354,1f956,1f32f,1f9c0
bifana|1f96a,1f969,1f354,1f32d
prego|1f96a,1f956,1f354,1f356
sardinha|1f420,1f364,1f363,1f990
caldo_verde|1f372,1f957,1f96c,1f33f
pao_chourico|1f96a,1f32d,1f356,1f969
frango_assado|1f356,1f414,1f969,1f35f
salsicha|1f32d,1f357,1f969,1f354
batatas_fritas|1f954,1f354,1f9c0,1f32d
salada|1f96c,1f345,1f952,1f955
sopa|1f963,1f35c,1f958,1f957
pipocas|1f33d,1f3ac,1f39f,1f35f
castanhas_assadas|1f95c,1f525,1f342,1f36f
tremocos|1f330,1f33d,1f33f,1f963
coxinha|1f95f,1f356,1f414,1f35f
pastel|1f950,1f9c0,1f95e,1f96e
pao_de_queijo|1f35e,1f950,1f96f,1f956
espetinho|1f356,1f361,1f969,1f364
milho_cozido|1f37f,1f33e,1f955,1f952
pamonha|1f33e,1f37f,1f95f,1f36e
canjica|1f33d,1f372,1f963,1f36e
tapioca|1f32f,1f95f,1f950,1f9c0
bolo|1f382,1f9c1,1f36e,1f369
cupcake|1f370,1f382,1f369,1f36a
brownie|1f36a,1f370,1f9c1,1f36e
bolacha|1f36b,1f950,1f370,1f9c1
donut|1f36a,1f9c1,1f370,1f36d
crepe|1f32f,1f353,1f36b,1f370
waffle|1f95e,1f353,1f366,1f36b
gelado|1f368,1f367,1f9ca,1f36d
algodao_doce|1f36c,2601,1f369,1f9c1
maca_amor|1f34f,1f36d,1f353,1f352
rebucados|1f36d,1f36b,1f361,1f381
chocolate|1f36a,1f370,1f36e,1f95c
mousse|1f36b,1f366,1f370,1f353
fruta|1f34e,1f34a,1f347,1f349
pastel_de_nata|1f370,1f950,1f95a,2615
bola_de_berlim|1f950,1f36a,1f9c1,1f36e
arroz_doce|1f35a,1f963,1f370,1f36f
farturas|1f369,1f950,1f36a,1f95f
brigadeiro|1f36c,1f36a,1f36d,1f370
pacoca|1f330,1f36b,1f36a,1f36c
quindim|1f36f,1f95a,1f370,1f36d
pe_de_moleque|1f330,1f36b,1f36a,1f36c
tiro_ao_alvo|1f3f9,1f3c6,1f3b1,1f3ae
pesca|1f41f,1f420,1f421,1f433
pintura_facial|1f921,1f58c,1f98b,1f984
insuflavel|1f3aa,1f388,1f3a0,1f3e0
carrossel|1f3a1,1f3a2,1f434,1f3aa
jogo_dos_pinos|1f3af,1f3b2,1f3c6,1f3ae
bilhete_rifa|1f3ab,1f381,1f340,1f3c6
karaoke|1f3b6,1f3b8,1f3b5,1f3a7
poni|1f40e,1f984,1f3a0,1f955
bingo|1f3b2,1f3b0,1f340,1f3c6
entrada|1f3ab,1f6aa,1f3a1,1f3aa
estacionamento|1f697,1f68c,1f6b2,1f3cd
tshirt|1f456,1f45a,1f9e5,1f9e2
bone|1f452,1f3a9,1f393,1f455
copo_reutilizavel|267b,2615,1f95b,1f9c3
donativo|1f49d,1f91d,1f381,1f31f
livro|1f4da,1f4d5,1f4d8,1f4d3
planta|1f33f,1f337,1f33b,1f335
saco|1f45c,1f392,1f6d2,1f381
caixa_surpresa|1f389,1f388,1f380,2753
"""

OCASIOES = """
festa_popular|arraial||6,7,8|salsicha,hamburguer,batatas_fritas,pipocas,algodao_doce,cerveja,refrigerante,agua,gelado,cafe|Festa popular|Local festival|Fiesta popular|Fête populaire|Volksfest|Festa popolare|Volksfeest|Festyn|Folkfest|Lidová slavnost|Sărbătoare populară|Λαϊκό πανηγύρι|Народное гулянье|Halk şenliği|民间庆典|お祭り|마을 축제|लोक उत्सव|Festa popular|Народне свято|Pesta rakyat|Lễ hội dân gian
santos_populares|santos|pt|6|sardinha,caldo_verde,bifana,pao_chourico,sangria,imperial,vinho_tinto,agua,refrigerante,farturas,cafe|=Santos Populares
festa_junina|arraial|br|6,7|pipocas,milho_cozido,pamonha,canjica,pacoca,pe_de_moleque,maca_amor,quentao,cachorro_quente,algodao_doce,refrigerante,agua|=Festa Junina
natal|natal||11,12|chocolate_quente,vinho_quente,bolo,bolacha,castanhas_assadas,cha,cafe,sumo,chocolate,rebucados|Natal|Christmas|Navidad|Noël|Weihnachten|Natale|Kerstmis|Boże Narodzenie|Jul|Vánoce|Crăciun|Χριστούγεννα|Рождество|Noel|圣诞节|クリスマス|크리스마스|क्रिसमस|Nadal|Різдво|Natal|Giáng sinh
magusto|magusto|pt|11|castanhas_assadas,agua_pe,jeropiga,vinho_tinto,cha,cafe,bolo|=Magusto
halloween|halloween||10|refrigerante,sumo,maca_amor,rebucados,pipocas,bolo,chocolate,cachorro_quente,limonada|Halloween|Halloween|Halloween|Halloween|Halloween|Halloween|Halloween|Halloween|Halloween|Halloween|Halloween|Χάλογουιν|Хэллоуин|Cadılar Bayramı|万圣节|ハロウィン|할로윈|हैलोवीन|Halloween|Гелловін|Halloween|Halloween
pascoa|pascoa||3,4|bolo,chocolate,cafe,cha,sumo,bolacha,fruta|Páscoa|Easter|Pascua|Pâques|Ostern|Pasqua|Pasen|Wielkanoc|Påsk|Velikonoce|Paște|Πάσχα|Пасха|Paskalya|复活节|イースター|부활절|ईस्टर|Pasqua|Великдень|Paskah|Lễ Phục sinh
carnaval|carnaval||2,3|crepe,cerveja,refrigerante,agua,cachorro_quente,hamburguer,pipocas,sangria|Carnaval|Carnival|Carnaval|Carnaval|Karneval|Carnevale|Carnaval|Karnawał|Karneval|Karneval|Carnaval|Καρναβάλι|Карнавал|Karnaval|狂欢节|カーニバル|카니발|कार्निवल|Carnaval|Карнавал|Karnaval|Lễ hội Carnaval
praia|praia||7,8|gelado,agua,refrigerante,sumo,limonada,cerveja,fruta,sandes,batatas_fritas,agua_coco|Dia de praia|Beach day|Día de playa|Journée plage|Strandtag|Giornata in spiaggia|Strandfeest|Dzień na plaży|Strandfest|Den na pláži|Zi la plajă|Μέρα στην παραλία|Пляжный день|Plaj günü|海滩日|ビーチデー|해변의 날|बीच डे|Dia de platja|День на пляжі|Hari pantai|Ngày đi biển
festa_escola|escola||5,6,9|bolo,bolacha,sumo,agua,fruta,pipocas,crepe,sandes,gelado,pintura_facial,insuflavel|Festa da escola|School party|Fiesta del colegio|Fête de l'école|Schulfest|Festa della scuola|Schoolfeest|Festyn szkolny|Skolfest|Školní slavnost|Serbarea școlii|Σχολική γιορτή|Школьный праздник|Okul şenliği|学校联欢|学校のお祭り|학교 축제|स्कूल उत्सव|Festa de l'escola|Шкільне свято|Pesta sekolah|Lễ hội trường học
clube|futebol||4,5,9,10|cerveja,imperial,chopp,refrigerante,agua,hamburguer,cachorro_quente,sandes,batatas_fritas,cafe,bolacha|Jogo do clube|Club match day|Día de partido del club|Jour de match du club|Vereinsspieltag|Giornata della partita del club|Clubwedstrijd|Mecz klubowy|Klubbmatch|Zápas klubu|Meci la club|Αγώνας συλλόγου|Матч клуба|Kulüp maçı günü|俱乐部比赛日|クラブの試合日|클럽 경기일|क्लब मैच दिवस|Dia de partit del club|День матчу клубу|Hari pertandingan klub|Ngày thi đấu của câu lạc bộ
feira_bolos|solidaria||3,4,5,9,10|bolo,cupcake,brownie,bolacha,donut,cafe,cha,sumo,donativo|Feira de bolos|Bake sale|Venta de pasteles|Vente de gâteaux|Kuchenbasar|Vendita di dolci|Taartenverkoop|Kiermasz ciast|Bakförsäljning|Prodej koláčů|Târg de prăjituri|Παζάρι γλυκών|Продажа выпечки|Pasta satışı|义卖糕点|ベイクセール|베이크 세일|बेक सेल|Venda de pastissos|Продаж випічки|Bazar kue|Bán bánh gây quỹ
festival|festival||7,8|cerveja,cocktail,hamburguer,pizza,batatas_fritas,refrigerante,agua,gelado,copo_reutilizavel,tshirt|=Festival
quermesse|quermesse||5,6,7,8,9|bolo,sumo,pipocas,algodao_doce,tiro_ao_alvo,pesca,bilhete_rifa,cafe|=Quermesse
inverno|inverno||1,2,12|chocolate_quente,vinho_quente,cha,sopa,castanhas_assadas,bolo,cafe|Inverno|Winter|Invierno|Hiver|Winter|Inverno|Winter|Zima|Vinter|Zima|Iarnă|Χειμώνας|Зима|Kış|冬季|冬|겨울|सर्दी|Hivern|Зима|Musim dingin|Mùa đông
"""
