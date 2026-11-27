"""Os guias «como fazer» nas línguas de um ficheiro só (catalão, ucraniano, indonésio, vietnamita): juntam-se aos de `escolas.DADOS`, `associacoes.DADOS`, `clubes.DADOS`, `bombeiros.DADOS` e `festas.DADOS` em `__init__.py`.

Mesmo formato dos outros: título, introdução, 5 passos (título, texto), 3 dicas e uma frase final. Sem revisão nativa; as regras de licença de uma rifa variam por país,
por isso o 1.º passo de ambos manda confirmar com a autoridade local. Ver docs/LINGUAS.md.
"""

ESCOLAS = {
    "ca": {
        "titulo": "Com fer una rifa per a l'escola",
        "intro": "Una rifa és una manera senzilla de recollir fons per a una sortida, la festa de Nadal o el material de la classe. Amb el Generador de Rifes feu butlletes numerades en pocs minuts, sense Canva i sense instal·lar res: dissenyeu, imprimiu i retalleu.",
        "passos": [
            ("Acordeu l'essencial", "Decidiu els premis (sovint donats per les famílies i el comerç local), el preu de la butlleta, quantes butlletes s'imprimiran i la data del sorteig. Abans de vendre, consulteu amb l'autoritat local si la rifa necessita llicència o notificació: les normes depenen del tipus de rifa."),
            ("Dissenyeu la butlleta", "A la galeria trieu un disseny (Natal, Bosque…) i escriviu el nom de l'escola, l'esdeveniment, els premis i la data. Si voleu alguna cosa a mida, feu servir l'Editor de plantilles i afegiu textos, línies i rectangles. Afegiu després el logotip de l'escola a «La vostra marca»."),
            ("Una sèrie per classe", "A «Prefix o sèries» escriviu, per exemple, 5A-, 5B-, 6A-: cada classe rep les seves butlletes (5A-0001, 5B-0001…) i els seus fitxers, i així sabeu quina classe n'ha venut més. Podeu donar un color a cada sèrie."),
            ("Imprimiu i retalleu", "Trieu el paper (l'A4 sol anar bé) i les marques de tall: el programa omple el full de butlletes. Imprimiu en paper de color per distingir les classes i retalleu seguint les marques. Les butlletes tenen taló, de manera que el número apareix dues vegades."),
            ("Controleu les vendes i sortegeu", "Exporteu la llista de butlletes (CSV) i el full de control de vendes per lliurar a cada professor. El dia del sorteig feu servir la pàgina «Sorteig»: amb una llavor pública (per exemple, el resultat de la loteria) qualsevol família pot confirmar el resultat."),
        ],
        "dicas": [
            "Reserveu algunes butlletes extra per substituir les que s'estripin, i doneu a cada classe un interval de números.",
            "No escriviu a les butlletes noms d'infants ni dades personals: n'hi ha prou amb el nom de qui compra, al taló.",
            "Anuncieu el resultat al tauler, al butlletí de l'escola o al grup de pares, amb l'enllaç del sorteig.",
        ],
        "fim": "El servei és gratuït, no cal registre i no guarda els vostres fitxers. Podeu començar ara mateix.",
    },
    "uk": {
        "titulo": "Як провести лотерею для школи",
        "intro": "Лотерея — простий спосіб зібрати кошти на екскурсію, різдвяне свято чи шкільне приладдя. З Генератором лотерей ви за кілька хвилин зробите пронумеровані квитки без Canva й нічого не встановлюючи: створіть, надрукуйте й виріжте.",
        "passos": [
            ("Домовтеся про головне", "Вирішіть, які будуть призи (їх часто дарують родини та місцеві магазини), ціну квитка, скільки квитків друкувати та дату розіграшу. Перед продажем дізнайтеся в місцевої влади, чи потрібні для лотереї ліцензія або повідомлення: правила залежать від типу лотереї."),
            ("Створіть квиток", "У галереї виберіть дизайн (Natal, Bosque…) і напишіть назву школи, подію, призи та дату. Якщо хочете щось своє, скористайтеся Редактором шаблонів і додайте тексти, лінії та прямокутники. Логотип школи додайте потім у розділі «Ваш бренд»."),
            ("Одна серія на клас", "У полі «Префікс або серії» напишіть, наприклад, 5А-, 5Б-, 6А-: кожен клас отримає свої квитки (5А-0001, 5Б-0001…) і власні файли, тож буде видно, який клас продав найбільше. Кожній серії можна дати колір."),
            ("Друк і вирізання", "Виберіть папір (зазвичай підходить A4) і мітки для обрізання: програма заповнює аркуш квитками. Друкуйте на кольоровому папері, щоб розрізняти класи, і ріжте по мітках. Квитки мають корінець, тож номер з'являється двічі."),
            ("Облік продажів і розіграш", "Експортуйте список квитків (CSV) і контрольний аркуш продажів, щоб передати кожному вчителю. У день розіграшу скористайтеся сторінкою «Розіграш»: з публічним зерном (наприклад, результатом лотереї) будь-яка родина може підтвердити результат."),
        ],
        "dicas": [
            "Залиште кілька запасних квитків для заміни пошкоджених і дайте кожному класу діапазон номерів.",
            "Не пишіть на квитках імен дітей чи персональних даних: достатньо імені покупця на корінці.",
            "Оголосіть результат на дошці оголошень, у шкільному бюлетені чи в батьківській групі з посиланням на розіграш.",
        ],
        "fim": "Сервіс безкоштовний, без реєстрації й не зберігає ваших файлів. Можна починати вже зараз.",
    },
    "id": {
        "titulo": "Cara menyelenggarakan undian untuk sekolah",
        "intro": "Undian adalah cara sederhana untuk menggalang dana bagi karya wisata, perayaan Natal atau perlengkapan kelas. Dengan Pembuat Undian Anda membuat tiket bernomor dalam hitungan menit, tanpa Canva dan tanpa memasang apa pun: rancang, cetak dan gunting.",
        "passos": [
            ("Sepakati hal-hal pokok", "Tentukan hadiah (sering disumbangkan keluarga dan toko setempat), harga tiket, jumlah tiket yang dicetak dan tanggal pengundian. Sebelum menjual, tanyakan ke otoritas setempat apakah undian memerlukan izin atau pemberitahuan: aturannya bergantung pada jenis undian."),
            ("Rancang tiketnya", "Pilih desain dari galeri (Natal, Bosque…) dan tulis nama sekolah, acara, hadiah dan tanggal. Jika ingin yang khusus, gunakan Editor templat dan tambahkan teks, garis dan persegi panjang. Tambahkan logo sekolah setelahnya di «Merek Anda»."),
            ("Satu seri per kelas", "Di «Awalan atau seri» ketik, misalnya, 5A-, 5B-, 6A-: setiap kelas mendapat tiketnya sendiri (5A-0001, 5B-0001…) dan berkasnya sendiri, sehingga Anda tahu kelas mana yang paling banyak menjual. Setiap seri dapat diberi warna."),
            ("Cetak dan gunting", "Pilih kertas (A4 biasanya cukup) dan tanda potong: program memenuhi lembar dengan tiket. Cetak di kertas berwarna agar kelas mudah dibedakan lalu gunting mengikuti tanda. Tiket memiliki kupon, sehingga nomor muncul dua kali."),
            ("Pantau penjualan dan undi", "Ekspor daftar tiket (CSV) dan lembar kontrol penjualan untuk diberikan kepada setiap guru. Pada hari pengundian gunakan halaman «Pengundian»: dengan benih publik (misalnya hasil undian nasional) keluarga mana pun dapat memastikan hasilnya."),
        ],
        "dicas": [
            "Sisihkan beberapa tiket cadangan untuk mengganti yang rusak, dan beri setiap kelas rentang nomor.",
            "Jangan menulis nama anak atau data pribadi pada tiket: nama pembeli di kupon sudah cukup.",
            "Umumkan hasilnya di papan pengumuman, buletin sekolah atau grup orang tua, beserta tautan pengundian.",
        ],
        "fim": "Layanan ini gratis, tanpa pendaftaran dan tidak menyimpan berkas Anda. Anda bisa mulai sekarang.",
    },
    "vi": {
        "titulo": "Cách tổ chức bốc thăm cho trường học",
        "intro": "Bốc thăm là cách đơn giản để gây quỹ cho chuyến tham quan, buổi tiệc Giáng sinh hay đồ dùng học tập. Với Trình tạo vé số, bạn làm vé đánh số trong vài phút, không cần Canva và không cài đặt gì: thiết kế, in và cắt.",
        "passos": [
            ("Thống nhất những điều cơ bản", "Quyết định giải thưởng (thường do các gia đình và cửa hàng địa phương tặng), giá vé, số vé cần in và ngày bốc thăm. Trước khi bán, hãy hỏi chính quyền địa phương xem cuộc bốc thăm có cần giấy phép hay thông báo không: quy định tùy theo loại bốc thăm."),
            ("Thiết kế vé", "Chọn một thiết kế trong thư viện (Natal, Bosque…) và nhập tên trường, sự kiện, giải thưởng và ngày. Nếu muốn riêng, hãy dùng Trình chỉnh sửa mẫu và thêm văn bản, đường kẻ, hình chữ nhật. Sau đó thêm logo của trường trong mục «Thương hiệu của bạn»."),
            ("Mỗi lớp một sê-ri", "Trong «Tiền tố hoặc sê-ri» hãy nhập, ví dụ, 5A-, 5B-, 6A-: mỗi lớp nhận vé riêng (5A-0001, 5B-0001…) và tệp riêng, để bạn biết lớp nào bán được nhiều nhất. Có thể gán cho mỗi sê-ri một màu."),
            ("In và cắt", "Chọn giấy (A4 thường là đủ) và dấu cắt: chương trình lấp đầy tờ giấy bằng vé. In trên giấy màu để phân biệt các lớp và cắt theo dấu. Vé có cuống, nên số xuất hiện hai lần."),
            ("Theo dõi doanh số và bốc thăm", "Xuất danh sách vé (CSV) và phiếu kiểm soát bán vé để đưa cho từng giáo viên. Vào ngày bốc thăm, hãy dùng trang «Bốc thăm»: với hạt giống công khai (ví dụ kết quả xổ số), gia đình nào cũng có thể xác nhận kết quả."),
        ],
        "dicas": [
            "Giữ lại vài vé dự phòng để thay vé bị hỏng, và cấp cho mỗi lớp một khoảng số.",
            "Đừng ghi tên trẻ em hay dữ liệu cá nhân lên vé: chỉ cần tên người mua trên cuống là đủ.",
            "Thông báo kết quả trên bảng tin, bản tin của trường hoặc nhóm phụ huynh, kèm liên kết bốc thăm.",
        ],
        "fim": "Dịch vụ miễn phí, không cần đăng ký và không lưu tệp của bạn. Bạn có thể bắt đầu ngay.",
    },
}

ASSOCIACOES = {
    "ca": {
        "titulo": "Com fer una rifa per a l'associació",
        "intro": "Associacions, clubs, grups de folklore i bombers voluntaris fan servir les rifes per finançar les seves activitats. El Generador de Rifes us dona butlletes numerades amb la imatge de la vostra associació, amb taló i llestes per imprimir, a més d'eines per seguir els venedors i demostrar que el sorteig ha estat net.",
        "passos": [
            ("Planifiqueu la campanya", "Fixeu l'objectiu, els premis, el preu, el nombre de butlletes i les dates de venda i de sorteig. Abans de vendre, consulteu amb l'autoritat local (o el regulador) quina llicència o notificació necessita la rifa."),
            ("Feu servir la imatge de l'associació", "Feu la butlleta a la galeria o a l'Editor de plantilles, o pugeu la vostra plantilla de Canva. Afegiu el logotip i el color de l'associació a «La vostra marca», perquè cada butlleta porti la seva identitat."),
            ("Una sèrie per venedor o grup", "Amb prefixos (A-, B-, C-), cada venedor, secció o grup rep les seves butlletes. Podeu ometre números reservats (per exemple 13 o 100–110) i donar un color a cada sèrie."),
            ("Imprimiu amb marques de tall", "Trieu el paper i deixeu que el programa disposi les butlletes al full, amb marques de tall als marges. Per a tirades grans de milers de números, genereu diversos PDF, un per sèrie o per nombre màxim de butlletes."),
            ("Seguiu, verifiqueu i informeu", "Exporteu la llista (CSV) i el full de control de vendes per a cada venedor. Activeu el QR de verificació a les butlletes i feu el sorteig a la pàgina «Sorteig», amb una llavor pública, per poder-lo mostrar als socis i a la comunitat."),
        ],
        "dicas": [
            "Anoteu qui s'endú cada bloc de butlletes i quan retorna els diners i els talons no venuts.",
            "Publiqueu els premis i la data del sorteig a les xarxes socials i a la seu: més confiança, més vendes.",
            "Guardeu la llista, el resultat del sorteig i l'enllaç per poder-los mostrar a l'assemblea general.",
        ],
        "fim": "És gratuït, no cal registre i els vostres fitxers no es guarden al servidor.",
    },
    "uk": {
        "titulo": "Як провести лотерею для об'єднання",
        "intro": "Об'єднання, клуби, фольклорні гуртки та добровільні пожежні команди проводять лотереї, щоб фінансувати свою діяльність. Генератор лотерей дає вам пронумеровані квитки у стилі вашого об'єднання, з корінцем і готові до друку, а також інструменти для обліку продавців і доказу чесності розіграшу.",
        "passos": [
            ("Сплануйте кампанію", "Визначте мету, призи, ціну, кількість квитків і дати продажу та розіграшу. Перед продажем дізнайтеся в місцевої влади (або регулятора), яка ліцензія чи повідомлення потрібні для лотереї."),
            ("Використайте стиль вашого об'єднання", "Створіть квиток у галереї чи в Редакторі шаблонів або завантажте свій шаблон Canva. Додайте логотип і колір об'єднання в розділі «Ваш бренд», щоб кожен квиток мав його ідентичність."),
            ("Одна серія на продавця чи групу", "З префіксами (A-, B-, C-) кожен продавець, секція чи група отримує власні квитки. Можна пропускати зарезервовані номери (наприклад, 13 або 100–110) і давати кожній серії колір."),
            ("Друк із мітками для обрізання", "Виберіть папір, і програма розкладе квитки на аркуші, з мітками для обрізання на полях. Для великих накладів із тисяч номерів створіть кілька PDF — по одному на серію чи на максимальну кількість квитків."),
            ("Облік, перевірка та звітність", "Експортуйте список (CSV) і контрольний аркуш продажів для кожного продавця. Увімкніть QR перевірки на квитках і проведіть розіграш на сторінці «Розіграш» із публічним зерном, щоб показати його членам і громаді."),
        ],
        "dicas": [
            "Записуйте, хто бере кожен блок квитків і коли повертає гроші та непродані корінці.",
            "Оприлюднюйте призи й дату розіграшу в соцмережах і в приміщенні: більше довіри — більше продажів.",
            "Збережіть список, результат розіграшу й посилання, щоб показати їх на загальних зборах.",
        ],
        "fim": "Безкоштовно, без реєстрації, а ваші файли не зберігаються на сервері.",
    },
    "id": {
        "titulo": "Cara menyelenggarakan undian untuk organisasi",
        "intro": "Organisasi, klub, kelompok seni tradisional dan pemadam kebakaran sukarela memakai undian untuk membiayai kegiatan mereka. Pembuat Undian memberi Anda tiket bernomor dengan gaya organisasi Anda, lengkap dengan kupon dan siap cetak, serta alat untuk memantau penjual dan menunjukkan bahwa pengundian berlangsung adil.",
        "passos": [
            ("Rencanakan kampanyenya", "Tetapkan tujuan, hadiah, harga, jumlah tiket serta tanggal penjualan dan pengundian. Sebelum menjual, tanyakan ke otoritas setempat (atau regulator) izin atau pemberitahuan apa yang diperlukan undian itu."),
            ("Pakai gaya organisasi Anda", "Buat tiket di galeri atau di Editor templat, atau unggah templat Canva Anda. Tambahkan logo dan warna organisasi di «Merek Anda», sehingga setiap tiket membawa identitasnya."),
            ("Satu seri per penjual atau kelompok", "Dengan awalan (A-, B-, C-), setiap penjual, seksi atau kelompok mendapat tiketnya sendiri. Anda dapat melewati nomor yang dicadangkan (misalnya 13 atau 100–110) dan memberi setiap seri warna sendiri."),
            ("Cetak dengan tanda potong", "Pilih kertas dan biarkan program menata tiket pada lembar, dengan tanda potong di margin. Untuk cetakan besar ribuan nomor, buat beberapa PDF, satu per seri atau per jumlah maksimum tiket."),
            ("Pantau, verifikasi dan laporkan", "Ekspor daftar (CSV) dan lembar kontrol penjualan untuk setiap penjual. Aktifkan QR verifikasi pada tiket dan adakan pengundian di halaman «Pengundian», dengan benih publik, agar dapat Anda tunjukkan kepada anggota dan masyarakat."),
        ],
        "dicas": [
            "Catat siapa yang membawa setiap blok tiket dan kapan mengembalikan uang serta kupon yang tidak terjual.",
            "Umumkan hadiah dan tanggal pengundian di media sosial dan di sekretariat: lebih dipercaya, lebih laku.",
            "Simpan daftar, hasil pengundian dan tautannya agar dapat ditunjukkan pada rapat umum.",
        ],
        "fim": "Gratis, tanpa pendaftaran, dan berkas Anda tidak disimpan di server.",
    },
    "vi": {
        "titulo": "Cách tổ chức bốc thăm cho hội nhóm",
        "intro": "Các hội nhóm, câu lạc bộ, đội văn nghệ dân gian và đội phòng cháy chữa cháy tình nguyện dùng bốc thăm để tài trợ hoạt động của mình. Trình tạo vé số cung cấp cho bạn vé đánh số mang phong cách hội nhóm, có cuống và sẵn sàng để in, cùng các công cụ theo dõi người bán và chứng minh cuộc bốc thăm công bằng.",
        "passos": [
            ("Lập kế hoạch chiến dịch", "Đặt mục tiêu, giải thưởng, giá vé, số lượng vé và ngày bán, ngày bốc thăm. Trước khi bán, hãy hỏi chính quyền địa phương (hoặc cơ quan quản lý) xem cuộc bốc thăm cần giấy phép hay thông báo gì."),
            ("Dùng phong cách của hội nhóm", "Làm vé trong thư viện hoặc Trình chỉnh sửa mẫu, hoặc tải lên mẫu Canva của bạn. Thêm logo và màu của hội nhóm trong «Thương hiệu của bạn», để mỗi vé mang dấu ấn của hội."),
            ("Mỗi người bán hoặc nhóm một sê-ri", "Với tiền tố (A-, B-, C-), mỗi người bán, ban hoặc nhóm nhận vé riêng. Bạn có thể bỏ qua các số giữ chỗ (ví dụ 13 hoặc 100–110) và cho mỗi sê-ri một màu."),
            ("In có dấu cắt", "Chọn giấy và để chương trình sắp vé trên tờ giấy, kèm dấu cắt ở lề. Với đợt in lớn hàng nghìn số, hãy tạo nhiều tệp PDF, mỗi sê-ri hoặc mỗi số vé tối đa một tệp."),
            ("Theo dõi, kiểm chứng và báo cáo", "Xuất danh sách (CSV) và phiếu kiểm soát bán vé cho từng người bán. Bật mã QR xác minh trên vé và tổ chức bốc thăm ở trang «Bốc thăm», với hạt giống công khai, để bạn có thể trình bày với hội viên và cộng đồng."),
        ],
        "dicas": [
            "Ghi lại ai nhận từng xấp vé và khi nào họ nộp lại tiền cùng các cuống chưa bán.",
            "Công bố giải thưởng và ngày bốc thăm trên mạng xã hội và tại trụ sở: thêm tin tưởng, thêm doanh số.",
            "Giữ lại danh sách, kết quả bốc thăm và liên kết để trình bày tại đại hội.",
        ],
        "fim": "Miễn phí, không cần đăng ký và tệp của bạn không được lưu trên máy chủ.",
    },
}


# ---------------------------------------------------------------- guias de clubes, bombeiros e festas (3.34.0)
CLUBES = {
    "ca": {
        "titulo": "Com fer una rifa per al club",
        "intro": "Una rifa és una manera senzilla que el club recapti fons per a equipaments, desplaçaments o la temporada vinent. Amb el Generador de Rifes feu butlletes numerades, amb l'escut del club, en pocs minuts: sense Canva ni programes per instal·lar.",
        "passos": [
            ("Acordeu l'essencial", "Decidiu els premis (sovint oferts per patrocinadors i socis), el preu de la butlleta, quantes butlletes s'imprimiran i la data del sorteig, per exemple en un partit a casa o al sopar de socis. Abans de vendre, consulteu a l'ajuntament si la rifa necessita llicència o comunicació: les normes depenen del tipus de rifa."),
            ("Dissenyeu la butlleta amb l'escut", "A la galeria trieu un disseny (Futebol, Retro…) i escriviu el nom del club, els premis i la data. Afegiu l'escut com a logotip (PNG o JPG) i trieu per als números els colors del club. Si voleu alguna cosa a mida, feu servir l'Editor de plantilles."),
            ("Una sèrie per equip o venedor", "A «Prefix o sèries» escriviu, per exemple, A-, B-, C-: cada equip, categoria o venedor rep les seves butlletes (A-0001, B-0001…) i els seus fitxers, i així se sap qui ha venut més. Podeu donar un color a cada sèrie."),
            ("Imprimiu i retalleu", "Trieu el paper (l'A4 sol anar bé) i les marques de tall: el programa omple el full de butlletes. Imprimiu i retalleu per les marques; amb paper de color distingiu les sèries. Les butlletes tenen taló, per això el número apareix dues vegades."),
            ("Controleu les vendes i sortegeu", "Exporteu la llista de butlletes (CSV) i el full de control de vendes per lliurar a cada entrenador o venedor. El dia del sorteig feu servir la pàgina «Sorteig»: amb una llavor pública (per exemple, la loteria) qualsevol soci pot comprovar el resultat."),
        ],
        "dicas": [
            "Doneu a cada equip o venedor un interval de números i apunteu qui s'endú cada bloc de butlletes.",
            "Veneu als partits i als esdeveniments del club i demaneu a qui compra que escrigui el nom i el contacte al taló.",
            "Anuncieu el resultat a les xarxes socials i al web del club, amb l'enllaç del sorteig, perquè tothom pugui comprovar-lo.",
        ],
        "fim": "El servei és gratuït, no cal registre i no guarda els vostres fitxers. Podeu començar ara mateix.",
    },
    "uk": {
        "titulo": "Як провести лотерею для клубу",
        "intro": "Лотерея — простий спосіб для клубу зібрати кошти на форму, поїздки чи наступний сезон. З Генератором лотерей ви за кілька хвилин зробите пронумеровані квитки з емблемою клубу: без Canva і без встановлення програм.",
        "passos": [
            ("Домовтеся про головне", "Вирішіть, які будуть призи (їх часто дарують спонсори та члени клубу), ціну квитка, скільки квитків друкувати і дату розіграшу, наприклад на домашньому матчі чи клубній вечері. Перед продажем дізнайтеся в місцевій владі, чи потрібні для лотереї дозвіл або повідомлення: правила залежать від виду лотереї."),
            ("Створіть квиток з емблемою", "У галереї виберіть дизайн (Futebol, Retro…) і напишіть назву клубу, призи та дату. Додайте емблему як логотип (PNG або JPG) і виберіть для номерів кольори клубу. Якщо хочете щось своє, скористайтеся Редактором шаблонів."),
            ("Одна серія на команду чи продавця", "У полі «Префікс або серії» напишіть, наприклад, A-, B-, C-: кожна команда, вікова група чи продавець отримає свої квитки (A-0001, B-0001…) і свої файли, тож видно, хто продав найбільше. Кожній серії можна дати колір."),
            ("Друк і вирізання", "Виберіть папір (зазвичай підходить A4) і мітки для обрізання: програма заповнює аркуш квитками. Надрукуйте й різіть по мітках; кольоровий папір допоможе розрізнити серії. У квитків є корінець, тому номер зазначено двічі."),
            ("Облік продажів і розіграш", "Експортуйте список квитків (CSV) і контрольний аркуш продажів, щоб передати кожному тренеру чи продавцю. У день розіграшу відкрийте сторінку «Розіграш»: з публічним зерном (наприклад, результатом лотереї) будь-який член клубу зможе перевірити підсумок."),
        ],
        "dicas": [
            "Дайте кожній команді чи продавцю діапазон номерів і записуйте, хто взяв який блок квитків.",
            "Продавайте на матчах і клубних заходах та просіть покупців писати ім'я й контакт на корінці.",
            "Оголосіть результат у соцмережах і на сайті клубу з посиланням на розіграш, щоб кожен міг його перевірити.",
        ],
        "fim": "Сервіс безкоштовний, без реєстрації й не зберігає ваших файлів. Можна починати вже зараз.",
    },
    "id": {
        "titulo": "Cara membuat undian untuk klub",
        "intro": "Undian adalah cara sederhana bagi klub untuk menggalang dana bagi perlengkapan, perjalanan, atau musim depan. Dengan Pembuat Undian Anda bisa membuat tiket bernomor berlogo klub dalam beberapa menit: tanpa Canva dan tanpa memasang program.",
        "passos": [
            ("Sepakati hal pokok", "Tentukan hadiah (sering disumbangkan sponsor dan anggota), harga tiket, jumlah tiket yang dicetak, dan tanggal pengundian, misalnya saat pertandingan kandang atau makan malam anggota. Sebelum menjual, tanyakan ke pemerintah setempat apakah undian memerlukan izin atau pemberitahuan: aturannya bergantung pada jenis undian."),
            ("Rancang tiket dengan lambang klub", "Di galeri pilih desain (Futebol, Retro…) dan tulis nama klub, hadiah, dan tanggal. Tambahkan lambang klub sebagai logo (PNG atau JPG) dan pilih warna klub untuk nomor. Untuk desain sendiri, gunakan Editor templat."),
            ("Satu seri per tim atau penjual", "Di «Awalan atau seri» tulis, misalnya, A-, B-, C-: setiap tim, kelompok umur, atau penjual mendapat tiket (A-0001, B-0001…) dan berkasnya sendiri, sehingga terlihat siapa yang paling banyak menjual. Setiap seri bisa diberi warna."),
            ("Cetak dan gunting", "Pilih kertas (biasanya A4 cukup) dan tanda potong: program memenuhi lembar dengan tiket. Cetak lalu gunting mengikuti tanda; kertas berwarna membantu membedakan seri. Tiket punya kupon, jadi nomornya muncul dua kali."),
            ("Pantau penjualan dan lakukan pengundian", "Ekspor daftar tiket (CSV) dan lembar kontrol penjualan untuk diberikan kepada setiap pelatih atau penjual. Pada hari pengundian gunakan halaman «Pengundian»: dengan seed publik (misalnya hasil lotere) setiap anggota dapat memastikan hasilnya."),
        ],
        "dicas": [
            "Beri setiap tim atau penjual rentang nomor dan catat siapa yang membawa tiap blok tiket.",
            "Jual di pertandingan dan acara klub, dan minta pembeli menulis nama dan kontak pada kupon.",
            "Umumkan hasil di media sosial dan situs klub beserta tautan pengundian agar semua orang bisa memeriksanya.",
        ],
        "fim": "Layanan ini gratis, tanpa pendaftaran dan tidak menyimpan berkas Anda. Anda bisa mulai sekarang.",
    },
    "vi": {
        "titulo": "Cách tổ chức bốc thăm cho câu lạc bộ",
        "intro": "Bốc thăm là cách đơn giản để câu lạc bộ gây quỹ mua trang phục, đi thi đấu xa hoặc chuẩn bị mùa giải sau. Với Trình tạo vé số, bạn làm vé đánh số có huy hiệu câu lạc bộ chỉ trong vài phút: không cần Canva, không cần cài phần mềm.",
        "passos": [
            ("Thống nhất những điều cơ bản", "Quyết định giải thưởng (thường do nhà tài trợ và hội viên tặng), giá vé, số vé sẽ in và ngày bốc thăm, chẳng hạn trong trận đấu trên sân nhà hoặc bữa tối của hội viên. Trước khi bán, hãy hỏi chính quyền địa phương xem cuộc bốc thăm có cần giấy phép hay thông báo không: quy định phụ thuộc vào loại hình."),
            ("Thiết kế vé có huy hiệu", "Trong thư viện, chọn một mẫu (Futebol, Retro…) rồi viết tên câu lạc bộ, giải thưởng và ngày. Thêm huy hiệu làm logo (PNG hoặc JPG) và chọn màu của câu lạc bộ cho các số. Muốn mẫu riêng, hãy dùng Trình chỉnh sửa mẫu."),
            ("Mỗi đội hoặc người bán một sê-ri", "Ở «Tiền tố hoặc sê-ri», gõ chẳng hạn A-, B-, C-: mỗi đội, mỗi nhóm tuổi hoặc người bán nhận vé (A-0001, B-0001…) và tệp riêng, nhờ đó biết ai bán nhiều nhất. Có thể gán cho mỗi sê-ri một màu."),
            ("In và cắt", "Chọn giấy (thường A4 là đủ) và dấu cắt: chương trình xếp đầy tờ giấy bằng vé. In rồi cắt theo dấu; dùng giấy màu để phân biệt các sê-ri. Vé có cuống nên số xuất hiện hai lần."),
            ("Theo dõi doanh số và bốc thăm", "Xuất danh sách vé (CSV) và bảng kiểm soát doanh số để đưa cho từng huấn luyện viên hoặc người bán. Đến ngày bốc thăm, dùng trang «Bốc thăm»: với hạt giống công khai (ví dụ kết quả xổ số), hội viên nào cũng có thể kiểm chứng kết quả."),
        ],
        "dicas": [
            "Giao cho mỗi đội hoặc người bán một dải số và ghi lại ai nhận từng xấp vé.",
            "Bán tại các trận đấu và sự kiện của câu lạc bộ, và nhờ người mua viết tên cùng liên lạc lên cuống vé.",
            "Công bố kết quả trên mạng xã hội và trang web của câu lạc bộ, kèm liên kết bốc thăm để ai cũng kiểm tra được.",
        ],
        "fim": "Dịch vụ miễn phí, không cần đăng ký và không lưu tệp của bạn. Bạn có thể bắt đầu ngay.",
    },
}

BOMBEIROS = {
    "ca": {
        "titulo": "Com fer una rifa per als bombers",
        "intro": "Les rifes són una ajuda tradicional per als cossos de bombers voluntaris: equipament, vehicles i la festa anual. Amb el Generador de Rifes feu butlletes numerades, amb l'escut del cos, en pocs minuts: sense Canva ni programes per instal·lar.",
        "passos": [
            ("Acordeu l'essencial", "Decidiu els premis (sovint oferts pel comerç i les empreses de la zona), el preu de la butlleta, quantes butlletes s'imprimiran i la data del sorteig, per exemple l'aniversari del cos. Abans de vendre, consulteu a l'ajuntament si la rifa necessita llicència o comunicació: les normes depenen del tipus de rifa."),
            ("Dissenyeu la butlleta", "A la galeria trieu un disseny (Bombeiros, Solidária…) i escriviu el nom del cos, els premis i la data. Afegiu l'escut com a logotip (PNG o JPG) i trieu el color dels números. Si voleu alguna cosa a mida, feu servir l'Editor de plantilles."),
            ("Una sèrie per venedor o barri", "A «Prefix o sèries» escriviu, per exemple, A-, B-, C-: cada venedor, parc o barri rep les seves butlletes (A-0001, B-0001…) i els seus fitxers, i així se sap qui ha venut més. A «Omet números» traieu els que queden reservats."),
            ("Imprimiu i retalleu", "Trieu el paper (l'A4 sol anar bé) i les marques de tall: el programa omple el full de butlletes. Imprimiu i retalleu per les marques; amb paper de color distingiu les sèries. Les butlletes tenen taló, per això el número apareix dues vegades."),
            ("Controleu les vendes i sortegeu", "Exporteu la llista de butlletes (CSV) i el full de control de vendes per lliurar a cada venedor. El dia del sorteig feu servir la pàgina «Sorteig»: amb una llavor pública (per exemple, la loteria) qualsevol persona pot comprovar el resultat."),
        ],
        "dicas": [
            "Lliureu els blocs de butlletes contra una llista i apunteu qui s'endú cada bloc.",
            "Escriviu a la butlleta el contacte del cos i la data límit per recollir els premis.",
            "Agraïu en públic a qui ha ofert premis i publiqueu el resultat amb l'enllaç del sorteig.",
        ],
        "fim": "El servei és gratuït, no cal registre i no guarda els vostres fitxers. Podeu començar ara mateix.",
    },
    "uk": {
        "titulo": "Як провести лотерею для пожежної команди",
        "intro": "Лотереї — традиційна допомога добровільним пожежним командам: на спорядження, машини та щорічне свято. З Генератором лотерей ви за кілька хвилин зробите пронумеровані квитки з емблемою команди: без Canva і без встановлення програм.",
        "passos": [
            ("Домовтеся про головне", "Вирішіть, які будуть призи (їх часто дарують місцеві крамниці та підприємства), ціну квитка, скільки квитків друкувати і дату розіграшу, наприклад у річницю команди. Перед продажем дізнайтеся в місцевій владі, чи потрібні для лотереї дозвіл або повідомлення: правила залежать від виду лотереї."),
            ("Створіть квиток", "У галереї виберіть дизайн (Bombeiros, Solidária…) і напишіть назву команди, призи та дату. Додайте емблему як логотип (PNG або JPG) і виберіть колір номерів. Якщо хочете щось своє, скористайтеся Редактором шаблонів."),
            ("Одна серія на продавця чи район", "У полі «Префікс або серії» напишіть, наприклад, A-, B-, C-: кожен продавець, частина чи район отримає свої квитки (A-0001, B-0001…) і свої файли, тож видно, хто продав найбільше. У «Пропустити номери» приберіть зарезервовані номери."),
            ("Друк і вирізання", "Виберіть папір (зазвичай підходить A4) і мітки для обрізання: програма заповнює аркуш квитками. Надрукуйте й різіть по мітках; кольоровий папір допоможе розрізнити серії. У квитків є корінець, тому номер зазначено двічі."),
            ("Облік продажів і розіграш", "Експортуйте список квитків (CSV) і контрольний аркуш продажів, щоб передати кожному продавцю. У день розіграшу відкрийте сторінку «Розіграш»: з публічним зерном (наприклад, результатом лотереї) будь-хто зможе перевірити підсумок."),
        ],
        "dicas": [
            "Видавайте блоки квитків під запис у списку й відзначайте, хто який блок узяв.",
            "Напишіть на квитку контакт команди та строк отримання призів.",
            "Публічно подякуйте тим, хто дав призи, і опублікуйте результат з посиланням на розіграш.",
        ],
        "fim": "Сервіс безкоштовний, без реєстрації й не зберігає ваших файлів. Можна починати вже зараз.",
    },
    "id": {
        "titulo": "Cara membuat undian untuk pemadam kebakaran",
        "intro": "Undian adalah dukungan tradisional bagi regu pemadam kebakaran sukarela: untuk peralatan, kendaraan, dan perayaan tahunan. Dengan Pembuat Undian Anda bisa membuat tiket bernomor berlambang regu dalam beberapa menit: tanpa Canva dan tanpa memasang program.",
        "passos": [
            ("Sepakati hal pokok", "Tentukan hadiah (sering disumbangkan toko dan usaha setempat), harga tiket, jumlah tiket yang dicetak, dan tanggal pengundian, misalnya pada hari jadi regu. Sebelum menjual, tanyakan ke pemerintah setempat apakah undian memerlukan izin atau pemberitahuan: aturannya bergantung pada jenis undian."),
            ("Rancang tiket", "Di galeri pilih desain (Bombeiros, Solidária…) dan tulis nama regu, hadiah, dan tanggal. Tambahkan lambang regu sebagai logo (PNG atau JPG) dan pilih warna nomor. Untuk desain sendiri, gunakan Editor templat."),
            ("Satu seri per penjual atau wilayah", "Di «Awalan atau seri» tulis, misalnya, A-, B-, C-: setiap penjual, pos, atau wilayah mendapat tiket (A-0001, B-0001…) dan berkasnya sendiri, sehingga terlihat siapa yang paling banyak menjual. Di «Lewati nomor» keluarkan nomor yang dicadangkan."),
            ("Cetak dan gunting", "Pilih kertas (biasanya A4 cukup) dan tanda potong: program memenuhi lembar dengan tiket. Cetak lalu gunting mengikuti tanda; kertas berwarna membantu membedakan seri. Tiket punya kupon, jadi nomornya muncul dua kali."),
            ("Pantau penjualan dan lakukan pengundian", "Ekspor daftar tiket (CSV) dan lembar kontrol penjualan untuk diberikan kepada setiap penjual. Pada hari pengundian gunakan halaman «Pengundian»: dengan seed publik (misalnya hasil lotere) siapa pun dapat memastikan hasilnya."),
        ],
        "dicas": [
            "Serahkan blok tiket dengan mencatatnya di daftar dan catat siapa yang membawa tiap blok.",
            "Tulis di tiket kontak regu dan batas waktu pengambilan hadiah.",
            "Ucapkan terima kasih secara terbuka kepada penyumbang hadiah dan umumkan hasil beserta tautan pengundian.",
        ],
        "fim": "Layanan ini gratis, tanpa pendaftaran dan tidak menyimpan berkas Anda. Anda bisa mulai sekarang.",
    },
    "vi": {
        "titulo": "Cách tổ chức bốc thăm cho đội cứu hỏa",
        "intro": "Bốc thăm là cách hỗ trợ truyền thống cho các đội cứu hỏa tình nguyện: mua trang thiết bị, xe cộ và tổ chức lễ hội hằng năm. Với Trình tạo vé số, bạn làm vé đánh số có huy hiệu của đội chỉ trong vài phút: không cần Canva, không cần cài phần mềm.",
        "passos": [
            ("Thống nhất những điều cơ bản", "Quyết định giải thưởng (thường do cửa hàng và doanh nghiệp trong vùng tặng), giá vé, số vé sẽ in và ngày bốc thăm, chẳng hạn vào ngày kỷ niệm của đội. Trước khi bán, hãy hỏi chính quyền địa phương xem cuộc bốc thăm có cần giấy phép hay thông báo không: quy định phụ thuộc vào loại hình."),
            ("Thiết kế vé", "Trong thư viện, chọn một mẫu (Bombeiros, Solidária…) rồi viết tên đội, giải thưởng và ngày. Thêm huy hiệu làm logo (PNG hoặc JPG) và chọn màu cho các số. Muốn mẫu riêng, hãy dùng Trình chỉnh sửa mẫu."),
            ("Mỗi người bán hoặc khu vực một sê-ri", "Ở «Tiền tố hoặc sê-ri», gõ chẳng hạn A-, B-, C-: mỗi người bán, đồn hoặc khu vực nhận vé (A-0001, B-0001…) và tệp riêng, nhờ đó biết ai bán nhiều nhất. Ở «Bỏ qua các số», loại những số để dành."),
            ("In và cắt", "Chọn giấy (thường A4 là đủ) và dấu cắt: chương trình xếp đầy tờ giấy bằng vé. In rồi cắt theo dấu; dùng giấy màu để phân biệt các sê-ri. Vé có cuống nên số xuất hiện hai lần."),
            ("Theo dõi doanh số và bốc thăm", "Xuất danh sách vé (CSV) và bảng kiểm soát doanh số để đưa cho từng người bán. Đến ngày bốc thăm, dùng trang «Bốc thăm»: với hạt giống công khai (ví dụ kết quả xổ số), ai cũng có thể kiểm chứng kết quả."),
        ],
        "dicas": [
            "Chỉ giao các xấp vé khi đã ghi vào danh sách, và ghi lại ai nhận xấp nào.",
            "Viết lên vé thông tin liên lạc của đội và hạn nhận giải thưởng.",
            "Công khai cảm ơn những người tặng giải thưởng và công bố kết quả kèm liên kết bốc thăm.",
        ],
        "fim": "Dịch vụ miễn phí, không cần đăng ký và không lưu tệp của bạn. Bạn có thể bắt đầu ngay.",
    },
}

FESTAS = {
    "ca": {
        "titulo": "Com fer una rifa per a la festa del barri",
        "intro": "En una festa de barri, de poble o en una revetlla, la rifa anima la nit i ajuda a pagar les despeses de la comissió de festes. Amb el Generador de Rifes feu butlletes numerades en pocs minuts: sense Canva ni programes per instal·lar. Dissenyeu, imprimiu i retalleu.",
        "passos": [
            ("Acordeu l'essencial", "Decidiu els premis (cistelles i regals dels comerciants de la zona), el preu de la butlleta, quantes butlletes s'imprimiran i l'hora del sorteig durant la festa. Abans de vendre, consulteu a l'ajuntament si la rifa necessita llicència o comunicació: les normes depenen del tipus de rifa."),
            ("Dissenyeu la butlleta", "A la galeria trieu un disseny (Arraial, Santos Populares…) i escriviu el nom de la festa, els premis, el lloc i la data. Si voleu alguna cosa a mida, feu servir l'Editor de plantilles i afegiu textos, línies i rectangles."),
            ("Una sèrie per dia o venedor", "A «Prefix o sèries» escriviu, per exemple, A-, B-, C- (divendres, dissabte i diumenge, o una per carrer o venedor): cada sèrie té les seves butlletes (A-0001, B-0001…) i els seus fitxers, i així se sap què ha venut cadascú. Podeu donar un color a cada sèrie."),
            ("Imprimiu i retalleu", "Trieu el paper (l'A4 sol anar bé) i les marques de tall: el programa omple el full de butlletes. Imprimiu i retalleu per les marques; amb paper de color distingiu les sèries. Les butlletes tenen taló, per això el número apareix dues vegades."),
            ("Controleu les vendes i sortegeu", "Exporteu la llista de butlletes (CSV) i el full de control de vendes per lliurar a cada venedor. A l'hora del sorteig feu servir la pàgina «Sorteig»: amb una llavor pública (per exemple, la loteria) qui sigui present pot comprovar el resultat des del mòbil."),
        ],
        "dicas": [
            "Imprimiu més butlletes de les que penseu vendre: en una festa, les vendes solen pujar en les últimes hores.",
            "Anuncieu el sorteig al cartell i per megafonia, amb l'hora, i demaneu a qui compra que escrigui el contacte al taló.",
            "Guardeu els talons en una caixa fins al sorteig i comproveu el número premiat amb el taló a la mà.",
        ],
        "fim": "El servei és gratuït, no cal registre i no guarda els vostres fitxers. Podeu començar ara mateix.",
    },
    "uk": {
        "titulo": "Як провести лотерею на святі району",
        "intro": "На святі району, села чи вуличному гулянні лотерея оживляє вечір і допомагає покрити витрати оргкомітету. З Генератором лотерей ви за кілька хвилин зробите пронумеровані квитки: без Canva і без встановлення програм. Створіть, надрукуйте й розріжте.",
        "passos": [
            ("Домовтеся про головне", "Вирішіть, які будуть призи (кошики й подарунки від місцевих торговців), ціну квитка, скільки квитків друкувати і час розіграшу під час свята. Перед продажем дізнайтеся в місцевій владі, чи потрібні для лотереї дозвіл або повідомлення: правила залежать від виду лотереї."),
            ("Створіть квиток", "У галереї виберіть дизайн (Arraial, Santos Populares…) і напишіть назву свята, призи, місце й дату. Якщо хочете щось своє, скористайтеся Редактором шаблонів і додайте тексти, лінії та прямокутники."),
            ("Одна серія на день чи продавця", "У полі «Префікс або серії» напишіть, наприклад, A-, B-, C- (п'ятниця, субота й неділя або по одній на вулицю чи продавця): у кожної серії свої квитки (A-0001, B-0001…) і свої файли, тож видно, скільки продав кожен. Кожній серії можна дати колір."),
            ("Друк і вирізання", "Виберіть папір (зазвичай підходить A4) і мітки для обрізання: програма заповнює аркуш квитками. Надрукуйте й різіть по мітках; кольоровий папір допоможе розрізнити серії. У квитків є корінець, тому номер зазначено двічі."),
            ("Облік продажів і розіграш", "Експортуйте список квитків (CSV) і контрольний аркуш продажів, щоб передати кожному продавцю. Під час розіграшу відкрийте сторінку «Розіграш»: з публічним зерном (наприклад, результатом лотереї) будь-хто з присутніх зможе перевірити підсумок на телефоні."),
        ],
        "dicas": [
            "Друкуйте більше квитків, ніж розраховуєте продати: на святі продажі зазвичай зростають в останні години.",
            "Оголосіть розіграш на афіші й через гучномовець, із часом, і попросіть покупців написати контакт на корінці.",
            "Зберігайте корінці в коробці до розіграшу й перевіряйте виграшний номер із корінцем у руках.",
        ],
        "fim": "Сервіс безкоштовний, без реєстрації й не зберігає ваших файлів. Можна починати вже зараз.",
    },
    "id": {
        "titulo": "Cara membuat undian untuk pesta warga",
        "intro": "Di pesta warga, perayaan desa, atau festival jalanan, undian memeriahkan malam dan membantu menutup biaya panitia. Dengan Pembuat Undian Anda bisa membuat tiket bernomor dalam beberapa menit: tanpa Canva dan tanpa memasang program. Rancang, cetak, dan gunting.",
        "passos": [
            ("Sepakati hal pokok", "Tentukan hadiah (keranjang dan hadiah dari pedagang setempat), harga tiket, jumlah tiket yang dicetak, dan jam pengundian selama acara. Sebelum menjual, tanyakan ke pemerintah setempat apakah undian memerlukan izin atau pemberitahuan: aturannya bergantung pada jenis undian."),
            ("Rancang tiket", "Di galeri pilih desain (Arraial, Santos Populares…) dan tulis nama acara, hadiah, tempat, dan tanggal. Untuk desain sendiri, gunakan Editor templat dan tambahkan teks, garis, dan persegi panjang."),
            ("Satu seri per hari atau penjual", "Di «Awalan atau seri» tulis, misalnya, A-, B-, C- (Jumat, Sabtu, dan Minggu, atau satu per jalan atau penjual): setiap seri punya tiket (A-0001, B-0001…) dan berkasnya sendiri, sehingga terlihat berapa yang dijual masing-masing. Setiap seri bisa diberi warna."),
            ("Cetak dan gunting", "Pilih kertas (biasanya A4 cukup) dan tanda potong: program memenuhi lembar dengan tiket. Cetak lalu gunting mengikuti tanda; kertas berwarna membantu membedakan seri. Tiket punya kupon, jadi nomornya muncul dua kali."),
            ("Pantau penjualan dan lakukan pengundian", "Ekspor daftar tiket (CSV) dan lembar kontrol penjualan untuk diberikan kepada setiap penjual. Saat pengundian gunakan halaman «Pengundian»: dengan seed publik (misalnya hasil lotere) siapa pun yang hadir dapat memastikan hasilnya lewat ponsel."),
        ],
        "dicas": [
            "Cetak lebih banyak tiket daripada perkiraan penjualan: di sebuah pesta, penjualan biasanya naik pada jam-jam terakhir.",
            "Umumkan pengundian di poster dan lewat pengeras suara, beserta jamnya, dan minta pembeli menulis kontak pada kupon.",
            "Simpan kupon dalam kotak sampai pengundian dan periksa nomor pemenang dengan kupon di tangan.",
        ],
        "fim": "Layanan ini gratis, tanpa pendaftaran dan tidak menyimpan berkas Anda. Anda bisa mulai sekarang.",
    },
    "vi": {
        "titulo": "Cách tổ chức bốc thăm cho lễ hội khu phố",
        "intro": "Trong lễ hội khu phố, hội làng hay lễ hội đường phố, bốc thăm làm buổi tối thêm vui và giúp trang trải chi phí của ban tổ chức. Với Trình tạo vé số, bạn làm vé đánh số chỉ trong vài phút: không cần Canva, không cần cài phần mềm. Thiết kế, in và cắt.",
        "passos": [
            ("Thống nhất những điều cơ bản", "Quyết định giải thưởng (giỏ quà và quà tặng của các tiểu thương trong vùng), giá vé, số vé sẽ in và giờ bốc thăm trong lúc diễn ra lễ hội. Trước khi bán, hãy hỏi chính quyền địa phương xem cuộc bốc thăm có cần giấy phép hay thông báo không: quy định phụ thuộc vào loại hình."),
            ("Thiết kế vé", "Trong thư viện, chọn một mẫu (Arraial, Santos Populares…) rồi viết tên lễ hội, giải thưởng, địa điểm và ngày. Muốn mẫu riêng, hãy dùng Trình chỉnh sửa mẫu và thêm văn bản, đường kẻ, hình chữ nhật."),
            ("Mỗi ngày hoặc người bán một sê-ri", "Ở «Tiền tố hoặc sê-ri», gõ chẳng hạn A-, B-, C- (thứ Sáu, thứ Bảy và Chủ nhật, hoặc mỗi con phố hay người bán một sê-ri): mỗi sê-ri có vé (A-0001, B-0001…) và tệp riêng, nhờ đó biết mỗi người bán được bao nhiêu. Có thể gán cho mỗi sê-ri một màu."),
            ("In và cắt", "Chọn giấy (thường A4 là đủ) và dấu cắt: chương trình xếp đầy tờ giấy bằng vé. In rồi cắt theo dấu; dùng giấy màu để phân biệt các sê-ri. Vé có cuống nên số xuất hiện hai lần."),
            ("Theo dõi doanh số và bốc thăm", "Xuất danh sách vé (CSV) và bảng kiểm soát doanh số để đưa cho từng người bán. Đến giờ bốc thăm, dùng trang «Bốc thăm»: với hạt giống công khai (ví dụ kết quả xổ số), ai có mặt cũng có thể kiểm chứng kết quả trên điện thoại."),
        ],
        "dicas": [
            "In nhiều vé hơn dự kiến bán được: ở lễ hội, doanh số thường tăng vào những giờ cuối.",
            "Thông báo giờ bốc thăm trên áp phích và qua loa, và nhờ người mua viết thông tin liên lạc lên cuống vé.",
            "Giữ các cuống vé trong một chiếc hộp cho đến lúc bốc thăm và đối chiếu số trúng thưởng với cuống vé trên tay.",
        ],
        "fim": "Dịch vụ miễn phí, không cần đăng ký và không lưu tệp của bạn. Bạn có thể bắt đầu ngay.",
    },
}


# ---------------------------------------------------------------- guia das paroquias (3.36.0)
IGREJAS = {
    "ca": {
        "titulo": "Com fer una rifa per a la parròquia",
        "intro": "El dubte més gran sobre una rifa parroquial sol ser sempre el mateix: «és realment honesta?». La resposta és el sorteig verificable del Generador de Rifes: la llavor és pública i qualsevol feligrès pot repetir el càlcul i comprovar el número guanyador, sense haver de confiar només en la paraula de qui organitza. Les rifes també són una tradició de les festes parroquials, que ajuden a pagar les obres de l'església, les cistelles de Nadal o la catequesi: en pocs minuts feu butlletes numerades amb el nom o l'escut de la parròquia, sense Canva ni programes per instal·lar.",
        "passos": [
            ("Decidiu-ho amb el consell parroquial", "Amb el consell parroquial o la comissió de festes, acordeu els premis (sovint oferts per feligresos i pel comerç local), el preu de la butlleta, quantes butlletes s'imprimiran i la data del sorteig, per exemple al final de la festa del patró. Abans de vendre, consulteu amb l'autoritat competent de la vostra zona si la rifa necessita llicència o comunicació: les normes varien segons la zona i el tipus de rifa."),
            ("Doneu a la butlleta la cara de la parròquia", "A la galeria trieu un disseny (Quermesse, Natal, Solidária…) i escriviu el nom de la parròquia, per a què serveixen els diners, els premis i la data: els feligresos solen comprar més quan saben on van els diners recaptats. Afegiu l'escut o el logotip de la parròquia (PNG o JPG); si voleu alguna cosa a mida, feu servir l'Editor de plantilles."),
            ("Una sèrie per grup", "A «Prefix o sèries» escriviu, per exemple, A-, B-, C-: cada grup (catequesi, escoltes, cor, joves) rep les seves butlletes (A-0001, B-0001…) i els seus fitxers, i així se sap qui ha venut més. A «Omet números» traieu els que queden reservats."),
            ("Imprimiu, retalleu i repartiu per grups", "Trieu el paper (l'A4 sol anar bé) i les marques de tall: el programa omple el full de butlletes. Retalleu per les marques i doneu un bloc a cada grup o voluntari, per vendre entre la comunitat; el paper de color ajuda a distingir les sèries. Les butlletes tenen taló, per això el número apareix dues vegades."),
            ("Sortegeu a la vista de tots i rendiu comptes", "Exporteu la llista de butlletes (CSV) i el full de control de vendes per lliurar a cada grup. El dia del sorteig feu servir la pàgina «Sorteig»: amb una llavor pública (per exemple, la loteria o un número del diari) qualsevol feligrès pot repetir el càlcul i confirmar el resultat. Publiqueu després, al full parroquial o al tauler, en què s'han usat els diners — la millor manera de mantenir la confiança any rere any."),
        ],
        "dicas": [
            "Escriviu a la butlleta per a què serveixen els diners (obres, cistelles, catequesi): qui coneix la finalitat sol comprar més, i amb més confiança.",
            "Demaneu a cada grup que retorni els talons i els diners de cada bloc abans del dia del sorteig.",
            "Anuncieu el resultat al full parroquial, al tauler de l'església i a les xarxes socials, amb l'enllaç del sorteig, perquè qui no hi va ser també ho pugui comprovar.",
        ],
        "fim": "El servei és gratuït, no cal registre, i no guarda cap dels vostres fitxers al servidor: podeu començar ara mateix.",
    },
    "uk": {
        "titulo": "Як провести лотерею для парафії",
        "intro": "Найбільший сумнів щодо парафіяльної лотереї майже завжди однаковий: «а чи це справді чесно?». Відповідь — у перевірюваному розіграші Генератора лотерей: зерно публічне, і будь-який парафіянин може повторити обчислення й перевірити виграшний номер, не покладаючись лише на слово організаторів. Лотереї — ще й традиція парафіяльних свят, що допомагають оплатити ремонт храму, різдвяні подарунки чи роботу з молоддю: за кілька хвилин ви зробите пронумеровані квитки з назвою чи емблемою парафії, без Canva і без встановлення програм.",
        "passos": [
            ("Вирішіть це разом із парафіяльною радою", "Разом із парафіяльною радою чи оргкомітетом свята домовтеся про призи (їх часто дарують парафіяни та місцеві крамниці), ціну квитка, скільки квитків друкувати і дату розіграшу, наприклад наприкінці храмового свята. Перед продажем дізнайтеся в компетентному органі вашого регіону, чи потрібні для лотереї дозвіл або повідомлення: правила відрізняються залежно від регіону і виду лотереї."),
            ("Надайте квитку обличчя парафії", "У галереї виберіть дизайн (Quermesse, Natal, Solidária…) і напишіть назву парафії, на що підуть гроші, призи та дату: парафіяни зазвичай купують більше, коли знають, куди йде виручка. Додайте емблему чи логотип парафії (PNG або JPG); якщо хочете щось своє, скористайтеся Редактором шаблонів."),
            ("Одна серія на групу", "У полі «Префікс або серії» напишіть, наприклад, A-, B-, C-: кожна група (недільна школа, скаути, хор, молодь) отримає свої квитки (A-0001, B-0001…) і свої файли, тож видно, хто продав найбільше. У «Пропустити номери» приберіть зарезервовані номери."),
            ("Надрукуйте, вирізайте й роздайте групам", "Виберіть папір (зазвичай підходить A4) і мітки для обрізання: програма заповнює аркуш квитками. Різіть за мітками і дайте кожній групі чи волонтеру пачку для продажу серед парафії; кольоровий папір допоможе розрізнити серії. У квитків є корінець, тому номер зазначено двічі."),
            ("Проведіть розіграш відкрито і прозвітуйте", "Експортуйте список квитків (CSV) і контрольний аркуш продажів, щоб передати кожній групі. У день розіграшу відкрийте сторінку «Розіграш»: з публічним зерном (наприклад, результатом лотереї чи номером із газети) будь-який парафіянин може повторити обчислення й перевірити підсумок. Потім оприлюдніть у парафіяльному листку чи на дошці, на що пішли гроші — найкращий спосіб зберігати довіру рік за роком."),
        ],
        "dicas": [
            "Напишіть на квитку, на що підуть гроші (ремонт, подарунки, молодь): хто знає мету, зазвичай купує більше — і з більшою довірою.",
            "Попросіть кожну групу здати корінці й гроші за кожен блок до дня розіграшу.",
            "Оголосіть результат у парафіяльному листку, на дошці оголошень храму й у соцмережах із посиланням на розіграш, щоб перевірити міг і той, хто не був присутній.",
        ],
        "fim": "Сервіс безкоштовний, без реєстрації, і не зберігає жодного з ваших файлів на сервері: можна починати прямо зараз.",
    },
    "id": {
        "titulo": "Cara membuat undian untuk gereja",
        "intro": "Keraguan terbesar tentang undian gereja hampir selalu sama: “apakah ini benar-benar jujur?”. Jawabannya adalah pengundian yang dapat diverifikasi dari Pembuat Undian: seed-nya bersifat publik dan setiap jemaat dapat mengulang hitungannya dan memeriksa nomor pemenang, tanpa harus hanya mempercayai kata-kata penyelenggara. Undian juga tradisi bazar dan perayaan gereja, membantu membayar perbaikan gedung gereja, bingkisan Natal, atau kegiatan sekolah minggu: dalam beberapa menit Anda membuat tiket bernomor dengan nama atau lambang gereja, tanpa Canva dan tanpa memasang program.",
        "passos": [
            ("Tentukan ini bersama dewan gereja", "Bersama dewan gereja atau panitia perayaan, sepakati hadiah (sering disumbangkan jemaat dan toko setempat), harga tiket, jumlah tiket yang dicetak, dan tanggal pengundian, misalnya di akhir perayaan. Sebelum menjual, tanyakan ke instansi yang berwenang di daerah Anda apakah undian memerlukan izin atau pemberitahuan: aturannya berbeda menurut daerah dan jenis undian."),
            ("Beri tiket wajah gereja Anda", "Di galeri pilih desain (Quermesse, Natal, Solidária…) dan tulis nama gereja, untuk apa dana itu, hadiah, dan tanggal: jemaat biasanya membeli lebih banyak jika tahu ke mana hasilnya pergi. Tambahkan lambang atau logo gereja (PNG atau JPG); untuk desain sendiri, gunakan Editor templat."),
            ("Satu seri per kelompok", "Di «Awalan atau seri» tulis, misalnya, A-, B-, C-: setiap kelompok (sekolah minggu, pramuka, paduan suara, pemuda) mendapat tiket (A-0001, B-0001…) dan berkasnya sendiri, sehingga terlihat siapa yang paling banyak menjual. Di «Lewati nomor» keluarkan nomor yang dicadangkan."),
            ("Cetak, gunting, dan bagikan ke kelompok", "Pilih kertas (biasanya A4 cukup) dan tanda potong: program memenuhi lembar dengan tiket. Gunting mengikuti tanda dan berikan satu bundel ke setiap kelompok atau relawan untuk dijual di antara jemaat; kertas berwarna membantu membedakan seri. Tiket punya kupon, jadi nomornya muncul dua kali."),
            ("Lakukan pengundian secara terbuka dan laporkan", "Ekspor daftar tiket (CSV) dan lembar kontrol penjualan untuk diberikan kepada setiap kelompok. Pada hari pengundian gunakan halaman «Pengundian»: dengan seed publik (misalnya hasil lotere atau nomor dari koran), setiap jemaat dapat mengulang hitungan dan memastikan hasilnya. Setelah itu, umumkan di warta jemaat atau papan pengumuman untuk apa dana itu digunakan — cara terbaik untuk menjaga kepercayaan dari tahun ke tahun."),
        ],
        "dicas": [
            "Tulis di tiket untuk apa dana itu (perbaikan, bingkisan, sekolah minggu): orang yang tahu tujuannya biasanya membeli lebih banyak, dan dengan lebih percaya.",
            "Minta setiap kelompok mengembalikan kupon dan uang tiap blok sebelum hari pengundian.",
            "Umumkan hasil di warta jemaat, papan pengumuman gereja, dan media sosial beserta tautan pengundian, agar yang tidak hadir pun bisa memeriksanya.",
        ],
        "fim": "Layanan ini gratis, tanpa pendaftaran, dan tidak menyimpan satu pun berkas Anda di server: Anda bisa mulai sekarang juga.",
    },
    "vi": {
        "titulo": "Cách tổ chức bốc thăm cho giáo xứ",
        "intro": "Nghi ngờ lớn nhất về một cuộc bốc thăm giáo xứ hầu như luôn giống nhau: “việc này có thực sự công bằng không?”. Câu trả lời là lần bốc thăm có thể kiểm chứng của Trình tạo vé số: hạt giống được công khai và bất kỳ giáo dân nào cũng có thể làm lại phép tính và kiểm tra số trúng, mà không phải chỉ tin vào lời của người tổ chức. Bốc thăm cũng là truyền thống của các hội chợ và lễ hội giáo xứ, giúp trả chi phí sửa nhà thờ, quà Giáng sinh hay lớp giáo lý: chỉ trong vài phút bạn làm được vé đánh số có tên hoặc huy hiệu giáo xứ, không cần Canva, không cần cài phần mềm.",
        "passos": [
            ("Quyết định cùng hội đồng giáo xứ", "Cùng hội đồng giáo xứ hoặc ban tổ chức lễ hội, thống nhất giải thưởng (thường do giáo dân và cửa hàng trong vùng tặng), giá vé, số vé sẽ in và ngày bốc thăm, chẳng hạn vào cuối lễ hội. Trước khi bán, hãy hỏi cơ quan có thẩm quyền ở khu vực của bạn xem cuộc bốc thăm có cần giấy phép hay thông báo không: quy định khác nhau theo khu vực và loại hình bốc thăm."),
            ("Cho tấm vé mang gương mặt giáo xứ", "Trong thư viện, chọn một mẫu (Quermesse, Natal, Solidária…) rồi viết tên giáo xứ, số tiền dùng vào việc gì, giải thưởng và ngày: giáo dân thường mua nhiều hơn khi biết tiền thu được dùng vào đâu. Thêm huy hiệu hoặc logo của giáo xứ (PNG hoặc JPG); muốn mẫu riêng, hãy dùng Trình chỉnh sửa mẫu."),
            ("Mỗi nhóm một sê-ri", "Ở «Tiền tố hoặc sê-ri», gõ chẳng hạn A-, B-, C-: mỗi nhóm (giáo lý, hướng đạo, ca đoàn, giới trẻ) nhận vé (A-0001, B-0001…) và tệp riêng, nhờ đó biết ai bán nhiều nhất. Ở «Bỏ qua các số», loại những số để dành."),
            ("In, cắt và chia cho các nhóm", "Chọn giấy (thường A4 là đủ) và dấu cắt: chương trình xếp đầy tờ giấy bằng vé. Cắt theo dấu rồi đưa mỗi nhóm hoặc người tình nguyện một xấp để bán trong giáo xứ; dùng giấy màu để phân biệt các sê-ri. Vé có cuống nên số xuất hiện hai lần."),
            ("Bốc thăm công khai và báo cáo rõ ràng", "Xuất danh sách vé (CSV) và bảng kiểm soát doanh số để đưa cho từng nhóm. Đến ngày bốc thăm, dùng trang «Bốc thăm»: với hạt giống công khai (ví dụ kết quả xổ số hoặc một số trên báo), bất kỳ giáo dân nào cũng có thể làm lại phép tính và xác nhận kết quả. Sau đó, hãy công khai trên bản tin hoặc bảng thông báo số tiền đã được dùng vào việc gì — cách tốt nhất để giữ niềm tin từ năm này qua năm khác."),
        ],
        "dicas": [
            "Viết lên vé số tiền dùng vào việc gì (sửa chữa, quà tặng, giáo lý): người biết mục đích thường mua nhiều hơn, và tin tưởng hơn.",
            "Nhờ mỗi nhóm nộp lại các cuống vé và tiền của từng xấp trước ngày bốc thăm.",
            "Công bố kết quả trên bản tin giáo xứ, bảng thông báo nhà thờ và mạng xã hội, kèm liên kết bốc thăm, để ai không có mặt cũng kiểm tra được.",
        ],
        "fim": "Dịch vụ này miễn phí, không cần đăng ký, và không lưu bất kỳ tệp nào của bạn trên máy chủ: bạn có thể bắt đầu ngay bây giờ.",
    },
}
