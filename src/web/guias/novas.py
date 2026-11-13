"""Os guias «como fazer» nas línguas de um ficheiro só (catalão, ucraniano, indonésio, vietnamita): juntam-se a `escolas.DADOS` e `associacoes.DADOS` em `__init__.py`.

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
