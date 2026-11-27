"""Os guias «como fazer» nas línguas de um ficheiro só (catalão, ucraniano, indonésio, vietnamita): juntam-se aos de `escolas.DADOS`, `associacoes.DADOS`, `clubes.DADOS`, `bombeiros.DADOS` e `festas.DADOS` em `__init__.py`.

Mesmo formato dos outros: título, introdução, 5 passos (título, texto), 3 dicas e uma frase final. Sem revisão nativa; as regras de licença de uma rifa variam por país,
por isso o 1.º passo de ambos manda confirmar com a autoridade local. Ver docs/LINGUAS.md.
"""

ESCOLAS = {
    "ca": {
        "titulo": "Com fer una rifa per a l'escola",
        "intro": "A una escola, la rifa normalment neix a l'associació de pares i mares o al consell escolar: falta diners per a la sortida, per renovar el material de l'aula o per a la festa de Nadal, i una rifa ho resol en poques setmanes. Amb el Generador de Rifes les butlletes numerades surten en pocs minuts, sense Canva ni programes per instal·lar: trieu un disseny, escriviu el text, imprimiu i retalleu.",
        "passos": [
            ("Decidiu-ho a l'associació de pares", "Amb l'associació de pares i mares o el consell escolar, acordeu la destinació dels diners (la sortida, els regals de Nadal, material nou per a l'aula), els premis — sovint donats per les mateixes famílies i el comerç de la zona —, el preu de la butlleta i la data del sorteig, preferiblement abans d'una reunió de pares o del final del trimestre. Abans de vendre, consulteu amb l'autoritat local si la rifa necessita llicència o notificació: les normes depenen del tipus de rifa."),
            ("Doneu a la butlleta la cara de l'escola", "A la galeria hi ha un disseny fet per a això, anomenat Escola; trieu-lo, o un altre, i escriviu el nom de l'escola, el motiu de la rifa, els premis i la data. No escriviu mai el nom d'un alumne ni altres dades personals a la butlleta: n'hi ha prou amb el nom de qui compra, al taló. Qui vulgui alguna cosa a mida pot dissenyar la butlleta a l'Editor de plantilles i afegir el logotip de l'escola a «La vostra marca»."),
            ("Una sèrie per classe, una per pare venedor", "A «Prefix o sèries» escriviu, per exemple, 5A-, 5B-, 6A-: cada classe es queda amb les seves butlletes (5A-0001, 5B-0001…) i els seus fitxers, el que facilita saber quina classe n'ha venut més i donar els números al pare o mare responsable de cada classe, en lloc de compartir un sol bloc. Podeu donar un color a cada sèrie."),
            ("Imprimiu amb marge abans de final de trimestre", "Trieu el paper (l'A4 sol anar bé) i les marques de tall: el programa omple el full de butlletes tot sol. Imprimiu amb un marge de seguretat — millor tenir butlletes de més que de menys abans de la reunió de pares o la sortida de la classe — i retalleu seguint les marques; el paper de color ajuda a distingir les classes. Les butlletes tenen taló, per això el número queda registrat dues vegades."),
            ("Recolliu els diners i sortegeu a la vista de tots", "Exporteu la llista de butlletes (CSV) i el full de control de vendes, un per classe, perquè cada professor o pare responsable comprovi què falta retornar. El dia del sorteig — per exemple a la festa de final de trimestre — feu servir la pàgina «Sorteig»: amb una llavor pública (per exemple, el resultat de la loteria), qualsevol família pot repetir el càlcul i confirmar el número sortit."),
        ],
        "dicas": [
            "No escriviu mai el nom d'un infant ni altres dades personals a la butlleta: el nom de qui compra, al taló, és suficient — així les dades dels alumnes queden fora del tot.",
            "Imprimiu sempre unes quantes butlletes més de les que penseu vendre i doneu a cada classe el seu propi interval de números, perquè no hi hagi confusions entre classes.",
            "Anuncieu el resultat al tauler de l'escola, al butlletí o al grup de pares de la classe, amb l'enllaç del sorteig, perquè qui no hi va poder ser també ho pugui comprovar.",
        ],
        "fim": "El servei és gratuït, no cal registre i no guarda ni els vostres fitxers ni els dels alumnes. Podeu començar ara mateix.",
    },
    "uk": {
        "titulo": "Як провести лотерею для школи",
        "intro": "У школі лотерея зазвичай починається з батьківського комітету або шкільної ради: не вистачає грошей на екскурсію, на нове обладнання для класу чи на новорічне свято, і лотерея вирішує це за кілька тижнів. З Генератором лотерей пронумеровані квитки готові за кілька хвилин, без Canva і без встановлення програм: виберіть дизайн, напишіть текст, надрукуйте й виріжте.",
        "passos": [
            ("Вирішіть це з батьківським комітетом", "З батьківським комітетом або шкільною радою домовтеся, на що підуть гроші (екскурсія, новорічні подарунки, нове обладнання для класу), про призи — їх часто дарують самі родини та місцеві магазини —, про ціну квитка й дату розіграшу, бажано до батьківських зборів або кінця семестру. Перед продажем дізнайтеся в місцевої влади, чи потрібні для лотереї дозвіл або повідомлення: правила залежать від виду лотереї."),
            ("Додайте квитку обличчя школи", "У галереї є дизайн, створений саме для цього, під назвою Школа; виберіть його або інший і впишіть назву школи, мету лотереї, призи та дату. Ніколи не пишіть на квитку ім'я учня чи інші особисті дані: достатньо імені покупця на корінці. Якщо хочете щось своє, оформте квиток у Редакторі шаблонів і додайте логотип школи в розділі «Ваш бренд»."),
            ("Одна серія на клас, одна на батька-продавця", "У полі «Префікс або серії» впишіть, наприклад, 5А-, 5Б-, 6А-: кожен клас зберігає свої квитки (5А-0001, 5Б-0001…) і свої файли, тож легко видно, який клас продав найбільше, а номери передаються батькам, відповідальним за цей клас, замість того, щоб ділити один спільний блок. Кожній серії можна дати колір."),
            ("Надрукуйте із запасом до кінця семестру", "Виберіть папір (зазвичай підходить A4) і мітки для обрізання: програма сама заповнює аркуш квитками. Друкуйте з невеликим запасом — краще кілька квитків зайвих, ніж замалих перед батьківськими зборами чи поїздкою класу — і ріжте по мітках; кольоровий папір допомагає розрізняти класи. Квитки мають корінець, тож номер записано двічі."),
            ("Зберіть гроші і розіграйте відкрито", "Експортуйте список квитків (CSV) і контрольний аркуш продажів, по одному на клас, щоб кожен учитель або відповідальний батько міг перевірити, що ще потрібно здати. У день розіграшу — наприклад, на святі закінчення семестру — скористайтеся сторінкою «Розіграш»: з публічним зерном (наприклад, результатом лотереї) будь-яка родина може повторити розрахунок і підтвердити виграшний номер."),
        ],
        "dicas": [
            "Ніколи не пишіть на квитку ім'я дитини чи інші особисті дані: достатньо імені покупця на корінці — так дані учнів залишаються повністю поза цим.",
            "Завжди друкуйте кілька квитків більше, ніж плануєте продати, і дайте кожному класу власний діапазон номерів, щоб класи не плутались.",
            "Оголосіть результат на шкільній дошці оголошень, у бюлетені чи в батьківській групі класу, з посиланням на розіграш, щоб і той, хто не був присутній, міг перевірити.",
        ],
        "fim": "Сервіс безкоштовний, без реєстрації, і не зберігає ні ваших файлів, ні файлів учнів. Можна починати вже зараз.",
    },
    "id": {
        "titulo": "Cara menyelenggarakan undian untuk sekolah",
        "intro": "Di sebuah sekolah, undian biasanya dimulai dari komite orang tua atau pihak sekolah: tidak ada anggaran untuk karya wisata, perlengkapan kelas baru, atau perayaan Natal, dan undian bisa menyelesaikannya dalam beberapa minggu. Dengan Pembuat Undian, tiket bernomor siap dalam hitungan menit, tanpa Canva dan tanpa memasang apa pun: pilih desain, tulis teksnya, cetak, dan gunting.",
        "passos": [
            ("Tentukan bersama komite orang tua", "Bersama komite orang tua atau pihak sekolah, sepakati untuk apa uangnya (karya wisata, hadiah Natal, perlengkapan baru untuk kelas), hadiah — sering disumbangkan keluarga sendiri dan toko setempat —, harga tiket, dan tanggal pengundian, sebaiknya sebelum rapat orang tua atau akhir semester. Sebelum menjual, tanyakan ke otoritas setempat apakah undian memerlukan izin atau pemberitahuan: aturannya bergantung pada jenis undian."),
            ("Beri tiket wajah sekolah", "Di galeri ada desain yang dibuat khusus untuk ini, bernama Sekolah; pilih itu, atau yang lain, dan tulis nama sekolah, tujuan undian, hadiah, dan tanggal. Jangan pernah menulis nama murid atau data pribadi lain pada tiket: nama pembeli di kupon sudah cukup. Jika ingin sesuatu yang khusus, rancang tiket di Editor templat dan tambahkan logo sekolah di «Merek Anda»."),
            ("Satu seri per kelas, satu per orang tua penjual", "Di «Awalan atau seri» ketik, misalnya, 5A-, 5B-, 6A-: setiap kelas menyimpan tiketnya sendiri (5A-0001, 5B-0001…) dan berkasnya sendiri, sehingga mudah dilihat kelas mana yang paling banyak menjual, dan nomor diserahkan ke orang tua yang bertanggung jawab atas kelas itu, bukan dibagi dalam satu blok bersama. Setiap seri dapat diberi warna."),
            ("Cetak dengan cadangan sebelum akhir semester", "Pilih kertas (A4 biasanya cukup) dan tanda potong: program mengisi lembar dengan tiket sendiri. Cetak dengan sedikit cadangan — lebih baik beberapa tiket berlebih daripada kurang sebelum rapat orang tua atau kunjungan kelas — lalu gunting mengikuti tanda; kertas berwarna membantu membedakan kelas. Tiket memiliki kupon, sehingga nomor tercatat dua kali."),
            ("Kumpulkan uang dan undi secara terbuka", "Ekspor daftar tiket (CSV) dan lembar kontrol penjualan, satu per kelas, agar setiap guru atau orang tua yang bertanggung jawab bisa memeriksa apa yang masih harus disetor. Pada hari pengundian — misalnya pada acara akhir semester — gunakan halaman «Pengundian»: dengan benih publik (misalnya hasil lotere), keluarga mana pun dapat mengulang perhitungan dan memastikan nomor yang keluar."),
        ],
        "dicas": [
            "Jangan pernah menulis nama anak atau data pribadi lain pada tiket: nama pembeli di kupon sudah cukup — sehingga data murid sama sekali tidak muncul di sana.",
            "Selalu cetak beberapa tiket lebih banyak daripada yang Anda rencanakan untuk dijual, dan beri setiap kelas rentang nomornya sendiri, agar tidak ada kebingungan antarkelas.",
            "Umumkan hasilnya di papan pengumuman sekolah, buletin, atau grup orang tua kelas, beserta tautan pengundian, agar yang tidak bisa hadir pun bisa memeriksanya.",
        ],
        "fim": "Layanan ini gratis, tanpa pendaftaran, dan tidak menyimpan berkas Anda maupun berkas murid. Anda bisa mulai sekarang.",
    },
    "vi": {
        "titulo": "Cách tổ chức bốc thăm cho trường học",
        "intro": "Ở một trường học, việc bốc thăm thường bắt đầu từ hội phụ huynh hoặc ban giám hiệu: thiếu tiền cho chuyến tham quan, đồ dùng mới cho lớp hoặc tiệc Giáng sinh, và bốc thăm giải quyết điều đó trong vài tuần. Với Trình tạo vé số, vé đánh số sẵn sàng trong vài phút, không cần Canva và không cần cài đặt gì: chọn một thiết kế, viết nội dung, in và cắt.",
        "passos": [
            ("Quyết định cùng hội phụ huynh", "Cùng hội phụ huynh hoặc ban giám hiệu, thống nhất tiền dùng để làm gì (chuyến tham quan, quà Giáng sinh, đồ dùng mới cho lớp), giải thưởng — thường do chính các gia đình và cửa hàng địa phương tặng —, giá vé và ngày bốc thăm, tốt nhất là trước một buổi họp phụ huynh hoặc cuối học kỳ. Trước khi bán, hãy hỏi chính quyền địa phương xem cuộc bốc thăm có cần giấy phép hay thông báo không: quy định tùy theo loại bốc thăm."),
            ("Cho vé mang dáng vẻ của trường", "Trong thư viện có một thiết kế làm riêng cho việc này, tên là Trường học; hãy chọn nó, hoặc một mẫu khác, rồi ghi tên trường, mục đích bốc thăm, giải thưởng và ngày. Đừng bao giờ viết tên học sinh hay dữ liệu cá nhân khác lên vé: chỉ cần tên người mua trên cuống là đủ. Nếu muốn thứ riêng của mình, hãy thiết kế vé trong Trình chỉnh sửa mẫu và thêm logo của trường vào «Thương hiệu của bạn»."),
            ("Mỗi lớp một sê-ri, mỗi phụ huynh bán một phần", "Trong «Tiền tố hoặc sê-ri» hãy nhập, ví dụ, 5A-, 5B-, 6A-: mỗi lớp giữ vé riêng (5A-0001, 5B-0001…) và tệp riêng, giúp dễ dàng biết lớp nào bán được nhiều nhất, và số vé được giao cho phụ huynh phụ trách lớp đó thay vì chia sẻ một xấp chung. Có thể gán cho mỗi sê-ri một màu."),
            ("In dư trước khi học kỳ kết thúc", "Chọn giấy (A4 thường là đủ) và dấu cắt: chương trình tự lấp đầy tờ giấy bằng vé. In thêm một ít để dự phòng — thừa vài vé còn hơn thiếu trước buổi họp phụ huynh hay chuyến đi của lớp — rồi cắt theo dấu; giấy màu giúp phân biệt các lớp. Vé có cuống, nên số được ghi hai lần."),
            ("Thu tiền và bốc thăm công khai", "Xuất danh sách vé (CSV) và phiếu kiểm soát bán vé, mỗi lớp một phiếu, để mỗi giáo viên hay phụ huynh phụ trách kiểm tra còn phải nộp lại gì. Vào ngày bốc thăm — chẳng hạn tại buổi lễ cuối học kỳ — hãy dùng trang «Bốc thăm»: với hạt giống công khai (ví dụ kết quả xổ số), gia đình nào cũng có thể làm lại phép tính và xác nhận số trúng."),
        ],
        "dicas": [
            "Đừng bao giờ viết tên trẻ em hay dữ liệu cá nhân khác lên vé: chỉ cần tên người mua trên cuống là đủ — nhờ đó dữ liệu học sinh hoàn toàn không xuất hiện.",
            "Luôn in thêm vài vé nhiều hơn số bạn định bán và cấp cho mỗi lớp một khoảng số riêng, để không bị nhầm lẫn giữa các lớp.",
            "Thông báo kết quả trên bảng tin của trường, trong bản tin hoặc nhóm phụ huynh của lớp, kèm liên kết bốc thăm, để ai không có mặt cũng kiểm tra được.",
        ],
        "fim": "Dịch vụ miễn phí, không cần đăng ký, và không lưu tệp của bạn hay của học sinh. Bạn có thể bắt đầu ngay.",
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
        "intro": "Una rifa ajuda un club esportiu a pagar l'equipament, un desplaçament o la temporada vinent, venent sobretot als propis socis i a les famílies dels esportistes. Amb el Generador de Rifes feu butlletes numerades, amb l'escut i els colors del club, en pocs minuts: sense Canva ni programes per instal·lar.",
        "passos": [
            ("Decidiu-ho amb la junta directiva", "En una reunió de la junta, o de l'assemblea de socis si la decisió és més gran, acordeu el motiu (equipament, desplaçaments, la temporada vinent), els premis, el preu de la butlleta, quantes se n'imprimiran i la data del sorteig — per exemple al sopar d'aniversari del club o al descans del torneig anual. Abans de vendre, consulteu a l'ajuntament (o a l'entitat competent) si la rifa necessita llicència o comunicació."),
            ("Vestiu la butlleta amb els colors del club", "A la galeria trieu un disseny (Futebol, Retro…) i escriviu el nom del club, la modalitat, els premis i la data. Afegiu l'escut com a logotip (PNG o JPG) i trieu per als números els colors oficials del club, perquè la butlleta es reconegui de lluny. Si voleu alguna cosa a mida, feu servir l'Editor de plantilles."),
            ("Una sèrie per equip, categoria o soci venedor", "A «Prefix o sèries» escriviu, per exemple, A-, B-, C-: cada equip, categoria de planter o soci venedor rep les seves butlletes (A-0001, B-0001…) i els seus fitxers propis, i així se sap qui ha venut més. A «Omet números» reserveu els ja promesos a un patrocinador, i doneu un color a cada sèrie."),
            ("Imprimiu i retalleu", "Trieu el paper (l'A4 sol anar bé) i les marques de tall: el programa omple el full de butlletes. Imprimiu i retalleu per les marques; el paper de color ajuda a distingir les sèries de les diferents categories. Les butlletes tenen taló, per això el número apareix dues vegades."),
            ("Controleu les vendes i sortegeu el gran dia", "Exporteu la llista de butlletes (CSV) i el full de control de vendes per lliurar a cada entrenador, capità d'equip o soci venedor. A la final de temporada, al torneig o a la gala anual, feu servir la pàgina «Sorteig»: amb una llavor pública (per exemple, el resultat del partit de la nit o la loteria) qualsevol soci pot comprovar el resultat des del mòbil."),
        ],
        "dicas": [
            "Doneu a cada equip o categoria un interval de números i apunteu qui s'endú cada bloc de butlletes, per saber a qui demanar comptes al final.",
            "Veneu als partits a casa, als entrenaments i als socis amb la quota al corrent: qui ja és de casa sol comprar sense pensar-s'ho dues vegades.",
            "Anuncieu el resultat a les xarxes socials i al tauler del club, amb l'enllaç del sorteig, perquè tots els socis puguin comprovar-lo.",
        ],
        "fim": "El servei és gratuït, no cal registre i no guarda els vostres fitxers. Podeu començar ara mateix.",
    },
    "uk": {
        "titulo": "Як провести лотерею для клубу",
        "intro": "Лотерея допомагає спортивному клубу оплатити форму, виїзну поїздку чи наступний сезон, продаючись переважно власним членам і родинам спортсменів. З Генератором лотерей ви за кілька хвилин зробите пронумеровані квитки з емблемою та кольорами клубу: без Canva і без встановлення програм.",
        "passos": [
            ("Вирішіть це з правлінням", "На зборах правління, а для важливішого рішення — на загальних зборах членів, визначте причину (форма, поїздки, наступний сезон), призи, ціну квитка, скільки квитків друкувати і дату розіграшу — наприклад, на вечері з нагоди ювілею клубу чи в перерві щорічного турніру. Перед продажем дізнайтеся в місцевій владі (або регуляторі), чи потрібні для лотереї дозвіл або повідомлення."),
            ("Одягніть квиток у кольори клубу", "У галереї виберіть дизайн (Futebol, Retro…) і напишіть назву клубу, вид спорту, призи та дату. Додайте емблему як логотип (PNG або JPG) і виберіть для номерів офіційні кольори клубу, щоб квиток впізнавали з відстані. Якщо хочете щось своє, скористайтеся Редактором шаблонів."),
            ("Одна серія на команду, вікову групу чи продавця-члена", "У полі «Префікс або серії» напишіть, наприклад, A-, B-, C-: кожна команда, молодіжна вікова група чи продавець-член клубу отримає свої квитки (A-0001, B-0001…) і свої файли, тож видно, хто продав найбільше. У «Пропустити номери» зарезервуйте ті, що вже обіцяні спонсору, і дайте кожній серії колір."),
            ("Друк і вирізання", "Виберіть папір (зазвичай підходить A4) і мітки для обрізання: програма заповнює аркуш квитками. Надрукуйте й різіть по мітках; кольоровий папір допомагає розрізняти серії різних вікових груп. У квитків є корінець, тому номер зазначено двічі."),
            ("Облік продажів і розіграш у великий день", "Експортуйте список квитків (CSV) і контрольний аркуш продажів, щоб передати кожному тренеру, капітану команди чи продавцю-члену. Наприкінці сезону, на турнірі чи на щорічному гала відкрийте сторінку «Розіграш»: з публічним зерном (наприклад, результатом вечірнього матчу чи лотереї) будь-який член клубу зможе перевірити підсумок на телефоні."),
        ],
        "dicas": [
            "Дайте кожній команді чи віковій групі діапазон номерів і записуйте, хто взяв який блок квитків, щоб знати, з кого наприкінці спитати звіт.",
            "Продавайте на домашніх матчах, на тренуваннях і членам із сплаченими внесками: хто вже «свій», часто купує не задумуючись.",
            "Оголосіть результат у соцмережах і на дошці клубу з посиланням на розіграш, щоб кожен член міг його перевірити.",
        ],
        "fim": "Сервіс безкоштовний, без реєстрації й не зберігає ваших файлів. Можна починати вже зараз.",
    },
    "id": {
        "titulo": "Cara membuat undian untuk klub",
        "intro": "Undian membantu klub olahraga membayar perlengkapan, perjalanan tandang, atau musim depan, dengan menjual terutama kepada anggota klub sendiri dan keluarga atlet. Dengan Pembuat Undian Anda bisa membuat tiket bernomor berlogo dan berwarna klub dalam beberapa menit: tanpa Canva dan tanpa memasang program.",
        "passos": [
            ("Putuskan bersama pengurus", "Pada rapat pengurus, atau rapat anggota untuk keputusan yang lebih besar, sepakati alasannya (perlengkapan, perjalanan, musim depan), hadiah, harga tiket, jumlah tiket yang dicetak, dan tanggal pengundian — misalnya pada malam ulang tahun klub atau saat istirahat turnamen tahunan. Sebelum menjual, tanyakan ke pemerintah setempat (atau regulator) apakah undian memerlukan izin atau pemberitahuan."),
            ("Hiasi tiket dengan warna klub", "Di galeri pilih desain (Futebol, Retro…) dan tulis nama klub, cabang olahraga, hadiah, dan tanggal. Tambahkan lambang klub sebagai logo (PNG atau JPG) dan pilih warna resmi klub untuk nomor, agar tiket mudah dikenali dari jauh. Untuk desain sendiri, gunakan Editor templat."),
            ("Satu seri per tim, kelompok umur, atau anggota penjual", "Di «Awalan atau seri» tulis, misalnya, A-, B-, C-: setiap tim, kelompok umur junior, atau anggota penjual mendapat tiket (A-0001, B-0001…) dan berkasnya sendiri, sehingga terlihat siapa yang paling banyak menjual. Di «Lewati nomor» sisihkan nomor yang sudah dijanjikan ke sponsor, dan beri setiap seri warna."),
            ("Cetak dan gunting", "Pilih kertas (biasanya A4 cukup) dan tanda potong: program memenuhi lembar dengan tiket. Cetak lalu gunting mengikuti tanda; kertas berwarna membantu membedakan seri dari tiap kelompok umur. Tiket punya kupon, jadi nomornya muncul dua kali."),
            ("Pantau penjualan dan lakukan pengundian di hari besar", "Ekspor daftar tiket (CSV) dan lembar kontrol penjualan untuk diberikan kepada setiap pelatih, kapten tim, atau anggota penjual. Pada akhir musim, di turnamen, atau di gala tahunan, gunakan halaman «Pengundian»: dengan seed publik (misalnya skor pertandingan malam itu atau hasil lotere) setiap anggota dapat memastikan hasilnya lewat ponsel."),
        ],
        "dicas": [
            "Beri setiap tim atau kelompok umur rentang nomor dan catat siapa yang membawa tiap blok tiket, agar tahu kepada siapa meminta laporan di akhir.",
            "Jual di pertandingan kandang, saat latihan, dan kepada anggota yang iurannya lunas: yang sudah menjadi bagian klub biasanya membeli tanpa berpikir dua kali.",
            "Umumkan hasil di media sosial dan papan pengumuman klub beserta tautan pengundian agar setiap anggota bisa memeriksanya.",
        ],
        "fim": "Layanan ini gratis, tanpa pendaftaran dan tidak menyimpan berkas Anda. Anda bisa mulai sekarang.",
    },
    "vi": {
        "titulo": "Cách tổ chức bốc thăm cho câu lạc bộ",
        "intro": "Bốc thăm giúp một câu lạc bộ thể thao trả tiền trang phục, chuyến đi thi đấu xa hoặc chi phí mùa giải sau, chủ yếu bán cho chính các hội viên và gia đình vận động viên. Với Trình tạo vé số, bạn làm vé đánh số có huy hiệu và màu sắc của câu lạc bộ chỉ trong vài phút: không cần Canva, không cần cài phần mềm.",
        "passos": [
            ("Quyết định cùng ban chấp hành", "Trong một cuộc họp ban chấp hành, hoặc đại hội hội viên nếu là quyết định lớn hơn, hãy thống nhất lý do (trang phục, chuyến đi, mùa giải sau), giải thưởng, giá vé, số vé sẽ in và ngày bốc thăm — chẳng hạn vào bữa tối kỷ niệm của câu lạc bộ hoặc giờ nghỉ của giải đấu hằng năm. Trước khi bán, hãy hỏi chính quyền địa phương (hoặc cơ quan quản lý) xem cuộc bốc thăm có cần giấy phép hay thông báo không."),
            ("Khoác lên vé màu sắc của câu lạc bộ", "Trong thư viện, chọn một mẫu (Futebol, Retro…) rồi viết tên câu lạc bộ, môn thể thao, giải thưởng và ngày. Thêm huy hiệu làm logo (PNG hoặc JPG) và chọn màu chính thức của câu lạc bộ cho các số, để vé được nhận ra từ xa. Muốn mẫu riêng, hãy dùng Trình chỉnh sửa mẫu."),
            ("Mỗi đội, nhóm tuổi hoặc hội viên bán hàng một sê-ri", "Ở «Tiền tố hoặc sê-ri», gõ chẳng hạn A-, B-, C-: mỗi đội, nhóm tuổi trẻ hoặc hội viên bán hàng nhận vé (A-0001, B-0001…) và tệp riêng, nhờ đó biết ai bán nhiều nhất. Ở «Bỏ qua các số», giữ lại những số đã hứa cho nhà tài trợ, và có thể gán cho mỗi sê-ri một màu."),
            ("In và cắt", "Chọn giấy (thường A4 là đủ) và dấu cắt: chương trình xếp đầy tờ giấy bằng vé. In rồi cắt theo dấu; giấy màu giúp phân biệt các sê-ri của từng nhóm tuổi. Vé có cuống nên số xuất hiện hai lần."),
            ("Theo dõi doanh số và bốc thăm vào ngày trọng đại", "Xuất danh sách vé (CSV) và bảng kiểm soát doanh số để đưa cho từng huấn luyện viên, đội trưởng hoặc hội viên bán hàng. Vào cuối mùa giải, tại giải đấu hoặc buổi dạ hội hằng năm, dùng trang «Bốc thăm»: với hạt giống công khai (ví dụ tỷ số trận đấu đêm đó hoặc kết quả xổ số), hội viên nào cũng có thể kiểm chứng kết quả trên điện thoại."),
        ],
        "dicas": [
            "Giao cho mỗi đội hoặc nhóm tuổi một dải số và ghi lại ai nhận từng xấp vé, để biết cuối cùng cần hỏi ai về số tiền thu được.",
            "Bán tại các trận đấu trên sân nhà, buổi tập và cho những hội viên đã đóng hội phí: người đã là thành viên thường mua mà không cần nghĩ nhiều.",
            "Công bố kết quả trên mạng xã hội và bảng thông báo của câu lạc bộ, kèm liên kết bốc thăm, để hội viên nào cũng kiểm tra được.",
        ],
        "fim": "Dịch vụ miễn phí, không cần đăng ký và không lưu tệp của bạn. Bạn có thể bắt đầu ngay.",
    },
}

BOMBEIROS = {
    "ca": {
        "titulo": "Com fer una rifa per als bombers",
        "intro": "Als cossos de bombers voluntaris, la rifa és gairebé una institució: és la manera més directa de finançar el que el pressupost municipal no cobreix — un vehicle, un joc de mànegues, equip de protecció individual — i normalment la decideix la mateixa junta o la comandància del cos, sovint coincidint amb l'aniversari de la corporació. Amb el Generador de Rifes es fan les butlletes numerades, amb l'escut i els colors del cos, en pocs minuts: sense Canva ni programes per instal·lar.",
        "passos": [
            ("Decidiu amb la junta què falta", "Amb la junta o la comandància, decidiu a què es destinaran els diners aquesta vegada (el vehicle, les mànegues, l'EPI, la festa d'aniversari), els premis — sovint oferts pel comerç i les empreses de la zona que els bombers ja han ajudat —, el preu de la butlleta i la data del sorteig, preferiblement coincidint amb l'aniversari del cos o una altra data que ja conegui la comunitat. Abans de vendre, consulteu a l'ajuntament si la rifa necessita llicència o comunicació: les normes depenen del tipus de rifa."),
            ("Vestiu la butlleta amb els colors del cos", "A la galeria trieu el disseny Bombeiros (o Solidária) i escriviu el nom del cos, a què es destinen els diners i la data. Afegiu l'escut com a logotip (PNG o JPG) i trieu per als números els mateixos colors de l'uniforme o de l'escut — vermell i negre, o els colors propis del cos. Si preferiu alguna cosa a mida, feu servir l'Editor de plantilles."),
            ("Una sèrie per a cada bomber venedor", "A «Prefix o sèries» escriviu, per exemple, A-, B-, C-: cada bomber, equip de guàrdia o barri rep les seves butlletes (A-0001, B-0001…) i els seus fitxers, el que facilita saber qui ha venut més quan la venda és de porta en porta. A «Omet números» traieu els que queden reservats, per exemple per a la junta."),
            ("Imprimiu a temps per a la ronda per les cases", "Trieu el paper (l'A4 sol anar bé) i les marques de tall: el programa omple el full de butlletes tot sol. Imprimiu amb uns quants dies de marge abans que els bombers surtin al carrer, d'uniforme, a vendre de porta en porta; el paper de color ajuda a distingir les sèries. Les butlletes tenen taló, per això el número queda registrat dues vegades."),
            ("Sortegeu davant la comunitat i retreu comptes", "Exporteu la llista de butlletes (CSV) i el full de control de vendes perquè cada bomber tanqui comptes amb la tresoreria. Activeu el QR de verificació a cada butlleta — qui l'ha comprada pot confirmar que el seu número és genuí — i feu el sorteig a la pàgina «Sorteig», amb una llavor pública (per exemple, la loteria): qualsevol persona de la comunitat pot repetir el càlcul i comprovar el resultat, el que ajuda a mantenir la confiança de qui continua comprant any rere any."),
        ],
        "dicas": [
            "Lliureu els blocs de butlletes contra una llista i anoteu quin bomber s'endú cada bloc i quan retorna els diners.",
            "Escriviu a la butlleta el contacte del cos i el termini per recollir els premis, perquè qui guanyi no el perdi.",
            "Agraïu en públic, a les xarxes socials o a la festa d'aniversari, a qui ha ofert premis, i publiqueu el resultat amb l'enllaç del sorteig.",
        ],
        "fim": "El servei és gratuït, no cal registre i no guarda els vostres fitxers. Podeu començar ara mateix.",
    },
    "uk": {
        "titulo": "Як провести лотерею для пожежної команди",
        "intro": "У добровільних пожежних командах лотерея — майже традиція: це найпряміший спосіб профінансувати те, що не покриває місцевий бюджет, — машину, комплект шлангів, засоби індивідуального захисту, — і рішення про неї зазвичай приймає саме правління або командування команди, часто приурочуючи її до річниці дружини. З Генератором лотерей ви за кілька хвилин зробите пронумеровані квитки з емблемою та кольорами команди: без Canva і без встановлення програм.",
        "passos": [
            ("Вирішіть із правлінням, чого не вистачає", "З правлінням або командуванням домовтеся, на що цього разу підуть гроші (машина, шланги, засоби захисту, святкування річниці), про призи — їх часто дарують місцеві магазини та підприємства, яким команда вже допомагала, — про ціну квитка й дату розіграшу, бажано приурочивши її до річниці команди або іншої дати, уже відомої громаді. Перед продажем дізнайтеся в місцевої влади, чи потрібні дозвіл або повідомлення: правила залежать від виду лотереї."),
            ("Одягніть квиток у кольори команди", "У галереї виберіть дизайн Bombeiros (або Solidária) і впишіть назву команди, на що підуть гроші, та дату. Додайте емблему як логотип (PNG або JPG) і виберіть для номерів ті самі кольори, що на формі чи емблемі, — червоний і чорний або власні кольори команди. Якщо хочете щось своє, скористайтеся Редактором шаблонів."),
            ("Одна серія на кожного пожежного-продавця", "У полі «Префікс або серії» впишіть, наприклад, A-, B-, C-: кожен пожежний, дежурна зміна чи район отримує свої квитки (A-0001, B-0001…) і свої файли, тож під час продажу по будинках легко видно, хто продав найбільше. У «Пропустити номери» прибирайте зарезервовані номери, наприклад для правління."),
            ("Надрукуйте завчасно до обходу будинків", "Виберіть папір (зазвичай підходить A4) і мітки для обрізання: програма сама заповнює аркуш квитками. Друкуйте за кілька днів до того, як пожежні у формі вийдуть продавати по будинках; кольоровий папір допомагає розрізняти серії. Квитки мають корінець, тож номер записано двічі."),
            ("Розіграйте перед громадою і прозвітуйте", "Експортуйте список квитків (CSV) і контрольний аркуш продажів, щоб кожен пожежний міг розрахуватися з скарбником. Увімкніть перевірочний QR на кожному квитку — покупець зможе підтвердити, що його номер справжній, — і проведіть розіграш на сторінці «Розіграш» із публічним зерном (наприклад, результатом лотереї): будь-хто в громаді може повторити розрахунок і перевірити результат, що допомагає зберегти довіру тих, хто купує рік за роком."),
        ],
        "dicas": [
            "Видавайте блоки квитків під запис у списку й зазначайте, який пожежний бере який блок і коли повертає гроші.",
            "Напишіть на квитку контакт команди та строк отримання призів, щоб переможці його не прогавили.",
            "Публічно подякуйте, у соцмережах або на святкуванні річниці, тим, хто дав призи, і опублікуйте результат із посиланням на розіграш.",
        ],
        "fim": "Сервіс безкоштовний, без реєстрації, і не зберігає ваших файлів. Можна починати вже зараз.",
    },
    "id": {
        "titulo": "Cara membuat undian untuk pemadam kebakaran",
        "intro": "Di regu pemadam kebakaran sukarela, undian hampir menjadi tradisi: ini adalah cara paling langsung bagi regu untuk membiayai apa yang tidak ditanggung anggaran daerah — kendaraan, satu set selang, perlengkapan pelindung diri — dan biasanya diputuskan oleh pengurus atau komando regu sendiri, sering bertepatan dengan hari jadi regu. Dengan Pembuat Undian, Anda membuat tiket bernomor dengan lambang dan warna regu dalam beberapa menit: tanpa Canva dan tanpa memasang program.",
        "passos": [
            ("Putuskan bersama pengurus apa yang kurang", "Bersama pengurus atau komando, sepakati untuk apa uangnya kali ini (kendaraan, selang, perlengkapan pelindung, pesta hari jadi), hadiah — sering diberikan toko dan usaha setempat yang pernah dibantu regu —, harga tiket, dan tanggal pengundian, sebaiknya bertepatan dengan hari jadi regu atau tanggal lain yang sudah dikenal masyarakat. Sebelum menjual, tanyakan ke pemerintah setempat apakah undian memerlukan izin atau pemberitahuan: aturannya bergantung pada jenis undian."),
            ("Beri tiket warna khas regu", "Di galeri pilih desain Bombeiros (atau Solidária) dan tulis nama regu, untuk apa uangnya, dan tanggalnya. Tambahkan lambang sebagai logo (PNG atau JPG) dan pilih warna nomor sama seperti seragam atau lambang — merah dan hitam, atau warna khas regu sendiri. Untuk desain sendiri, gunakan Editor templat."),
            ("Satu seri untuk setiap anggota yang menjual", "Di «Awalan atau seri» tulis, misalnya, A-, B-, C-: setiap anggota, tim jaga, atau wilayah mendapat tiketnya sendiri (A-0001, B-0001…) dan berkasnya sendiri, sehingga mudah melihat siapa yang paling banyak menjual saat berjualan dari rumah ke rumah. Di «Lewati nomor» keluarkan nomor yang dicadangkan, misalnya untuk pengurus."),
            ("Cetak tepat waktu sebelum keliling dari rumah ke rumah", "Pilih kertas (biasanya A4 cukup) dan tanda potong: program mengisi lembar dengan tiket sendiri. Cetak beberapa hari sebelum anggota regu berseragam turun berjualan dari rumah ke rumah; kertas berwarna membantu membedakan seri. Tiket memiliki kupon, sehingga nomornya tercatat dua kali."),
            ("Lakukan pengundian di depan warga dan laporkan hasilnya", "Ekspor daftar tiket (CSV) dan lembar kontrol penjualan agar setiap anggota bisa menyelesaikan hitungan dengan bendahara. Aktifkan QR verifikasi pada setiap tiket — agar pembeli bisa memastikan nomornya asli — dan lakukan pengundian di halaman «Pengundian», dengan benih publik (misalnya hasil lotere): siapa pun di masyarakat dapat mengulang perhitungan dan memeriksa hasilnya, yang membantu menjaga kepercayaan mereka yang terus membeli setiap tahun."),
        ],
        "dicas": [
            "Serahkan blok tiket dengan mencatatnya di daftar dan catat anggota mana yang membawa blok mana serta kapan mengembalikan uangnya.",
            "Tulis di tiket kontak regu dan batas waktu pengambilan hadiah, agar pemenang tidak melewatkannya.",
            "Ucapkan terima kasih secara terbuka, di media sosial atau pada pesta hari jadi, kepada penyumbang hadiah, dan umumkan hasil beserta tautan pengundian.",
        ],
        "fim": "Layanan ini gratis, tanpa pendaftaran, dan tidak menyimpan berkas Anda. Anda bisa mulai sekarang.",
    },
    "vi": {
        "titulo": "Cách tổ chức bốc thăm cho đội cứu hỏa",
        "intro": "Ở các đội cứu hỏa tình nguyện, bốc thăm gần như là một truyền thống: đây là cách trực tiếp nhất để đội chi trả cho những gì ngân sách địa phương không đủ — một chiếc xe, một bộ vòi, thiết bị bảo hộ cá nhân — và thường do chính ban lãnh đạo hoặc chỉ huy của đội quyết định, nhiều khi trùng với ngày kỷ niệm thành lập đội. Với Trình tạo vé số, bạn làm vé đánh số có huy hiệu và màu sắc của đội trong vài phút: không cần Canva, không cần cài phần mềm.",
        "passos": [
            ("Quyết định cùng ban lãnh đạo xem còn thiếu gì", "Cùng ban lãnh đạo hoặc chỉ huy, thống nhất lần này tiền dùng để làm gì (xe, vòi, thiết bị bảo hộ, tiệc kỷ niệm), giải thưởng — thường do các cửa hàng và doanh nghiệp trong vùng mà đội đã từng giúp tặng —, giá vé và ngày bốc thăm, tốt nhất là trùng với ngày kỷ niệm của đội hoặc một ngày khác mà cộng đồng đã biết. Trước khi bán, hãy hỏi chính quyền địa phương xem cuộc bốc thăm có cần giấy phép hay thông báo không: quy định tùy theo loại hình."),
            ("Khoác cho vé màu sắc của đội", "Trong thư viện, chọn mẫu Bombeiros (hoặc Solidária) rồi viết tên đội, tiền dùng để làm gì và ngày tháng. Thêm huy hiệu làm logo (PNG hoặc JPG) và chọn cho các số cùng màu với đồng phục hoặc huy hiệu — đỏ và đen, hoặc màu riêng của đội. Muốn mẫu riêng, hãy dùng Trình chỉnh sửa mẫu."),
            ("Mỗi thành viên bán hàng một sê-ri", "Ở «Tiền tố hoặc sê-ri», gõ chẳng hạn A-, B-, C-: mỗi thành viên, ca trực hoặc khu vực nhận vé riêng (A-0001, B-0001…) và tệp riêng, nhờ đó khi bán từng nhà dễ thấy ai bán được nhiều nhất. Ở «Bỏ qua các số», loại ra những số để dành, chẳng hạn cho ban lãnh đạo."),
            ("In đúng lúc trước đợt đi từng nhà", "Chọn giấy (thường A4 là đủ) và dấu cắt: chương trình tự lấp đầy tờ giấy bằng vé. In trước vài ngày khi các thành viên mặc đồng phục đi bán từng nhà; giấy màu giúp phân biệt các sê-ri. Vé có cuống nên số được ghi hai lần."),
            ("Bốc thăm trước cộng đồng và báo cáo lại", "Xuất danh sách vé (CSV) và phiếu kiểm soát bán vé để mỗi thành viên quyết toán với thủ quỹ. Kích hoạt mã QR xác minh trên từng vé — để người mua có thể xác nhận số của họ là thật — và tổ chức bốc thăm ở trang «Bốc thăm», với hạt giống công khai (ví dụ kết quả xổ số): bất kỳ ai trong cộng đồng đều có thể làm lại phép tính và kiểm tra kết quả, điều này giúp giữ niềm tin của những người năm nào cũng mua."),
        ],
        "dicas": [
            "Chỉ giao xấp vé khi đã ghi vào danh sách, và ghi lại thành viên nào nhận xấp nào, khi nào nộp lại tiền.",
            "Viết lên vé thông tin liên lạc của đội và hạn nhận giải thưởng, để người trúng không bỏ lỡ.",
            "Công khai cảm ơn, trên mạng xã hội hoặc tại tiệc kỷ niệm, những người đã tặng giải thưởng, và công bố kết quả kèm liên kết bốc thăm.",
        ],
        "fim": "Dịch vụ miễn phí, không cần đăng ký, và không lưu tệp của bạn. Bạn có thể bắt đầu ngay.",
    },
}

FESTAS = {
    "ca": {
        "titulo": "Com fer una rifa per a la festa del barri",
        "intro": "Darrere una festa de barri gairebé mai hi ha una associació formal: ho organitza tot un comitè de veïns, o només un grapat de veïns que s'han ofert aquest any. Sigui la festa d'estiu, el cap d'any o la festa del patró, la rifa ajuda a pagar les despeses i anima la nit: amb el Generador de Rifes feu butlletes numerades en pocs minuts, sense Canva ni programes per instal·lar.",
        "passos": [
            ("Decidiu-ho entre veïns, amb un responsable definit", "Reuniu els organitzadors — el comitè de veïns, o només els veïns que s'han ofert aquest any — i acordeu els premis (sovint regals dels comerciants de la zona), el preu de la butlleta, quantes se n'imprimiran i l'hora del sorteig durant la festa. Com que normalment no hi ha una associació amb personalitat jurídica al darrere, decidiu ja qui es queda els diners i els premis fins al sorteig, i digueu aquest nom a tothom. Abans de vendre, consulteu a l'ajuntament (o a l'entitat competent) si la rifa necessita llicència o comunicació."),
            ("Dissenyeu la butlleta de la festa", "A la galeria trieu un disseny (Arraial, Santos Populares…) i escriviu el nom de la festa, el lloc i la data — sigui la festa d'estiu, el cap d'any o la del sant patró. Si voleu alguna cosa a mida, feu servir l'Editor de plantilles i afegiu textos, línies i rectangles: no cal escut ni logotip, només el nom que tothom al carrer ja coneix."),
            ("Una sèrie per carrer, per dia o per veí venedor", "A «Prefix o sèries» escriviu, per exemple, A-, B-, C- (un carrer, un dia de festa o un veí que ven): cada sèrie té les seves butlletes (A-0001, B-0001…) i els seus fitxers, i així se sap què ha venut cadascú. Doneu un color a cada sèrie, perquè els veïns distingeixin els blocs d'una ullada."),
            ("Imprimiu, retalleu i repartiu pel carrer", "Trieu el paper (l'A4 sol anar bé) i les marques de tall: el programa omple el full de butlletes. Retalleu per les marques i lliureu un bloc a cada veí que ven; el paper de color ajuda a veure de seguida de quina sèrie és cada bloc. Les butlletes tenen taló, per això el número apareix dues vegades."),
            ("Controleu els diners i sortegeu davant de tothom", "Exporteu la llista de butlletes (CSV) i el full de control de vendes perquè cada veí torni els diners i els talons sense vendre abans de la festa. A l'hora acordada feu servir la pàgina «Sorteig»: amb una llavor pública (per exemple, la loteria o un número del diari del dia) qualsevol veí present pot comprovar el resultat des del mòbil, sense haver de confiar només en la paraula de qui ho ha organitzat."),
        ],
        "dicas": [
            "Imprimiu més butlletes de les que penseu vendre: en una festa de barri, les vendes solen dispararse en les últimes hores, de porta en porta.",
            "Escriviu-ho al cartell, i digueu-ho al grup de veïns a les xarxes socials: qui és el responsable dels diners i dels premis fins al sorteig.",
            "Guardeu els talons en una caixa fins al sorteig i comproveu el número premiat amb el taló a la mà, davant de qui hi sigui present.",
        ],
        "fim": "El servei és gratuït, no cal registre i no guarda els vostres fitxers. Podeu començar ara mateix.",
    },
    "uk": {
        "titulo": "Як провести лотерею на святі району",
        "intro": "За святом району майже ніколи не стоїть офіційне об'єднання: усе організовує комітет мешканців, або просто кілька сусідів, які зголосилися цього року. Чи це літнє свято, новорічна зустріч чи день покровителя, лотерея допомагає покрити витрати й оживляє вечір: з Генератором лотерей ви за кілька хвилин зробите пронумеровані квитки, без Canva і без встановлення програм.",
        "passos": [
            ("Вирішіть це разом із сусідами, з чітко визначеним відповідальним", "Зберіть організаторів — комітет мешканців, або просто сусідів, які зголосилися цього року, — і домовтеся про призи (часто подарунки від місцевих торговців), ціну квитка, скільки квитків друкувати і час розіграшу під час свята. Оскільки зазвичай позаду немає об'єднання з юридичною особою, вирішіть уже зараз, хто зберігатиме гроші та призи до розіграшу, і скажіть це ім'я всім. Перед продажем дізнайтеся в місцевій владі (або регуляторі), чи потрібні для лотереї дозвіл або повідомлення."),
            ("Створіть квиток свята", "У галереї виберіть дизайн (Arraial, Santos Populares…) і напишіть назву свята, місце й дату — чи це літнє свято, новорічна зустріч чи день покровителя. Якщо хочете щось своє, скористайтеся Редактором шаблонів і додайте тексти, лінії та прямокутники: емблема чи логотип не потрібні, досить назви, яку вже знають усі на вулиці."),
            ("Одна серія на вулицю, день чи сусіда-продавця", "У полі «Префікс або серії» напишіть, наприклад, A-, B-, C- (одна вулиця, один день свята чи один сусід, що продає): у кожної серії свої квитки (A-0001, B-0001…) і свої файли, тож видно, що продав кожен. Дайте кожній серії колір, щоб сусіди з одного погляду розрізняли пачки."),
            ("Надрукуйте, виріжте і роздайте по вулиці", "Виберіть папір (зазвичай підходить A4) і мітки для обрізання: програма заповнює аркуш квитками. Різіть по мітках і дайте пачку кожному сусіду-продавцю; кольоровий папір одразу показує, до якої серії належить пачка. У квитків є корінець, тому номер зазначено двічі."),
            ("Стежте за грошима і проведіть розіграш перед усіма", "Експортуйте список квитків (CSV) і контрольний аркуш продажів, щоб кожен сусід повернув гроші та непродані корінці до свята. У призначений час відкрийте сторінку «Розіграш»: з публічним зерном (наприклад, результатом лотереї або числом з газети того дня) будь-який присутній сусід зможе перевірити підсумок на телефоні, не довіряючи лише слову організатора."),
        ],
        "dicas": [
            "Надрукуйте більше квитків, ніж розраховуєте продати: на святі району продажі зазвичай набирають обертів в останні години, від дверей до дверей.",
            "Напишіть це на афіші й скажіть у сусідській групі в соцмережах: хто відповідає за гроші та призи до розіграшу.",
            "Зберігайте корінці в коробці до розіграшу й перевіряйте виграшний номер із корінцем у руках, перед присутніми.",
        ],
        "fim": "Сервіс безкоштовний, без реєстрації й не зберігає ваших файлів. Можна починати вже зараз.",
    },
    "id": {
        "titulo": "Cara membuat undian untuk pesta warga",
        "intro": "Di balik pesta warga hampir tidak pernah ada organisasi resmi: semuanya diatur oleh panitia warga, atau hanya segelintir tetangga yang maju tahun ini. Baik itu pesta musim panas, malam tahun baru, atau perayaan santo pelindung, undian membantu menutup biaya dan meramaikan malam: dengan Pembuat Undian Anda bisa membuat tiket bernomor dalam beberapa menit, tanpa Canva dan tanpa memasang program.",
        "passos": [
            ("Putuskan bersama warga, dengan penanggung jawab yang jelas", "Kumpulkan para penyelenggara — panitia warga, atau hanya tetangga yang mengajukan diri tahun ini — dan sepakati hadiah (sering berupa hadiah dari pedagang setempat), harga tiket, jumlah tiket yang dicetak, dan jam pengundian selama acara. Karena biasanya tidak ada organisasi berbadan hukum di baliknya, tentukan sekarang siapa yang menyimpan uang dan hadiah sampai pengundian, dan beri tahu nama itu kepada semua orang. Sebelum menjual, tanyakan ke pemerintah setempat (atau regulator) apakah undian memerlukan izin atau pemberitahuan."),
            ("Rancang tiket pesta", "Di galeri pilih desain (Arraial, Santos Populares…) dan tulis nama acara, tempat, dan tanggal — baik itu pesta musim panas, malam tahun baru, atau perayaan santo pelindung. Untuk desain sendiri, gunakan Editor templat dan tambahkan teks, garis, dan persegi panjang: Anda tidak perlu lambang atau logo, cukup nama yang sudah dikenal semua orang di jalan itu."),
            ("Satu seri per jalan, hari, atau tetangga penjual", "Di «Awalan atau seri» tulis, misalnya, A-, B-, C- (satu jalan, satu hari acara, atau satu tetangga yang berjualan): setiap seri punya tiket (A-0001, B-0001…) dan berkasnya sendiri, sehingga terlihat apa yang dijual masing-masing. Beri setiap seri warna, agar tetangga bisa membedakan kelompok tiket sekilas."),
            ("Cetak, gunting, dan bagikan di sepanjang jalan", "Pilih kertas (biasanya A4 cukup) dan tanda potong: program memenuhi lembar dengan tiket. Gunting mengikuti tanda dan beri satu kelompok tiket kepada setiap tetangga yang berjualan; kertas berwarna langsung menunjukkan seri mana kelompok itu. Tiket punya kupon, jadi nomornya muncul dua kali."),
            ("Pantau uangnya dan lakukan pengundian di depan semua orang", "Ekspor daftar tiket (CSV) dan lembar kontrol penjualan agar setiap tetangga mengembalikan uang dan kupon yang tidak terjual sebelum acara. Pada jam yang disepakati, gunakan halaman «Pengundian»: dengan seed publik (misalnya hasil lotere atau nomor dari koran hari itu) siapa pun tetangga yang hadir dapat memastikan hasilnya lewat ponsel, tanpa harus percaya hanya pada kata-kata penyelenggara."),
        ],
        "dicas": [
            "Cetak lebih banyak tiket daripada perkiraan penjualan: di pesta warga, penjualan biasanya meningkat pada jam-jam terakhir, dari pintu ke pintu.",
            "Tulis di poster, dan sampaikan di grup media sosial warga, siapa yang bertanggung jawab atas uang dan hadiah sampai pengundian.",
            "Simpan kupon dalam kotak sampai pengundian dan periksa nomor pemenang dengan kupon di tangan, di depan yang hadir.",
        ],
        "fim": "Layanan ini gratis, tanpa pendaftaran dan tidak menyimpan berkas Anda. Anda bisa mulai sekarang.",
    },
    "vi": {
        "titulo": "Cách tổ chức bốc thăm cho lễ hội khu phố",
        "intro": "Đằng sau một lễ hội khu phố hầu như không bao giờ có một hội đoàn chính thức: mọi việc do một ban đại diện cư dân, hoặc chỉ vài người hàng xóm tự nguyện năm nay, đứng ra lo. Dù là lễ hội mùa hè, đêm giao thừa hay lễ thánh bảo trợ, bốc thăm giúp trang trải chi phí và làm buổi tối thêm vui: với Trình tạo vé số, bạn làm vé đánh số chỉ trong vài phút, không cần Canva, không cần cài phần mềm.",
        "passos": [
            ("Quyết định cùng nhau, với người chịu trách nhiệm rõ ràng", "Tập hợp những người tổ chức — ban đại diện cư dân, hoặc chỉ những người hàng xóm tự nguyện năm nay — và thống nhất giải thưởng (thường là quà của các tiểu thương trong vùng), giá vé, số vé sẽ in và giờ bốc thăm trong lúc diễn ra lễ hội. Vì thường không có hội đoàn với tư cách pháp nhân đứng sau, hãy quyết định ngay ai sẽ giữ tiền và giải thưởng cho đến lúc bốc thăm, và nói tên người đó cho mọi người biết. Trước khi bán, hãy hỏi chính quyền địa phương (hoặc cơ quan quản lý) xem cuộc bốc thăm có cần giấy phép hay thông báo không."),
            ("Thiết kế vé của lễ hội", "Trong thư viện, chọn một mẫu (Arraial, Santos Populares…) rồi viết tên lễ hội, địa điểm và ngày — dù là lễ hội mùa hè, đêm giao thừa hay lễ thánh bảo trợ. Muốn mẫu riêng, hãy dùng Trình chỉnh sửa mẫu và thêm văn bản, đường kẻ, hình chữ nhật: không cần huy hiệu hay logo, chỉ cần cái tên mà mọi người trên phố đã biết."),
            ("Mỗi con phố, mỗi ngày hoặc mỗi người hàng xóm bán hàng một sê-ri", "Ở «Tiền tố hoặc sê-ri», gõ chẳng hạn A-, B-, C- (một con phố, một ngày lễ hội, hoặc một người hàng xóm bán hàng): mỗi sê-ri có vé riêng (A-0001, B-0001…) và tệp riêng, nhờ đó biết mỗi người bán được gì. Hãy gán cho mỗi sê-ri một màu, để hàng xóm phân biệt các xấp vé chỉ bằng một cái nhìn."),
            ("In, cắt và phát dọc theo con phố", "Chọn giấy (thường A4 là đủ) và dấu cắt: chương trình xếp đầy tờ giấy bằng vé. Cắt theo dấu và đưa một xấp cho mỗi người hàng xóm bán hàng; giấy màu cho biết ngay xấp đó thuộc sê-ri nào. Vé có cuống nên số xuất hiện hai lần."),
            ("Theo dõi tiền và bốc thăm trước mặt mọi người", "Xuất danh sách vé (CSV) và bảng kiểm soát doanh số để mỗi người hàng xóm trả lại tiền và các cuống chưa bán trước lễ hội. Vào giờ đã hẹn, dùng trang «Bốc thăm»: với hạt giống công khai (ví dụ kết quả xổ số hoặc một số từ tờ báo hôm đó), bất kỳ người hàng xóm nào có mặt cũng có thể kiểm chứng kết quả trên điện thoại, mà không phải chỉ tin vào lời của người tổ chức."),
        ],
        "dicas": [
            "In nhiều vé hơn dự kiến bán được: ở lễ hội khu phố, doanh số thường tăng vào những giờ cuối, khi đi gõ cửa từng nhà.",
            "Viết lên áp phích, và nói trong nhóm mạng xã hội của khu phố, ai là người chịu trách nhiệm về tiền và giải thưởng cho đến lúc bốc thăm.",
            "Giữ các cuống vé trong một chiếc hộp cho đến lúc bốc thăm và đối chiếu số trúng thưởng với cuống vé trên tay, trước mặt những người có mặt.",
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
