"""Os textos de SEO das línguas de um ficheiro só (catalão, ucraniano, indonésio, vietnamita): juntam-se a `seo_textos.CHAVES` ao importar (ver docs/LINGUAS.md).

As mesmas chaves e os mesmos {parâmetros} que as outras línguas; `tests/test_web_seo_linguas.py` verifica-o e as larguras (título até 66, descrição entre 50 e 158).
Sem revisão por falantes nativos. O nome da app vem de `app_nome` de cada língua.
"""
NOVAS = ("ca", "uk", "id", "vi")

LOCALE_OG = {"ca": "ca_ES", "uk": "uk_UA", "id": "id_ID", "vi": "vi_VN"}

CHAVES: dict[str, dict[str, str]] = {
    "t_inicio": {
        "ca": "{app}: rifes numerades en PDF des de Canva",
        "uk": "{app}: пронумеровані квитки в PDF із Canva",
        "id": "{app}: tiket undian bernomor PDF dari Canva",
        "vi": "{app}: vé số đánh số dạng PDF từ Canva",
    },
    "d_inicio": {
        "ca": "Rifes numerades en PDF a partir d'una plantilla de Canva: trieu els números, mireu la previsualització i baixeu-les. Gratis i sense registre.",
        "uk": "Пронумеровані лотерейні квитки в PDF із шаблону Canva: виберіть номери, перегляньте та завантажте. Безкоштовно й без реєстрації.",
        "id": "Tiket undian bernomor dalam PDF dari templat Canva: pilih nomor, lihat pratinjau, lalu unduh. Gratis dan tanpa pendaftaran.",
        "vi": "Vé số đánh số dạng PDF từ mẫu Canva: chọn số, xem trước rồi tải về. Miễn phí, không cần đăng ký.",
    },
    "d_tutorial": {
        "ca": "Pas a pas: prepareu la plantilla a Canva, creeu el fitxer de xifres, trieu els números i genereu els PDF de la rifa.",
        "uk": "Крок за кроком: підготуйте шаблон у Canva, створіть файл із цифрами, виберіть номери й створіть PDF лотереї.",
        "id": "Langkah demi langkah: siapkan templat di Canva, buat berkas angka, pilih nomor, lalu buat PDF undian.",
        "vi": "Từng bước: chuẩn bị mẫu trong Canva, tạo tệp chữ số, chọn các số rồi tạo tệp PDF vé số.",
    },
    "d_video": {
        "ca": "Mireu com generar butlletes de rifa numerades en PDF, de la plantilla de Canva fins al PDF llest per imprimir.",
        "uk": "Дивіться, як створити пронумеровані лотерейні квитки в PDF: від шаблону Canva до готового до друку PDF.",
        "id": "Tonton cara membuat tiket undian bernomor dalam PDF, dari templat Canva sampai PDF siap cetak.",
        "vi": "Xem cách tạo vé số đánh số dạng PDF, từ mẫu Canva đến tệp PDF sẵn sàng để in.",
    },
    "d_sobre": {
        "ca": "Què és el Generador de Rifes, com funciona i què fa servir. El mateix motor que l'aplicació per a Windows, ara al navegador.",
        "uk": "Що таке Генератор лотерей, як він працює й що використовує. Той самий рушій, що й застосунок для Windows, тепер у браузері.",
        "id": "Apa itu Pembuat Undian, cara kerjanya dan apa yang dipakainya. Mesin yang sama dengan aplikasi Windows, kini di browser.",
        "vi": "Trình tạo vé số là gì, hoạt động ra sao và dùng những gì. Cùng một bộ máy với ứng dụng Windows, nay chạy ngay trên trình duyệt.",
    },
    "d_sorteio": {
        "ca": "Sorteja números guanyadors de manera que qualsevol persona pugui repetir el sorteig i confirmar el resultat, amb una llavor pública.",
        "uk": "Розіграйте виграшні номери так, щоб будь-хто міг повторити розіграш і підтвердити результат за допомогою публічного зерна.",
        "id": "Undi nomor pemenang agar siapa pun dapat mengulang pengundian dan memastikan hasilnya, dengan benih publik.",
        "vi": "Bốc các số trúng thưởng để bất kỳ ai cũng có thể lặp lại lần bốc và xác nhận kết quả, dùng hạt giống công khai.",
    },
    "d_editor": {
        "ca": "Dissenyeu la butlleta de rifa sense Canva: textos, rectangles, línies i el número 0001, i feu-la servir de plantilla per generar butlletes numerades.",
        "uk": "Створіть лотерейний квиток без Canva: тексти, прямокутники, лінії та номер 0001, і використайте його як шаблон для пронумерованих квитків.",
        "id": "Rancang tiket undian tanpa Canva: teks, persegi panjang, garis dan nomor 0001, lalu pakai sebagai templat untuk membuat tiket bernomor.",
        "vi": "Thiết kế vé số không cần Canva: văn bản, hình chữ nhật, đường kẻ và số 0001, rồi dùng làm mẫu để tạo vé đánh số.",
    },
    "d_guia_escolas": {
        "ca": "Com fer una rifa per a l'escola: dissenyar les butlletes, una sèrie per classe, imprimir i retallar, controlar vendes i fer un sorteig verificable.",
        "uk": "Як провести лотерею для школи: створити квитки, одна серія на клас, друк і різання, облік продажів і перевірюваний розіграш для родин.",
        "id": "Cara menyelenggarakan undian sekolah: rancang tiket, satu seri per kelas, cetak dan gunting, pantau penjualan, lalu adakan pengundian yang dapat diverifikasi.",
        "vi": "Cách tổ chức bốc thăm cho trường học: thiết kế vé, mỗi lớp một sê-ri, in và cắt, theo dõi doanh số và bốc thăm để các gia đình kiểm chứng.",
    },
    "d_guia_associacoes": {
        "ca": "Com fer una rifa per a l'associació: butlletes amb la vostra imatge i taló, una sèrie per venedor, marques de tall, control de vendes i sorteig verificable.",
        "uk": "Як провести лотерею для об'єднання: квитки у вашому стилі з корінцем, одна серія на продавця, мітки для обрізання, облік продажів і перевірюваний розіграш.",
        "id": "Cara membuat undian untuk organisasi: tiket dengan kupon, satu seri per penjual, tanda potong, kontrol penjualan dan pengundian yang terverifikasi.",
        "vi": "Cách tổ chức bốc thăm cho hội nhóm: vé mang phong cách của bạn có cuống, mỗi người bán một sê-ri, dấu cắt, kiểm soát doanh số và bốc thăm kiểm chứng được.",
    },
    "d_termos": {
        "ca": "Les normes d'ús del Generador de Rifes: què fa el servei, què no fa i qui és responsable de la rifa.",
        "uk": "Правила користування Генератором лотерей: що робить сервіс, чого не робить і хто відповідає за лотерею.",
        "id": "Aturan penggunaan Pembuat Undian: apa yang dilakukan layanan, apa yang tidak dilakukannya dan siapa yang bertanggung jawab atas undian.",
        "vi": "Quy tắc sử dụng Trình tạo vé số: dịch vụ làm gì, không làm gì và ai chịu trách nhiệm về cuộc bốc thăm.",
    },
    "d_privacidade": {
        "ca": "Quines dades tracta el Generador de Rifes (gairebé cap), durant quant de temps i quins drets teniu segons el RGPD.",
        "uk": "Які дані обробляє Генератор лотерей (майже жодних), як довго та які права ви маєте відповідно до GDPR.",
        "id": "Data apa yang diproses Pembuat Undian (hampir tidak ada), berapa lama dan hak apa yang Anda miliki menurut GDPR.",
        "vi": "Trình tạo vé số xử lý những dữ liệu nào (gần như không có), trong bao lâu và bạn có những quyền gì theo GDPR.",
    },
    "d_contacto": {
        "ca": "Com contactar amb qui gestiona el Generador de Rifes: dubtes, errors i suggeriments sobre les vostres butlletes numerades.",
        "uk": "Як зв'язатися з тим, хто веде Генератор лотерей: питання, помилки та пропозиції щодо ваших пронумерованих квитків.",
        "id": "Cara menghubungi pengelola Pembuat Undian: pertanyaan, kesalahan dan saran tentang tiket bernomor Anda.",
        "vi": "Cách liên hệ với người vận hành Trình tạo vé số: câu hỏi, lỗi và góp ý về vé đánh số của bạn.",
    },
    "d_changelog": {
        "ca": "Tot el que ha canviat al Generador de Rifes, versió a versió: novetats, millores i correccions.",
        "uk": "Усе, що змінилося в Генераторі лотерей, версія за версією: нові функції, покращення й виправлення.",
        "id": "Semua yang berubah di Pembuat Undian, versi demi versi: fitur baru, peningkatan dan perbaikan.",
        "vi": "Mọi thay đổi của Trình tạo vé số, từng phiên bản: tính năng mới, cải tiến và sửa lỗi.",
    },
    "intro": {
        "ca": "Creeu rifes numerades en PDF a partir d'una plantilla de Canva: trieu els números, mireu la previsualització i baixeu PDF llestos per imprimir. És gratuït, no cal registre i funciona en 22 llengües.",
        "uk": "Створюйте пронумеровані лотерейні квитки в PDF із шаблону Canva: виберіть номери, перегляньте та завантажте PDF, готові до друку. Безкоштовно, без реєстрації, 22 мовами.",
        "id": "Buat tiket undian bernomor dalam PDF dari templat Canva: pilih nomor, lihat pratinjau, lalu unduh PDF siap cetak. Gratis, tanpa pendaftaran dan tersedia dalam 22 bahasa.",
        "vi": "Tạo vé số đánh số dạng PDF từ mẫu Canva: chọn số, xem trước và tải về tệp PDF sẵn sàng để in. Miễn phí, không cần đăng ký và có 22 ngôn ngữ.",
    },
    "como": {
        "ca": "Com funciona",
        "uk": "Як це працює",
        "id": "Cara kerjanya",
        "vi": "Cách hoạt động",
    },
    "ficheiros": {
        "ca": "La plantilla i les xifres només es fan servir per generar les butlletes i s'esborren del servidor passats {min} minuts d'inactivitat, o quan premeu «Neteja-ho tot».",
        "uk": "Шаблон і цифри використовуються лише для створення квитків і видаляються із сервера після {min} хв бездіяльності або коли ви натискаєте «Очистити все».",
        "id": "Templat dan angka hanya dipakai untuk membuat tiket Anda dan dihapus dari server setelah {min} menit tanpa aktivitas, atau saat Anda menekan “Bersihkan semua”.",
        "vi": "Mẫu và các chữ số chỉ được dùng để tạo vé của bạn và bị xóa khỏi máy chủ sau {min} phút không hoạt động, hoặc khi bạn bấm “Xóa tất cả”.",
    },
    "voltar": {
        "ca": "Torna a {app}",
        "uk": "Назад до {app}",
        "id": "Kembali ke {app}",
        "vi": "Quay lại {app}",
    },
    "og_alt": {
        "ca": "{app}: dues butlletes numerades, una de groga amb el 7 de la sort",
        "uk": "{app}: два пронумеровані квитки, жовтий із щасливою сімкою",
        "id": "{app}: dua tiket bernomor, satu berwarna kuning dengan angka 7 keberuntungan",
        "vi": "{app}: hai vé đánh số, một vé màu vàng có số 7 may mắn",
    },
}
